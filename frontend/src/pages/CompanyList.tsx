import { useState, useEffect, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import { Search, Filter, ChevronRight, Building2, AlertCircle, CheckCircle, Clock, Plus } from 'lucide-react'
import { format } from 'date-fns'
import RiskScoreBadge from '../components/RiskScoreBadge'
import ReviewStatusBadge from '../components/ReviewStatusBadge'
import CreateCompanyModal from '../components/CreateCompanyModal'
import type { CompanyWithVerification, CompanyListResponse, CompanyListParams, Company } from '../types/api'

export default function CompanyList() {
  const [companies, setCompanies] = useState<CompanyWithVerification[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [showFilters, setShowFilters] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [reviewFilter, setReviewFilter] = useState<'all' | 'reviewed' | 'pending' | 'flagged'>('all')
  const navigate = useNavigate()
  const limit = 20

  const fetchCompanies = useCallback(async () => {
    setLoading(true)
    try {
      const params: CompanyListParams = {
        skip: (page - 1) * limit,
        limit,
      }
      if (search) params.search = search
      if (reviewFilter === 'reviewed') params.reviewed = true
      else if (reviewFilter === 'pending') params.reviewed = false

      const response = await api.get<CompanyListResponse>('/companies/', { params })
      setCompanies(response.data.items || [])
      setTotal(response.data.total || 0)
    } catch (error) {
      console.error('Failed to fetch companies:', error)
    } finally {
      setLoading(false)
    }
  }, [page, search, reviewFilter, limit])

  useEffect(() => {
    fetchCompanies()
  }, [fetchCompanies])

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'IN_PROGRESS':
        return <Clock className="w-4 h-4 text-yellow-600" />
      case 'FAILED':
        return <AlertCircle className="w-4 h-4 text-red-600" />
      default:
        return null
    }
  }

  const handleCompanyCreated = (company: Company) => {
    // Refresh the list
    fetchCompanies()
    // Navigate to the new company
    navigate(`/companies/${company.id}`)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Companies</h1>
          <p className="text-gray-600 mt-2">Manage and verify company information</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>Add Company</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search companies..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
              showFilters
                ? 'bg-primary-50 border-primary-300 text-primary-700'
                : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Filter className="w-4 h-4" />
            <span>Filters</span>
          </button>
        </div>
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-gray-700">Review Status:</label>
              <select
                value={reviewFilter}
                onChange={(e) => {
                  setReviewFilter(e.target.value as 'all' | 'reviewed' | 'pending' | 'flagged')
                  setPage(1)
                }}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="all">All</option>
                <option value="reviewed">Reviewed</option>
                <option value="pending">Pending</option>
                <option value="flagged">Flagged</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Company List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : companies.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <Building2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No companies found</h3>
          <p className="text-gray-600">Get started by adding your first company.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="divide-y divide-gray-200">
            {companies.map((company) => (
              <Link
                key={company.id}
                to={`/companies/${company.id}`}
                className="block p-6 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0">
                        <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                          <Building2 className="w-6 h-6 text-primary-600" />
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-gray-900 truncate">
                          {company.legal_name}
                        </h3>
                        <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
                          {company.registration_number && (
                            <span>Reg: {company.registration_number}</span>
                          )}
                          {company.jurisdiction && (
                            <span>• {company.jurisdiction}</span>
                          )}
                          {company.domain && (
                            <span>• {company.domain}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-6 ml-6">
                    {company.review && (
                      <ReviewStatusBadge status={company.review.status} size="sm" />
                    )}
                    {company.verification_result && (
                      <>
                        <RiskScoreBadge
                          score={company.verification_result.risk_score}
                          category={company.verification_result.risk_category}
                        />
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(company.verification_result.verification_status)}
                          <span className="text-sm text-gray-600 capitalize">
                            {company.verification_result.verification_status.toLowerCase().replace('_', ' ')}
                          </span>
                        </div>
                      </>
                    )}
                    <div className="text-sm text-gray-500">
                      {format(new Date(company.created_at), 'MMM d, yyyy')}
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Pagination */}
      {total > limit && (
        <div className="flex items-center justify-between bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="text-sm text-gray-600">
            Showing {(page - 1) * limit + 1} to {Math.min(page * limit, total)} of {total} companies
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={page * limit >= total}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Create Company Modal */}
      <CreateCompanyModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={handleCompanyCreated}
      />
    </div>
  )
}

