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
      <div className="mx-auto max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Welcome back</p>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">Log in to IdentityAI</h1>
        <p className="mt-2 text-sm text-slate-500">Access your verified identity workspace.</p>
        <form className="mt-8 space-y-5" onSubmit={submit}>
          <label className="block text-sm font-semibold text-slate-700">Username or email<input required placeholder="you@example.com" value={username} onChange={e => setUsername(e.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-3 font-normal outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100" /></label>
          <label className="block text-sm font-semibold text-slate-700">Password<input required type="password" placeholder="Enter your password" value={password} onChange={e => setPassword(e.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-3 font-normal outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100" /></label>
          {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
          <button disabled={loading} className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">{loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" aria-hidden="true" />}{loading ? 'Logging in...' : 'Log in'}</button>
        </form>
      </div>
    </Layout>
  )
}
