import { describe, it, expect } from 'vitest'
import { render, screen } from '../../test/utils/test-utils'
import VerificationIndicator from '../VerificationIndicator'

describe('VerificationIndicator', () => {
  it('renders verified status correctly', () => {
    render(<VerificationIndicator status="verified" label="Verified" />)
    expect(screen.getByText('Verified')).toBeInTheDocument()
  })

  it('renders partial status correctly', () => {
    render(<VerificationIndicator status="partial" label="Partial" />)
    expect(screen.getByText('Partial')).toBeInTheDocument()
  })

  it('renders discrepancy status correctly', () => {
    render(<VerificationIndicator status="discrepancy" label="Discrepancy" />)
    expect(screen.getByText('Discrepancy')).toBeInTheDocument()
  })

  it('renders with small size', () => {
    render(<VerificationIndicator status="verified" label="Test" size="sm" />)
    const indicator = screen.getByText('Test')
    expect(indicator).toBeInTheDocument()
  })
})

