import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Clock, User, AlertCircle } from 'lucide-react'
import api from '../services/api'
import { toast } from '../utils/toast'
import { format } from 'date-fns'
import type { DataCorrection } from '../types/api'
import { useAuthStore } from '../store/authStore'
import clsx from 'clsx'

interface CorrectionApprovalPanelProps {
  companyId: string
  onApprovalChange: () => void
}

export default function CorrectionApprovalPanel({
  companyId,
  onApprovalChange,
}: CorrectionApprovalPanelProps) {
  const [pendingCorrections, setPendingCorrections] = useState<DataCorrection[]>([])
  const [loading, setLoading] = useState(true)
  const { user } = useAuthStore()

  useEffect(() => {
    fetchPendingCorrections()
  }, [companyId])

  const fetchPendingCorrections = async () => {
    setLoading(true)
    try {
      const response = await api.get<DataCorrection[]>(`/company/${companyId}/corrections`)
      // Filter for pending corrections
      const pending = response.data.filter((c) => c.status === 'PENDING')
      setPendingCorrections(pending)
    } catch (error) {
      console.error('Failed to fetch pending corrections:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (correctionId: string) => {
    try {
      await api.post(`/corrections/${correctionId}/approve`)
      toast.success('Correction approved and applied successfully!')
      fetchPendingCorrections()
      onApprovalChange()
    } catch (error: any) {
      console.error('Failed to approve correction:', error)
      toast.error(error.response?.data?.detail || 'Failed to approve correction.')
    }
  }

  const handleReject = async (correctionId: string, reason?: string) => {
    const rejectionReason = reason || prompt('Please provide a reason for rejection:')
    if (!rejectionReason) {
      toast.error('Rejection reason is required')
      return
    }

    try {
      await api.post(`/corrections/${correctionId}/reject`, null, {
        params: { rejection_reason: rejectionReason },
      })
      toast.success('Correction rejected successfully')
      fetchPendingCorrections()
      onApprovalChange()
    } catch (error: any) {
      console.error('Failed to reject correction:', error)
      toast.error(error.response?.data?.detail || 'Failed to reject correction.')
    }
  }

  // Check if user has admin/compliance role
  const canApprove = user?.role === 'admin' || user?.role === 'compliance'

  if (!canApprove) {
    return null
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-4">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (pendingCorrections.length === 0) {
    return null
  }

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
      <div className="flex items-center space-x-2 mb-4">
        <AlertCircle className="w-5 h-5 text-yellow-600" />
        <h3 className="text-lg font-semibold text-gray-900">Pending Corrections</h3>
        <span className="px-2 py-1 bg-yellow-600 text-white text-xs font-medium rounded-full">
          {pendingCorrections.length}
        </span>
      </div>

      <div className="space-y-4">
        {pendingCorrections.map((correction) => (
          <div
            key={correction.id}
            className="bg-white rounded-lg border border-yellow-200 p-4"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <Clock className="w-4 h-4 text-yellow-600" />
                  <span className="text-sm font-medium text-gray-900">{correction.field_name}</span>
                  <span className="text-xs text-gray-500">v{correction.version}</span>
                </div>

                <div className="space-y-1 text-sm">
                  {correction.old_value && (
                    <div>
                      <span className="font-medium text-gray-700">Old:</span>{' '}
                      <span className="text-gray-600 line-through">{correction.old_value}</span>
                    </div>
                  )}
                  <div>
                    <span className="font-medium text-gray-700">New:</span>{' '}
                    <span className="text-gray-900 font-medium">{correction.new_value}</span>
                  </div>
                  {correction.correction_reason && (
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <span className="font-medium text-gray-700">Reason:</span>{' '}
                      <span className="text-gray-600">{correction.correction_reason}</span>
                    </div>
                  )}
                  <div className="flex items-center space-x-1 mt-2 text-xs text-gray-500">
                    <User className="w-3 h-3" />
                    <span>Submitted by {correction.corrector_name}</span>
                    <span className="mx-2">•</span>
                    <span>{format(new Date(correction.created_at), 'MMM d, yyyy HH:mm')}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end space-x-3 pt-3 border-t border-gray-200">
              <button
                onClick={() => handleReject(correction.id)}
                className="flex items-center space-x-2 px-4 py-2 border border-red-300 rounded-lg text-sm font-medium text-red-700 hover:bg-red-50 transition-colors"
              >
                <XCircle className="w-4 h-4" />
                <span>Reject</span>
              </button>
              <button
                onClick={() => handleApprove(correction.id)}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
              >
                <CheckCircle className="w-4 h-4" />
                <span>Approve</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

