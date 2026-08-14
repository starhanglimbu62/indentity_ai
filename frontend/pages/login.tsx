import { useState } from 'react'
import Layout from '../src/components/Layout'
import { useRouter } from 'next/router'
import { login } from '../src/api/api'
import { useAuth } from '../src/hooks/useAuth'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()
  const { setToken } = useAuth()

  const submit = async (e: any) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const resp: any = await login({ username, password })
      if (resp && resp.access) {
        setToken(resp.access)
        router.push('/dashboard')
      } else {
        setError('Login failed')
      }
    } catch (err: any) {
      setError('Invalid credentials')
    } finally { setLoading(false) }
  }

  return (
    <Layout>
      <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold">Login</h2>
        <form className="mt-4 space-y-3" onSubmit={submit}>
          <input required placeholder="Username or email" value={username} onChange={e => setUsername(e.target.value)} className="w-full border px-3 py-2 rounded" />
          <input required type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} className="w-full border px-3 py-2 rounded" />
          {error && <div className="text-red-600">{error}</div>}
          <button disabled={loading} className="w-full bg-indigo-600 text-white py-2 rounded">{loading ? 'Logging in...' : 'Login'}</button>
        </form>
      </div>
    </Layout>
  )
}
