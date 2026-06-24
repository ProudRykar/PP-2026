import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import type { Curator } from '../types'
import { fetchMe, login as apiLogin, register as apiRegister } from '../api'

interface AuthState {
  token: string | null
  curator: Curator | null
  loading: boolean
  login: (login: string, password: string) => Promise<void>
  register: (full_name: string, login: string, email: string, password: string, role?: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthState | null>(null)

const TOKEN_KEY = 'auth_token'

function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

function storeToken(token: string | null) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(getStoredToken)
  const [curator, setCurator] = useState<Curator | null>(null)
  const [loading, setLoading] = useState(true)

  console.debug('[Auth] render:', { token: !!token, curator: !!curator, loading })

  const logout = useCallback(() => {
    setToken(null)
    setCurator(null)
    storeToken(null)
  }, [])

  useEffect(() => {
    console.debug('[Auth] useEffect([token]) fired:', { token: !!token })
    if (!token) {
      setLoading(false)
      return
    }
    fetchMe()
      .then(res => {
        console.debug('[Auth] fetchMe ok:', { curator: res.curator?.full_name })
        setCurator(res.curator)
      })
      .catch((err) => {
        console.debug('[Auth] fetchMe failed:', err)
        storeToken(null)
        setToken(null)
      })
      .finally(() => setLoading(false))
  }, [token])

  const login = useCallback(async (login: string, password: string) => {
    console.debug('[Auth] login() called')
    const res = await apiLogin(login, password)
    console.debug('[Auth] login ok:', { curator: res.curator?.full_name })
    storeToken(res.token)
    setToken(res.token)
    setCurator(res.curator)
  }, [])

  const register = useCallback(async (
    full_name: string,
    login: string,
    email: string,
    password: string,
    role?: string,
  ) => {
    const res = await apiRegister(full_name, login, email, password, role)
    storeToken(res.token)
    setToken(res.token)
    setCurator(res.curator)
  }, [])

  return (
    <AuthContext.Provider value={{
      token,
      curator,
      loading,
      login,
      register,
      logout,
      isAuthenticated: !!token && !!curator,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
