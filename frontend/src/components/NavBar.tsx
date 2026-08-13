import Link from 'next/link'
import { useAuth } from '../hooks/useAuth'

export default function NavBar() {
  const { token, setToken } = useAuth()

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-4xl mx-auto px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/" className="font-bold">IdentityAI</Link>
          <Link href="/dashboard" className="text-sm text-gray-600">Dashboard</Link>
        </div>
        <div className="flex items-center gap-3">
          {token ? (
            <button className="text-sm text-red-600" onClick={() => setToken(null)}>Logout</button>
          ) : (
            <>
              <Link href="/login" className="text-sm">Login</Link>
              <Link href="/register" className="text-sm">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
