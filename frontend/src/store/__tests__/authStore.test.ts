import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore } from '../authStore'

describe('authStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
    })
  })

  it('initializes with no user', () => {
    const state = useAuthStore.getState()
    expect(state.user).toBeNull()
    expect(state.isAuthenticated).toBe(false)
  })

  it('sets user and token on login', () => {
    const user = {
      id: '1',
      email: 'test@example.com',
      username: 'testuser',
      role: 'operator' as const,
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
    }
    const token = 'test-token'

    useAuthStore.getState().setUser(user, token)

    const state = useAuthStore.getState()
    expect(state.user).toEqual(user)
    expect(state.token).toBe(token)
    expect(state.isAuthenticated).toBe(true)
  })

  it('clears user and token on logout', () => {
    // First login
    const user = {
      id: '1',
      email: 'test@example.com',
      username: 'testuser',
      role: 'operator' as const,
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
    }
    useAuthStore.getState().setUser(user, 'token')

    // Then logout
    useAuthStore.getState().logout()

    const state = useAuthStore.getState()
    expect(state.user).toBeNull()
    expect(state.token).toBeNull()
    expect(state.isAuthenticated).toBe(false)
  })
})

