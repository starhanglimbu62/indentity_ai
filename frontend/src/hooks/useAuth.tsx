import React, { createContext, useContext, useEffect, useState } from 'react'

type AuthContextType = {
  token: string | null
  setToken: (t: string | null) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [token, setTokenState] = useState<string | null>(null)

  useEffect(() => {
    const t = sessionStorage.getItem('access')
    if (t) setTokenState(t)
  }, [])

  const setToken = (t: string | null) => {
    if (t) sessionStorage.setItem('access', t)
    else sessionStorage.removeItem('access')
    setTokenState(t)
  }

  return (
    <AuthContext.Provider value={{ token, setToken }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
