import Layout from '../../src/components/Layout'
import { useState } from 'react'
import { useRouter } from 'next/router'
import api from '../../src/api/api'

export default function BankLoginPage() {
  const router = useRouter()
  const [bankCode, setBankCode] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const submit = async (e: any) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const result = await api.bankLogin({ bank_code: bankCode, api_key: apiKey })
      sessionStorage.setItem('bank', JSON.stringify(result))
      sessionStorage.setItem('bank_api_key', apiKey)
      router.push('/bank/dashboard')
    } catch (err: any) {
      setError(err?.data?.error || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout>
      <div className="mx-auto max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Bank Portal</p>
          <h1 className="mt-2 text-2xl font-bold text-slate-900">Sign in to your account</h1>
          <p className="mt-2 text-sm text-slate-500">Access the IdentityAI verification platform</p>
        </div>

        <form onSubmit={submit} className="mt-8 space-y-4">
          <label className="block text-sm font-semibold text-slate-700">
            Bank Code
            <input
              type="text"
              value={bankCode}
              onChange={e => setBankCode(e.target.value)}
              placeholder="e.g., BANK001"
              className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-3 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100"
              required
            />
          </label>

          <label className="block text-sm font-semibold text-slate-700">
            API Key
            <input
              type="password"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
              placeholder="Your API key"
              className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-3 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100"
              required
            />
          </label>

          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <button
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" aria-hidden="true" />}
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <p className="mt-2 text-sm text-slate-500">
          Don&apos;t have bank credentials? <button onClick={() => router.push('/')} className="font-semibold text-indigo-600 hover:text-indigo-700">Contact support</button>
        </p>
      </div>
    </Layout>
  )
}
