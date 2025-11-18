import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '../../test/utils'
import userEvent from '@testing-library/user-event'
import CreateCompanyModal from '../CreateCompanyModal'

// Mock API
vi.mock('../../services/api', () => ({
  default: {
    post: vi.fn(),
  },
}))

describe('CreateCompanyModal', () => {
  it('renders modal when open', () => {
    render(
      <CreateCompanyModal
        isOpen={true}
        onClose={() => {}}
        onSuccess={() => {}}
      />
    )
    
    expect(screen.getByText(/create company/i)).toBeInTheDocument()
  })

  it('does not render when closed', () => {
    render(
      <CreateCompanyModal
        isOpen={false}
        onClose={() => {}}
        onSuccess={() => {}}
      />
    )
    
    expect(screen.queryByText(/create company/i)).not.toBeInTheDocument()
  })

  it('validates required fields', async () => {
    const user = userEvent.setup()
    render(
      <CreateCompanyModal
        isOpen={true}
        onClose={() => {}}
        onSuccess={() => {}}
      />
    )
    
    const submitButton = screen.getByRole('button', { name: /create/i })
    await user.click(submitButton)
    
    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText(/legal name is required/i)).toBeInTheDocument()
    })
  })

  it('submits form with valid data', async () => {
    const user = userEvent.setup()
    const onSuccess = vi.fn()
    const api = await import('../../services/api')
    
    vi.mocked(api.default.post).mockResolvedValue({
      data: { id: '1', legal_name: 'Test Company' },
    })
    
    render(
      <CreateCompanyModal
        isOpen={true}
        onClose={() => {}}
        onSuccess={onSuccess}
      />
    )
    
    const nameInput = screen.getByLabelText(/legal name/i)
    await user.type(nameInput, 'Test Company')
    
    const submitButton = screen.getByRole('button', { name: /create/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(api.default.post).toHaveBeenCalled()
      expect(onSuccess).toHaveBeenCalled()
    })
  })
})

