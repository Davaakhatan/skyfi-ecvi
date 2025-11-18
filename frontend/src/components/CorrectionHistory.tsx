import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Clock, History, User } from 'lucide-react'
import api from '../services/api'
import { format } from 'date-fns'
import type { DataCorrection } from '../types/api'
import clsx from 'clsx'

interface CorrectionHistoryProps {
  companyId: string
  fieldName?: string
}

export default function CorrectionHistory({ companyId, fieldName }: CorrectionHistoryProps) {
  const [corrections, setCorrections] = useState<DataCorrection[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCorrections()
  }, [companyId, fieldName])

  const fetchCorrections = async () => {
    setLoading(true)
    try {
      const params: any = {}
      if (fieldName) {
        params.field_name = fieldName
      }
      const response = await api.get<DataCorrection[]>(`/company/${companyId}/corrections`, { params })
      setCorrections(response.data)
    } catch (error) {
      console.error('Failed to fetch correction history:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return CheckCircle
      case 'REJECTED':
        return XCircle
      default:
        return Clock
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'REJECTED':
        return 'text-red-600 bg-red-50 border-red-200'
      default:
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (corrections.length === 0) {
    return (
      <div className="text-center py-8">
        <History className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-sm text-gray-500">No correction history</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {corrections.map((correction) => {
        const StatusIcon = getStatusIcon(correction.status)
        return (
          <div
            key={correction.id}
            className={clsx(
              'p-4 rounded-lg border',
              getStatusColor(correction.status)
            )}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <StatusIcon className="w-5 h-5" />
                  <span className="text-sm font-medium capitalize">{correction.status.toLowerCase()}</span>
                  <span className="text-xs text-gray-500">v{correction.version}</span>
                </div>
                
                <div className="space-y-1 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Field:</span>{' '}
                    <span className="text-gray-600">{correction.field_name}</span>
                  </div>
                  
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
                  
                  <div className="flex items-center space-x-4 mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500">
                    <div className="flex items-center space-x-1">
                      <User className="w-3 h-3" />
                      <span>By {correction.corrector_name}</span>
                    </div>
                    {correction.approver_name && (
                      <div className="flex items-center space-x-1">
                        <CheckCircle className="w-3 h-3" />
                        <span>Approved by {correction.approver_name}</span>
                      </div>
                    )}
                    <span>{format(new Date(correction.created_at), 'MMM d, yyyy HH:mm')}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

