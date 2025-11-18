// API Response Types

export interface User {
  id: string
  email: string
  username: string
  role: 'admin' | 'operator' | 'viewer'
  is_active: boolean
  created_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Company {
  id: string
  legal_name: string
  registration_number: string | null
  jurisdiction: string | null
  domain: string | null
  created_at: string
  updated_at: string
}

export interface VerificationResult {
  id: string
  company_id: string
  risk_score: number
  risk_category: 'LOW' | 'MEDIUM' | 'HIGH'
  verification_status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED'
  analysis_started_at: string | null
  analysis_completed_at: string | null
  created_at: string
}

export interface CompanyWithVerification extends Company {
  verification_result?: VerificationResult
  review?: {
    status: ReviewStatus
    reviewed_at: string | null
    reviewer_name: string | null
  }
}

export interface CompanyListResponse {
  items: CompanyWithVerification[]
  total: number
  skip: number
  limit: number
}

export interface CompanyListParams {
  skip?: number
  limit?: number
  search?: string
  risk_score_min?: number
  risk_score_max?: number
  risk_category?: 'LOW' | 'MEDIUM' | 'HIGH'
  verification_status?: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED'
  reviewed?: boolean
  reviewer_id?: string
  start_date?: string
  end_date?: string
  sort_by?: 'created_at' | 'legal_name' | 'risk_score'
  sort_order?: 'asc' | 'desc'
}

export type CorrectionStatus = 'PENDING' | 'APPROVED' | 'REJECTED'

export interface DataCorrection {
  id: string
  company_id: string
  company_data_id: string | null
  field_name: string
  field_type: string
  old_value: string | null
  new_value: string
  correction_reason: string | null
  status: CorrectionStatus
  version: string
  corrected_by: string
  corrector_name: string
  approved_by: string | null
  approver_name: string | null
  approved_at: string | null
  created_at: string
  updated_at: string
}

export interface CorrectionCreate {
  field_name: string
  field_type: string
  new_value: string
  correction_reason?: string | null
  company_data_id?: string | null
  metadata?: Record<string, any> | null
}

export type ContactType = 'EMAIL' | 'PHONE' | 'NAME'
export type ContactVerificationStatus = 'PENDING' | 'VERIFIED' | 'FAILED' | 'PARTIAL'

export interface ContactVerificationResult {
  id: string
  company_id: string
  verification_result_id: string | null
  contact_type: ContactType
  contact_value: string
  country_code: string | null
  format_valid: boolean
  domain_exists: boolean | null
  mx_record_exists: boolean | null
  email_exists: boolean | null
  carrier_valid: boolean | null
  carrier_name: string | null
  line_type: string | null
  name_verified: boolean | null
  public_records_match: boolean | null
  social_profiles_match: boolean | null
  status: ContactVerificationStatus
  confidence_score: number | null
  risk_score: number | null
  verification_details: Record<string, any> | null
  errors: string[] | null
  sources_checked: string[] | null
  verified_at: string | null
  created_at: string
  updated_at: string
}

export interface ContactVerificationRequest {
  email?: string | null
  phone?: string | null
  name?: string | null
  country_code?: string | null
}

export type ReviewStatus = 'PENDING' | 'REVIEWED' | 'FLAGGED'

export interface Review {
  id: string
  company_id: string
  reviewer_id: string
  reviewer_name: string
  reviewed_at: string
  notes: string | null
  status: ReviewStatus
}

export interface CompanyWithReview extends CompanyWithVerification {
  review?: Review
}

