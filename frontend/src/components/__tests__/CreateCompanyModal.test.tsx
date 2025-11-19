import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '../../test/utils/test-utils'
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
    
    // Check for the header text (there are multiple "Create Company" texts)
    expect(screen.getByRole('heading', { name: /create company/i })).toBeInTheDocument()
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
    const onSuccess = vi.fn()
    const api = await import('../../services/api')
    
    render(
      <CreateCompanyModal
        isOpen={true}
        onClose={() => {}}
        onSuccess={onSuccess}
      />
    )
    
    // Find the submit button
    const submitButton = screen.getByRole('button', { name: /create company/i })
    
    // Submit form without filling required field
    await user.click(submitButton)
    
    // Wait a bit for any async operations
    await waitFor(() => {
      // The API should not be called when validation fails
      expect(api.default.post).not.toHaveBeenCalled()
      // onSuccess should not be called
      expect(onSuccess).not.toHaveBeenCalled()
    }, { timeout: 1000 })
    
    // Verify the input field exists (form is still visible)
    const nameInput = screen.getByLabelText(/company name/i)
    expect(nameInput).toBeInTheDocument()
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
    
    const nameInput = screen.getByLabelText(/company name/i)
    await user.type(nameInput, 'Test Company')
    
    const submitButton = screen.getByRole('button', { name: /create/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(api.default.post).toHaveBeenCalled()
      expect(onSuccess).toHaveBeenCalled()
    })
  })
})

