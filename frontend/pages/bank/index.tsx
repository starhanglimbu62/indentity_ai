import Layout from '../../src/components/Layout'
import { useState } from 'react'
import { createVerificationRequest } from '../../src/api/api'

export default function BankPortal() {
  const [bankCode, setBankCode] = useState('')
  const [userId, setUserId] = useState('')
  const [claim, setClaim] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const submit = async (e: any) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const res = await createVerificationRequest({ bank_code: bankCode, user_id: userId, claim })
      setResult(res)
    } catch (err: any) {
      setError(err?.data || 'Request failed')
    } finally { setLoading(false) }
  }

  return (
    <Layout>
      <div className="mx-auto max-w-xl rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Bank workspace</p>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">Create a verification request</h1>
        <p className="mt-2 text-sm leading-6 text-slate-500">Request a specific claim while keeping the user&apos;s raw identity data private.</p>
        <form className="mt-8 space-y-5" onSubmit={submit}>
          <label className="block text-sm font-semibold text-slate-700">Bank code<input value={bankCode} onChange={e => setBankCode(e.target.value)} placeholder="Example Bank" className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-3 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100" /></label>
          <label className="block text-sm font-semibold text-slate-700">User ID<input value={userId} onChange={e => setUserId(e.target.value)} placeholder="User UUID" className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-3 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100" /></label>
          <label className="block text-sm font-semibold text-slate-700">Claim<input value={claim} onChange={e => setClaim(e.target.value)} placeholder="AGE_OVER_18" className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-3 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100" /></label>
          {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{String(error)}</div>}
          <button disabled={loading} className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">{loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" aria-hidden="true" />}{loading ? 'Creating request...' : 'Create verification request'}</button>
        </form>

        {result && (
          <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
            <div className="font-semibold">Request created.</div>
            <div className="mt-2 break-all font-mono text-xs">{JSON.stringify(result)}</div>
          </div>
        )}
      </div>
    </Layout>
  )
}
