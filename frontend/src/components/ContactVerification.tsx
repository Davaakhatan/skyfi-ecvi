import { useState, useEffect } from 'react'
import { Mail, Phone, User, CheckCircle, XCircle, AlertCircle, Clock, Loader2 } from 'lucide-react'
import api from '../services/api'
import { format } from 'date-fns'
import type { ContactVerificationResult } from '../types/api'
import clsx from 'clsx'

interface ContactVerificationProps {
  companyId: string
  verificationResultId?: string | null
}

export default function ContactVerification({
  companyId,
  verificationResultId,
}: ContactVerificationProps) {
  const [verifications, setVerifications] = useState<ContactVerificationResult[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchVerifications()
  }, [companyId, verificationResultId])

  const fetchVerifications = async () => {
    setLoading(true)
    try {
      const params: any = {}
      if (verificationResultId) {
        params.verification_result_id = verificationResultId
      }
      const response = await api.get<ContactVerificationResult[]>(
        `/company/${companyId}/contact/verifications`,
        { params }
      )
      setVerifications(response.data || [])
    } catch (error: any) {
      // Handle errors gracefully - 404 means no verifications exist yet
      if (error.response?.status !== 404) {
        console.error('Failed to fetch contact verifications:', error)
      }
      setVerifications([])
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'VERIFIED':
        return CheckCircle
      case 'FAILED':
        return XCircle
      case 'PARTIAL':
        return AlertCircle
      default:
        return Clock
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'VERIFIED':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'FAILED':
        return 'text-red-600 bg-red-50 border-red-200'
      case 'PARTIAL':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getContactIcon = (type: string) => {
    switch (type) {
      case 'EMAIL':
        return Mail
      case 'PHONE':
        return Phone
      case 'NAME':
        return User
      default:
        return User
    }
  }

  const formatConfidence = (score: number | null) => {
    if (score === null) return 'N/A'
    return `${(score * 100).toFixed(0)}%`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
      </div>
    )
  }

  if (verifications.length === 0) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-sm text-gray-500">No contact verification data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {verifications.map((verification) => {
        const StatusIcon = getStatusIcon(verification.status)
        const ContactIcon = getContactIcon(verification.contact_type)
        const statusColor = getStatusColor(verification.status)

        return (
          <div
            key={verification.id}
            className={clsx('p-5 rounded-lg border', statusColor)}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                  <ContactIcon className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-sm font-semibold text-gray-900 capitalize">
                      {verification.contact_type.toLowerCase()}
                    </h3>
                    <StatusIcon className="w-4 h-4" />
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{verification.contact_value}</p>
                </div>
              </div>
              <div className="text-right">
                <span className="text-xs font-medium capitalize px-2 py-1 bg-white rounded">
                  {verification.status.toLowerCase()}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-white/50">
              <div>
                <p className="text-xs text-gray-600 mb-1">Format Valid</p>
                <p className="text-sm font-medium">
                  {verification.format_valid ? (
                    <span className="text-green-600">✓ Valid</span>
                  ) : (
                    <span className="text-red-600">✗ Invalid</span>
                  )}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600 mb-1">Confidence</p>
                <p className="text-sm font-medium">{formatConfidence(verification.confidence_score)}</p>
              </div>
            </div>

            {/* Email-specific details */}
            {verification.contact_type === 'EMAIL' && (
              <div className="mt-4 pt-4 border-t border-white/50 space-y-2">
                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="text-gray-600">Domain:</span>{' '}
                    <span className="font-medium">
                      {verification.domain_exists ? '✓ Exists' : '✗ Not found'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">MX Record:</span>{' '}
                    <span className="font-medium">
                      {verification.mx_record_exists ? '✓ Found' : '✗ Not found'}
                    </span>
                  </div>
                  {verification.email_exists !== null && (
                    <div>
                    <span className="text-gray-600">Email Exists:</span>{' '}
                    <span className="font-medium">
                      {verification.email_exists ? '✓ Yes' : '✗ No'}
                    </span>
                  </div>
                  )}
                </div>
              </div>
            )}

            {/* Phone-specific details */}
            {verification.contact_type === 'PHONE' && (
              <div className="mt-4 pt-4 border-t border-white/50 space-y-2">
                <div className="grid grid-cols-2 gap-4 text-xs">
                  {verification.carrier_valid !== null && (
                    <div>
                      <span className="text-gray-600">Carrier:</span>{' '}
                      <span className="font-medium">
                        {verification.carrier_valid ? '✓ Valid' : '✗ Invalid'}
                      </span>
                    </div>
                  )}
                  {verification.carrier_name && (
                    <div>
                      <span className="text-gray-600">Carrier Name:</span>{' '}
                      <span className="font-medium">{verification.carrier_name}</span>
                    </div>
                  )}
                  {verification.line_type && (
                    <div>
                      <span className="text-gray-600">Line Type:</span>{' '}
                      <span className="font-medium capitalize">{verification.line_type}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Name-specific details */}
            {verification.contact_type === 'NAME' && (
              <div className="mt-4 pt-4 border-t border-white/50 space-y-2">
                <div className="grid grid-cols-2 gap-4 text-xs">
                  {verification.name_verified !== null && (
                    <div>
                      <span className="text-gray-600">Name Verified:</span>{' '}
                      <span className="font-medium">
                        {verification.name_verified ? '✓ Yes' : '✗ No'}
                      </span>
                    </div>
                  )}
                  {verification.public_records_match !== null && (
                    <div>
                      <span className="text-gray-600">Public Records:</span>{' '}
                      <span className="font-medium">
                        {verification.public_records_match ? '✓ Match' : '✗ No match'}
                      </span>
                    </div>
                  )}
                  {verification.social_profiles_match !== null && (
                    <div>
                      <span className="text-gray-600">Social Profiles:</span>{' '}
                      <span className="font-medium">
                        {verification.social_profiles_match ? '✓ Match' : '✗ No match'}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Errors */}
            {verification.errors && verification.errors.length > 0 && (
              <div className="mt-4 pt-4 border-t border-white/50">
                <p className="text-xs text-gray-600 mb-2">Errors:</p>
                <ul className="list-disc list-inside space-y-1 text-xs text-red-600">
                  {verification.errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Sources checked */}
            {verification.sources_checked && verification.sources_checked.length > 0 && (
              <div className="mt-3 pt-3 border-t border-white/50">
                <p className="text-xs text-gray-600">
                  Sources: {verification.sources_checked.join(', ')}
                </p>
              </div>
            )}

            {/* Timestamp */}
            {verification.verified_at && (
              <div className="mt-3 pt-3 border-t border-white/50">
                <p className="text-xs text-gray-500">
                  Verified: {format(new Date(verification.verified_at), 'MMM d, yyyy HH:mm')}
                </p>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

