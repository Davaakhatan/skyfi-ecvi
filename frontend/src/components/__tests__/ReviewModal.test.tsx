import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '../../test/utils/test-utils'
import ReviewModal from '../ReviewModal'

describe('ReviewModal', () => {
  it('renders modal when open', () => {
    render(
      <ReviewModal
        isOpen={true}
        onClose={() => {}}
        companyId="test-id"
        onSuccess={() => {}}
      />
    )
    
    // The modal shows "Mark as Reviewed" when there's no existing review
    expect(screen.getByText(/mark as reviewed/i)).toBeInTheDocument()
  })

  it('does not render when closed', () => {
    render(
      <ReviewModal
        isOpen={false}
        onClose={() => {}}
        companyId="test-id"
        onSuccess={() => {}}
      />
    )
    
    expect(screen.queryByText(/mark as reviewed/i)).not.toBeInTheDocument()
  })

  it('displays existing review when provided', () => {
    const existingReview = {
      id: '1',
      company_id: 'test-id',
      reviewer_id: 'user-1',
      reviewer_name: 'Test User',
      reviewed_at: '2024-01-01T00:00:00Z',
      notes: 'Existing review notes',
      status: 'REVIEWED' as const,
    }
    
    render(
      <ReviewModal
        isOpen={true}
        onClose={() => {}}
        companyId="test-id"
        existingReview={existingReview}
        onSuccess={() => {}}
      />
    )
    
    expect(screen.getByDisplayValue('Existing review notes')).toBeInTheDocument()
  })
})

