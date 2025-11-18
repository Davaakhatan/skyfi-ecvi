import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'
import { toast } from '../utils/toast'
import { ArrowLeft, Download, Share2, Building2, CheckCircle, AlertTriangle, Clock, Play, Loader2, RefreshCw, Edit2 } from 'lucide-react'
import RiskScoreBadge from '../components/RiskScoreBadge'
import ReviewStatusBadge from '../components/ReviewStatusBadge'
import ReviewModal from '../components/ReviewModal'
import ReTriggerModal from '../components/ReTriggerModal'
import VerificationDetails from '../components/VerificationDetails'
import VerificationIndicator, { VerificationStatus } from '../components/VerificationIndicator'
import VerificationHistoryChart from '../components/VerificationHistoryChart'
import DataCorrectionModal from '../components/DataCorrectionModal'
import CorrectionHistory from '../components/CorrectionHistory'
import CorrectionApprovalPanel from '../components/CorrectionApprovalPanel'
import ContactVerification from '../components/ContactVerification'
import { format } from 'date-fns'
import type { Company, VerificationResult, Review } from '../types/api'
import { useNotificationStore } from '../store/notificationStore'

interface ReportData {
  discrepancies?: {
    name?: any
    address?: any
    registration?: any
  }
  matches?: any[]
  confidence_scores?: any
}

export default function CompanyDetail() {
  const { id } = useParams<{ id: string }>()
  const [company, setCompany] = useState<Company | null>(null)
  const [verification, setVerification] = useState<VerificationResult | null>(null)
  const [reportData, setReportData] = useState<ReportData | null>(null)
  const [review, setReview] = useState<Review | null>(null)
  const [showReviewModal, setShowReviewModal] = useState(false)
  const [showReTriggerModal, setShowReTriggerModal] = useState(false)
  const [showCorrectionModal, setShowCorrectionModal] = useState(false)
  const [correctionField, setCorrectionField] = useState<{ name: string; type: 'legal_name' | 'registration_number' | 'jurisdiction' | 'domain'; value: string | null } | null>(null)
  const [verificationHistory, setVerificationHistory] = useState<VerificationResult[]>([])
  const [loading, setLoading] = useState(true)
  const [verifying, setVerifying] = useState(false)
  const [loadingReport, setLoadingReport] = useState(false)
  const [wasReTriggered, setWasReTriggered] = useState(false)
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const previousStatusRef = useRef<string | null>(null)
  const { addNotification } = useNotificationStore()

  const fetchCompany = useCallback(async () => {
    if (!id) return
    try {
      const response = await api.get<Company>(`/companies/${id}`)
      setCompany(response.data)
    } catch (error) {
      console.error('Failed to fetch company:', error)
    }
  }, [id])

  const fetchReportData = useCallback(async () => {
    if (!id) return
    setLoadingReport(true)
    try {
      const response = await api.get(`/reports/company/${id}/report`, {
        params: { format: 'json' },
      })
      setReportData(response.data)
    } catch (error) {
      console.error('Failed to fetch report data:', error)
    } finally {
      setLoadingReport(false)
    }
  }, [id])

  const fetchReview = useCallback(async () => {
    if (!id) return
    try {
      const response = await api.get<Review>(`/reviews/company/${id}/review`)
      setReview(response.data)
    } catch (error: any) {
      // 404 is expected if no review exists
      if (error.response?.status !== 404) {
        console.error('Failed to fetch review:', error)
      }
      setReview(null)
    }
  }, [id])

  const handleReviewSuccess = useCallback(() => {
    fetchReview()
  }, [fetchReview])

  const fetchVerificationHistory = useCallback(async () => {
    if (!id) return
    try {
      const response = await api.get<VerificationResult[]>(`/companies/${id}/verification/history`, {
        params: { limit: 5 },
      })
      setVerificationHistory(response.data)
    } catch (error) {
      console.error('Failed to fetch verification history:', error)
    }
  }, [id])

  const fetchVerification = useCallback(async () => {
    if (!id) return
    try {
      const response = await api.get<VerificationResult>(`/companies/${id}/verification`)
      const newStatus = response.data.verification_status
      const previousStatus = previousStatusRef.current
      
      // Check if status changed from IN_PROGRESS to COMPLETED
      if (previousStatus === 'IN_PROGRESS' && newStatus === 'COMPLETED') {
        // Show notification
        addNotification({
          type: 'success',
          title: 'Verification Completed',
          message: wasReTriggered
            ? `Re-analysis completed for ${company?.legal_name || 'company'}`
            : `Verification completed for ${company?.legal_name || 'company'}`,
          companyId: id,
          companyName: company?.legal_name,
          actionUrl: `/companies/${id}`,
        })
        
        // Stop polling
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current)
          pollingIntervalRef.current = null
        }
        setWasReTriggered(false)
      }
      
      // Check if status changed to FAILED
      if (previousStatus === 'IN_PROGRESS' && newStatus === 'FAILED') {
        addNotification({
          type: 'error',
          title: 'Verification Failed',
          message: `Verification failed for ${company?.legal_name || 'company'}`,
          companyId: id,
          companyName: company?.legal_name,
          actionUrl: `/companies/${id}`,
        })
        
        // Stop polling
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current)
          pollingIntervalRef.current = null
        }
        setWasReTriggered(false)
      }
      
      previousStatusRef.current = newStatus
      setVerification(response.data)
      
      // Fetch report data if verification is completed
      if (response.data.verification_status === 'COMPLETED') {
        fetchReportData()
      }
    } catch (error) {
      console.error('Failed to fetch verification:', error)
    } finally {
      setLoading(false)
    }
  }, [id, fetchReportData, company?.legal_name, wasReTriggered, addNotification])

  const handleReTriggerSuccess = useCallback(() => {
    setWasReTriggered(true)
    previousStatusRef.current = 'IN_PROGRESS' // Set initial status for comparison
    fetchVerification()
    fetchVerificationHistory()
    
    // Start polling for status updates
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
    }
    pollingIntervalRef.current = setInterval(() => {
      fetchVerification()
    }, 10000) // Poll every 10 seconds
  }, [fetchVerification, fetchVerificationHistory])

  useEffect(() => {
    if (id) {
      fetchCompany()
      fetchVerification()
      fetchReview()
      fetchVerificationHistory()
    }
  }, [id, fetchCompany, fetchVerification, fetchReview, fetchVerificationHistory])
  
  // Initialize previous status when verification is first loaded
  useEffect(() => {
    if (verification) {
      previousStatusRef.current = verification.verification_status
    }
  }, [verification?.id]) // Only update when verification ID changes (new verification)

  const handleVerify = async () => {
    if (!id) return
    setVerifying(true)
    try {
      await api.post(`/companies/${id}/verify`, null, {
        params: { async_mode: true, timeout_hours: 2.0 },
      })
      toast.success('Verification started! This may take a few minutes.')
      previousStatusRef.current = 'IN_PROGRESS'
      
      // Start polling for status updates
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
      }
      pollingIntervalRef.current = setInterval(() => {
        fetchVerification()
      }, 10000) // Poll every 10 seconds
      
      // Refresh verification status after a short delay
      setTimeout(() => {
        fetchVerification()
      }, 2000)
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to start verification'
      toast.error(errorMessage)
    } finally {
      setVerifying(false)
    }
  }
  
  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
      }
    }
  }, [])
  
  // Stop polling when verification is completed or failed
  useEffect(() => {
    if (verification && (verification.verification_status === 'COMPLETED' || verification.verification_status === 'FAILED')) {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
        pollingIntervalRef.current = null
      }
    }
  }, [verification])

  const handleExport = async (format: 'json' | 'csv' | 'pdf' | 'html') => {
    if (!id) return
    try {
      const response = await api.get(`/reports/company/${id}/report`, {
        params: { format },
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `report-${id}.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      toast.success(`Report exported as ${format.toUpperCase()}`)
    } catch (error) {
      console.error('Export failed:', error)
      toast.error('Failed to export report')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!company) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Company not found</p>
        <Link to="/companies" className="text-primary-600 hover:text-primary-700 mt-4 inline-block">
          Back to companies
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/companies"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{company.legal_name}</h1>
            <p className="text-gray-600 mt-1">Company verification details</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowReviewModal(true)}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            {review ? (
              <>
                <CheckCircle className="w-4 h-4" />
                <span>Update Review</span>
              </>
            ) : (
              <>
                <CheckCircle className="w-4 h-4" />
                <span>Mark as Reviewed</span>
              </>
            )}
          </button>
          {!verification || verification.verification_status === 'FAILED' ? (
            <button
              onClick={handleVerify}
              disabled={verifying}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {verifying ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Starting...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Verify Company</span>
                </>
              )}
            </button>
          ) : null}
          {verification && verification.verification_status === 'COMPLETED' && (
            <>
              <button
                onClick={() => setShowReTriggerModal(true)}
                className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Re-trigger</span>
              </button>
              <button
                onClick={() => handleExport('pdf')}
                className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                <Share2 className="w-4 h-4" />
                <span>Share</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Review Status Card */}
      {review && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Review Status</h2>
              <p className="text-sm text-gray-600">
                Reviewed by {review.reviewer_name} on {format(new Date(review.reviewed_at), 'MMM d, yyyy')}
              </p>
            </div>
            <ReviewStatusBadge status={review.status} />
          </div>
          {review.notes && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium text-gray-700 mb-1">Notes</p>
              <p className="text-sm text-gray-600 whitespace-pre-wrap">{review.notes}</p>
            </div>
          )}
        </div>
      )}

      {/* Risk Score Card */}
      {verification ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Risk Assessment</h2>
              <p className="text-sm text-gray-600">Current verification status and risk score</p>
            </div>
            <RiskScoreBadge
              score={verification.risk_score}
              category={verification.risk_category}
            />
          </div>
          <div className="mt-6 grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <div className="flex items-center space-x-2 mt-1">
                {verification.verification_status === 'COMPLETED' && (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
                {verification.verification_status === 'IN_PROGRESS' && (
                  <Clock className="w-5 h-5 text-yellow-600" />
                )}
                {verification.verification_status === 'FAILED' && (
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                )}
                <p className="text-lg font-medium text-gray-900 capitalize">
                  {verification.verification_status.toLowerCase().replace('_', ' ')}
                </p>
              </div>
            </div>
            {verification.analysis_completed_at && (
              <div>
                <p className="text-sm text-gray-600">Completed</p>
                <p className="text-lg font-medium text-gray-900 mt-1">
                  {format(new Date(verification.analysis_completed_at), 'MMM d, yyyy HH:mm')}
                </p>
              </div>
            )}
            {verification.verification_status === 'IN_PROGRESS' && (
              <div className="col-span-2">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    Verification is in progress. This may take up to 2 hours. You can check back later or refresh the page.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="text-center py-8">
            <Building2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Verification Yet</h3>
            <p className="text-gray-600 mb-4">Start verification to get a risk assessment for this company.</p>
            <button
              onClick={handleVerify}
              disabled={verifying}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {verifying ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Starting Verification...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  <span>Start Verification</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Company Information */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Company Information</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center space-x-2">
                <p className="text-sm text-gray-600">Legal Name</p>
                {reportData?.discrepancies?.name && (
                  <VerificationIndicator
                    status={
                      reportData.discrepancies.name.severity === 'high'
                        ? 'discrepancy'
                        : reportData.discrepancies.name.severity === 'medium'
                        ? 'partial'
                        : 'verified'
                    }
                    label=""
                    size="sm"
                  />
                )}
              </div>
              <button
                onClick={() => {
                  setCorrectionField({ name: 'Legal Name', type: 'legal_name', value: company.legal_name })
                  setShowCorrectionModal(true)
                }}
                className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
                title="Correct this field"
              >
                <Edit2 className="w-4 h-4" />
              </button>
            </div>
            <p className="text-lg font-medium text-gray-900 mt-1">{company.legal_name}</p>
          </div>
          {company.registration_number && (
            <div>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center space-x-2">
                  <p className="text-sm text-gray-600">Registration Number</p>
                  {reportData?.discrepancies?.registration && (
                    <VerificationIndicator
                      status={
                        reportData.discrepancies.registration.severity === 'high'
                          ? 'discrepancy'
                          : reportData.discrepancies.registration.severity === 'medium'
                          ? 'partial'
                          : 'verified'
                      }
                      label=""
                      size="sm"
                    />
                  )}
                </div>
                <button
                  onClick={() => {
                    setCorrectionField({ name: 'Registration Number', type: 'registration_number', value: company.registration_number })
                    setShowCorrectionModal(true)
                  }}
                  className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
                  title="Correct this field"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
              </div>
              <p className="text-lg font-medium text-gray-900 mt-1">{company.registration_number}</p>
            </div>
          )}
          {company.jurisdiction && (
            <div>
              <div className="flex items-center justify-between mb-1">
                <p className="text-sm text-gray-600">Jurisdiction</p>
                <button
                  onClick={() => {
                    setCorrectionField({ name: 'Jurisdiction', type: 'jurisdiction', value: company.jurisdiction })
                    setShowCorrectionModal(true)
                  }}
                  className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
                  title="Correct this field"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
              </div>
              <p className="text-lg font-medium text-gray-900 mt-1">{company.jurisdiction}</p>
            </div>
          )}
          {company.domain && (
            <div>
              <div className="flex items-center justify-between mb-1">
                <p className="text-sm text-gray-600">Domain</p>
                <button
                  onClick={() => {
                    setCorrectionField({ name: 'Domain', type: 'domain', value: company.domain })
                    setShowCorrectionModal(true)
                  }}
                  className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
                  title="Correct this field"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
              </div>
              <a
                href={`https://${company.domain}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-lg font-medium text-primary-600 hover:text-primary-700 mt-1 inline-block"
              >
                {company.domain}
              </a>
            </div>
          )}
          <div>
            <p className="text-sm text-gray-600">Created</p>
            <p className="text-lg font-medium text-gray-900 mt-1">
              {format(new Date(company.created_at), 'MMM d, yyyy')}
            </p>
          </div>
        </div>
      </div>

      {/* Pending Corrections Approval Panel (Admin/Compliance only) */}
      {id && (
        <CorrectionApprovalPanel
          companyId={id}
          onApprovalChange={() => {
            fetchCompany() // Refresh company data after approval
          }}
        />
      )}

      {/* Correction History */}
      {id && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Data Correction History</h2>
          <CorrectionHistory companyId={id} />
        </div>
      )}

      {/* Contact Verification */}
      {verification && verification.verification_status === 'COMPLETED' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Contact Verification</h2>
          <ContactVerification
            companyId={id!}
            verificationResultId={verification.id}
          />
        </div>
      )}

      {/* Verification Details */}
      {verification && verification.verification_status === 'COMPLETED' && reportData && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Verification Details</h2>
          {loadingReport ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Summary Indicators */}
              <div className="flex items-center space-x-4 pb-4 border-b border-gray-200">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span className="text-sm text-gray-600">
                    Verified: {reportData.matches?.length || 0}
                  </span>
                </div>
                {reportData.discrepancies && (
                  <>
                    {(reportData.discrepancies.name?.discrepancies?.length > 0 ||
                      reportData.discrepancies.address?.discrepancies?.length > 0 ||
                      reportData.discrepancies.registration?.discrepancies?.length > 0) && (
                      <div className="flex items-center space-x-2">
                        <AlertTriangle className="w-5 h-5 text-red-600" />
                        <span className="text-sm text-gray-600">
                          Discrepancies:{' '}
                          {(reportData.discrepancies.name?.discrepancies?.length || 0) +
                            (reportData.discrepancies.address?.discrepancies?.length || 0) +
                            (reportData.discrepancies.registration?.discrepancies?.length || 0)}
                        </span>
                      </div>
                    )}
                  </>
                )}
              </div>

              {/* Detailed Verification Data */}
              {company && (
                <VerificationDetails
                  data={[
                    {
                      field: 'legal_name',
                      value: company.legal_name,
                      status: reportData.discrepancies?.name
                        ? reportData.discrepancies.name.severity === 'high'
                          ? 'discrepancy'
                          : reportData.discrepancies.name.severity === 'medium'
                          ? 'partial'
                          : 'verified'
                        : 'verified',
                      confidence: reportData.discrepancies?.name?.confidence,
                      sources: reportData.discrepancies?.name?.sources_checked,
                      matches: reportData.discrepancies?.name?.matches,
                      discrepancies: reportData.discrepancies?.name?.discrepancies?.map(
                        (d: any) => ({
                          source: d.source || 'Unknown',
                          value: d.reported_name || d.value || 'N/A',
                          type: d.type || 'mismatch',
                        })
                      ),
                    },
                    ...(company.registration_number
                      ? [
                          {
                            field: 'registration_number',
                            value: company.registration_number,
                            status: reportData.discrepancies?.registration
                              ? reportData.discrepancies.registration.severity === 'high'
                                ? 'discrepancy'
                                : reportData.discrepancies.registration.severity === 'medium'
                                ? 'partial'
                                : 'verified'
                              : ('verified' as VerificationStatus),
                            confidence: reportData.discrepancies?.registration?.confidence,
                            sources: reportData.discrepancies?.registration?.sources_checked,
                            matches: reportData.discrepancies?.registration?.matches,
                            discrepancies: reportData.discrepancies?.registration?.discrepancies?.map(
                              (d: any) => ({
                                source: d.source || 'Unknown',
                                value: d.value || 'N/A',
                                type: d.type || 'mismatch',
                              })
                            ),
                          },
                        ]
                      : []),
                  ]}
                />
              )}
            </div>
          )}
        </div>
      )}

      {/* Verification Report */}
      {verification && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Verification Report</h2>
          <p className="text-gray-600">Full verification report available for download.</p>
          <div className="mt-4 flex items-center space-x-3">
            <button
              onClick={() => handleExport('json')}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              JSON
            </button>
            <button
              onClick={() => handleExport('csv')}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              CSV
            </button>
            <button
              onClick={() => handleExport('pdf')}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              PDF
            </button>
            <button
              onClick={() => handleExport('html')}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              HTML
            </button>
          </div>
        </div>
      )}

      {/* Verification History Comparison */}
      {verificationHistory.length > 1 && (
        <div className="space-y-6">
          {/* Visual Charts */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Verification History Analysis</h2>
            <VerificationHistoryChart history={verificationHistory} />
          </div>

          {/* History List */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Verification History</h2>
            <div className="space-y-3">
              {verificationHistory.map((result, index) => (
                <div
                  key={result.id}
                  className={`p-4 rounded-lg border ${
                    index === 0
                      ? 'bg-primary-50 border-primary-200'
                      : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {index === 0 && (
                        <span className="px-2 py-1 bg-primary-600 text-white text-xs font-medium rounded">
                          Latest
                        </span>
                      )}
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {format(new Date(result.created_at), 'MMM d, yyyy HH:mm')}
                        </p>
                        <div className="flex items-center space-x-4 mt-1">
                          <RiskScoreBadge
                            score={result.risk_score}
                            category={result.risk_category}
                          />
                          <span className="text-xs text-gray-600 capitalize">
                            {result.verification_status.toLowerCase().replace('_', ' ')}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Review Modal */}
      {id && (
        <ReviewModal
          isOpen={showReviewModal}
          onClose={() => setShowReviewModal(false)}
          companyId={id}
          existingReview={review}
          onSuccess={handleReviewSuccess}
        />
      )}

      {/* Re-trigger Modal */}
      {id && (
        <ReTriggerModal
          isOpen={showReTriggerModal}
          onClose={() => setShowReTriggerModal(false)}
          companyId={id}
          onSuccess={handleReTriggerSuccess}
        />
      )}

      {/* Data Correction Modal */}
      {id && company && correctionField && (
        <DataCorrectionModal
          isOpen={showCorrectionModal}
          onClose={() => {
            setShowCorrectionModal(false)
            setCorrectionField(null)
          }}
          company={company}
          fieldName={correctionField.name}
          fieldType={correctionField.type}
          currentValue={correctionField.value}
          onSuccess={() => {
            fetchCompany() // Refresh company data
            setShowCorrectionModal(false)
            setCorrectionField(null)
          }}
        />
      )}
    </div>
  )
}

