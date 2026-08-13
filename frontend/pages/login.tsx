import { useState } from 'react'
import Layout from '../src/components/Layout'
import { useRouter } from 'next/router'
import { loginWithToken } from '../src/api/api'

export default function Login() {
  const [token, setToken] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const submit = async (e: any) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await loginWithToken(token)
      router.push('/dashboard')
    } catch (err: any) {
      setError('Invalid token')
    } finally { setLoading(false) }
  }

  return (
    <Layout>
      <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold">Login (Paste token)</h2>
        <form className="mt-4 space-y-3" onSubmit={submit}>
          <textarea required placeholder="Paste access token" value={token} onChange={e => setToken(e.target.value)} className="w-full border px-3 py-2 rounded h-24" />
          {error && <div className="text-red-600">{error}</div>}
          <button disabled={loading} className="w-full bg-indigo-600 text-white py-2 rounded">{loading ? 'Logging in...' : 'Login'}</button>
        </form>
      </div>
    </Layout>
  )
}
