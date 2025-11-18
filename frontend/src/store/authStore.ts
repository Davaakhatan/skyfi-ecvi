import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { User, LoginResponse } from '../types/api'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: User, token: string) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: async (email: string, password: string) => {
        const response = await fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({ username: email, password }),
        })
        if (!response.ok) throw new Error('Login failed')
        const data: LoginResponse = await response.json()
        set({
          user: data.user,
          token: data.access_token,
          isAuthenticated: true,
        })
      },
      logout: () => {
        set({ user: null, token: null, isAuthenticated: false })
      },
      setUser: (user: User, token: string) => {
        set({ user, token, isAuthenticated: true })
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
)

