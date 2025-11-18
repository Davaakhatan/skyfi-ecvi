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

