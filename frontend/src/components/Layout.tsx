import React from 'react'
import NavBar from './NavBar'

export const Layout: React.FC<React.PropsWithChildren> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col">
      <NavBar />
      <main className="flex-1 w-full max-w-6xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </main>
      <footer className="px-4 py-6 text-center text-xs text-slate-400 sm:px-6">
        Privacy-first identity verification
      </footer>
    </div>
  )
}

export default Layout
