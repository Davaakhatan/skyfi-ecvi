import { useState, useEffect } from 'react'
import { X, Loader2, Edit2, AlertCircle } from 'lucide-react'
import api from '../services/api'
import { toast } from '../utils/toast'
import type { DataCorrection, CorrectionCreate, Company } from '../types/api'
import { useAuthStore } from '../store/authStore'

interface DataCorrectionModalProps {
  isOpen: boolean
  onClose: () => void
  company: Company
  fieldName: string
  fieldType: 'legal_name' | 'registration_number' | 'jurisdiction' | 'domain'
  currentValue: string | null
  onSuccess: () => void
}

export default function DataCorrectionModal({
  isOpen,
  onClose,
  company,
  fieldName,
  fieldType,
  currentValue,
  onSuccess,
}: DataCorrectionModalProps) {
  const [newValue, setNewValue] = useState('')
  const [reason, setReason] = useState('')
  const [loading, setLoading] = useState(false)
  const { user } = useAuthStore()

  useEffect(() => {
    if (isOpen) {
      setNewValue(currentValue || '')
      setReason('')
    }
  }, [isOpen, currentValue])

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!newValue.trim()) {
      toast.error('New value is required')
      return
    }
    
    if (newValue.trim() === currentValue) {
      toast.error('New value must be different from current value')
      return
    }

    if (!user) {
      toast.error('You must be logged in to submit a correction.')
      return
    }

    setLoading(true)
    try {
      const correctionData: CorrectionCreate = {
        field_name: fieldName,
        field_type: fieldType,
        new_value: newValue.trim(),
        correction_reason: reason.trim() || null,
      }

      await api.post(`/company/${company.id}/corrections`, correctionData)
      toast.success('Correction submitted successfully! It will be reviewed by an admin.')
      onSuccess()
      onClose()
    } catch (error: any) {
      console.error('Failed to submit correction:', error)
      toast.error(error.response?.data?.detail || 'Failed to submit correction.')
    } finally {
      setLoading(false)
    }
  }

  const getFieldLabel = () => {
    switch (fieldType) {
      case 'legal_name':
        return 'Legal Name'
      case 'registration_number':
        return 'Registration Number'
      case 'jurisdiction':
        return 'Jurisdiction'
      case 'domain':
        return 'Domain'
      default:
        return fieldName
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <Edit2 className="w-6 h-6 text-primary-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Correct Data</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={loading}
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          <div>
            <p className="text-sm text-gray-600 mb-4">
              Submit a correction for <span className="font-medium">{getFieldLabel()}</span>. 
              This will be reviewed by an administrator before being applied.
            </p>
          </div>

          {/* Current Value */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Value
            </label>
            <div className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-600">
              {currentValue || <span className="text-gray-400 italic">No value set</span>}
            </div>
          </div>

          {/* New Value */}
          <div>
            <label htmlFor="newValue" className="block text-sm font-medium text-gray-700 mb-2">
              New Value <span className="text-red-500">*</span>
            </label>
            <input
              id="newValue"
              type="text"
              value={newValue}
              onChange={(e) => setNewValue(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
              placeholder={`Enter new ${getFieldLabel().toLowerCase()}`}
              required
              disabled={loading}
            />
          </div>

          {/* Reason */}
          <div>
            <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-2">
              Reason for Correction (Optional)
            </label>
            <textarea
              id="reason"
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors resize-none"
              placeholder="e.g., Updated information from official registry, typo correction, etc."
              disabled={loading}
            />
          </div>

          {/* Info Alert */}
          <div className="flex items-start space-x-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-blue-800">
              Corrections require approval from an administrator. Once approved, the new value will be applied and a new verification analysis will be triggered.
            </p>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !newValue.trim() || newValue.trim() === currentValue}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Submitting...</span>
                </>
              ) : (
                <>
                  <Edit2 className="w-4 h-4" />
                  <span>Submit Correction</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

