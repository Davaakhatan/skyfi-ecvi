import { useState } from 'react'
import { X, Building2, Loader2 } from 'lucide-react'
import api from '../services/api'
import { toast } from '../utils/toast'
import type { Company } from '../types/api'

interface CreateCompanyModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: (company: Company) => void
}

export default function CreateCompanyModal({ isOpen, onClose, onSuccess }: CreateCompanyModalProps) {
  const [formData, setFormData] = useState({
    legal_name: '',
    registration_number: '',
    jurisdiction: '',
    domain: '',
  })
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  if (!isOpen) return null

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }))
    }
  }

  const validate = () => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.legal_name.trim()) {
      newErrors.legal_name = 'Company name is required'
    } else if (formData.legal_name.trim().length < 2) {
      newErrors.legal_name = 'Company name must be at least 2 characters'
    }

    if (formData.domain && !formData.domain.match(/^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$/)) {
      newErrors.domain = 'Please enter a valid domain (e.g., example.com)'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validate()) {
      return
    }

    setLoading(true)
    try {
      const payload = {
        legal_name: formData.legal_name.trim(),
        registration_number: formData.registration_number.trim() || undefined,
        jurisdiction: formData.jurisdiction.trim().toUpperCase() || undefined,
        domain: formData.domain.trim().toLowerCase() || undefined,
      }

      const response = await api.post<Company>('/companies/', payload)
      toast.success('Company created successfully!')
      onSuccess(response.data)
      handleClose()
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to create company'
      toast.error(errorMessage)
      if (error.response?.data?.detail) {
        setErrors({ form: errorMessage })
      }
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setFormData({
      legal_name: '',
      registration_number: '',
      jurisdiction: '',
      domain: '',
    })
    setErrors({})
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <Building2 className="w-6 h-6 text-primary-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Create Company</h2>
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
          {errors.form && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {errors.form}
            </div>
          )}

          <div>
            <label htmlFor="legal_name" className="block text-sm font-medium text-gray-700 mb-2">
              Company Name <span className="text-red-500">*</span>
            </label>
            <input
              id="legal_name"
              name="legal_name"
              type="text"
              value={formData.legal_name}
              onChange={handleChange}
              required
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors ${
                errors.legal_name ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Enter company legal name"
            />
            {errors.legal_name && (
              <p className="mt-1 text-sm text-red-600">{errors.legal_name}</p>
            )}
          </div>

          <div>
            <label htmlFor="domain" className="block text-sm font-medium text-gray-700 mb-2">
              Domain
            </label>
            <input
              id="domain"
              name="domain"
              type="text"
              value={formData.domain}
              onChange={handleChange}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors ${
                errors.domain ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="example.com"
            />
            {errors.domain && (
              <p className="mt-1 text-sm text-red-600">{errors.domain}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="registration_number" className="block text-sm font-medium text-gray-700 mb-2">
                Registration Number
              </label>
              <input
                id="registration_number"
                name="registration_number"
                type="text"
                value={formData.registration_number}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="12345678"
              />
            </div>

            <div>
              <label htmlFor="jurisdiction" className="block text-sm font-medium text-gray-700 mb-2">
                Jurisdiction
              </label>
              <input
                id="jurisdiction"
                name="jurisdiction"
                type="text"
                value={formData.jurisdiction}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="US, GB, etc."
                maxLength={2}
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
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
                  <span>Creating...</span>
                </>
              ) : (
                <span>Create Company</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

