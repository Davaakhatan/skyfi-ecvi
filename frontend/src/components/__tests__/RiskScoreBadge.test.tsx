import { describe, it, expect } from 'vitest'
import { render, screen } from '../../test/utils/test-utils'
import RiskScoreBadge from '../RiskScoreBadge'

describe('RiskScoreBadge', () => {
  it('renders low risk badge correctly', () => {
    render(<RiskScoreBadge score={20} category="LOW" />)
    const badge = screen.getByText('20')
    expect(badge).toBeInTheDocument()
  })

  it('renders medium risk badge correctly', () => {
    render(<RiskScoreBadge score={50} category="MEDIUM" />)
    const badge = screen.getByText('50')
    expect(badge).toBeInTheDocument()
  })

  it('renders high risk badge correctly', () => {
    render(<RiskScoreBadge score={80} category="HIGH" />)
    const badge = screen.getByText('80')
    expect(badge).toBeInTheDocument()
  })

  it('displays correct risk category', () => {
    render(<RiskScoreBadge score={75} category="HIGH" />)
    // The component displays category in lowercase
    const category = screen.getByText('high')
    expect(category).toBeInTheDocument()
  })
})

