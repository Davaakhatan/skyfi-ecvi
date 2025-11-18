import { useState } from 'react'
import { X, CheckCircle, AlertCircle, Clock, Loader2 } from 'lucide-react'
import api from '../services/api'
import { toast } from '../utils/toast'
import type { Review, ReviewStatus } from '../types/api'

interface ReviewModalProps {
  isOpen: boolean
  onClose: () => void
  companyId: string
  existingReview?: Review | null
  onSuccess: () => void
}

export default function ReviewModal({
  isOpen,
  onClose,
  companyId,
  existingReview,
  onSuccess,
}: ReviewModalProps) {
  const [status, setStatus] = useState<ReviewStatus>(
    existingReview?.status || 'REVIEWED'
  )
  const [notes, setNotes] = useState(existingReview?.notes || '')
  const [loading, setLoading] = useState(false)

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await api.post(`/reviews/company/${companyId}/review`, {
        status,
        notes: notes.trim() || null,
      })

      toast.success(
        existingReview ? 'Review updated successfully' : 'Company marked as reviewed'
      )
      onSuccess()
      handleClose()
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to save review'
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!existingReview) return

    if (!confirm('Are you sure you want to remove this review?')) {
      return
    }

    setLoading(true)
    try {
      await api.delete(`/reviews/company/${companyId}/review`)
      toast.success('Review removed successfully')
      onSuccess()
      handleClose()
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to remove review'
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setNotes(existingReview?.notes || '')
    setStatus(existingReview?.status || 'REVIEWED')
    onClose()
  }

  const statusOptions: { value: ReviewStatus; label: string; icon: typeof CheckCircle }[] = [
    { value: 'REVIEWED', label: 'Reviewed', icon: CheckCircle },
    { value: 'FLAGGED', label: 'Flagged', icon: AlertCircle },
    { value: 'PENDING', label: 'Pending', icon: Clock },
  ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-primary-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">
              {existingReview ? 'Update Review' : 'Mark as Reviewed'}
            </h2>
          </div>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={loading}
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Status Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Review Status
            </label>
            <div className="grid grid-cols-3 gap-3">
              {statusOptions.map((option) => {
                const Icon = option.icon
                const isSelected = status === option.value
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setStatus(option.value)}
                    className={`
                      flex flex-col items-center space-y-2 p-4 rounded-lg border-2 transition-all
                      ${
                        isSelected
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }
                    `}
                  >
                    <Icon
                      className={`w-6 h-6 ${
                        isSelected ? 'text-primary-600' : 'text-gray-400'
                      }`}
                    />
                    <span
                      className={`text-sm font-medium ${
                        isSelected ? 'text-primary-700' : 'text-gray-600'
                      }`}
                    >
                      {option.label}
                    </span>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Notes */}
          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
              Notes (Optional)
            </label>
            <textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors resize-none"
              placeholder="Add any notes or comments about this review..."
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            {existingReview && (
              <button
                type="button"
                onClick={handleDelete}
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Remove Review
              </button>
            )}
            <div className="flex items-center space-x-3 ml-auto">
              <button
                type="button"
                onClick={handleClose}
                disabled={loading}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <span>Save Review</span>
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}

