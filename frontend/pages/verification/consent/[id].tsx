import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'
import Layout from '../../../src/components/Layout'
import { consentRequest } from '../../../src/api/api'

export default function ConsentPage() {
  const router = useRouter()
  const { id } = router.query
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    // no-op
  }, [id])

  const submit = async () => {
    if (!id) return
    setLoading(true)
    setError(null)
    try {
      await consentRequest(String(id))
      setSuccess(true)
    } catch (err: any) {
      setError(err?.data || 'Consent failed')
    } finally { setLoading(false) }
  }

  return (
    <Layout>
      <div className="mx-auto max-w-xl">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Your approval</p>
          <h1 className="mt-2 text-2xl font-bold text-slate-900">Consent to verification</h1>
          <p className="mt-3 text-sm leading-6 text-slate-500">A bank is requesting a verification claim. Approve only if you recognize this request.</p>
          <div className="mt-6 rounded-lg bg-slate-50 p-4 text-sm text-slate-600">
            <span className="font-semibold text-slate-800">Request ID</span>
            <span className="mt-1 block break-all font-mono text-xs text-slate-500">{id}</span>
          </div>
          <div className="mt-6">
          {error && <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{String(error)}</div>}
          {success ? (
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 font-semibold text-emerald-800">Consent recorded successfully.</div>
          ) : (
            <button disabled={loading || !id} onClick={submit} className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">
              {loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" aria-hidden="true" />}
              {loading ? 'Recording consent...' : 'Approve request'}
            </button>
          )}
          </div>
        </div>
      </div>
    </Layout>
  )
}
