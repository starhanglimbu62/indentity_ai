import { useRouter } from 'next/router'
import { useCallback, useEffect, useState } from 'react'
import Layout from '../../../src/components/Layout'
import { verifyRequest } from '../../../src/api/api'

export default function ResultPage() {
  const router = useRouter()
  const { id } = router.query
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<any | null>(null)

  const fetchVerify = useCallback(async () => {
    if (!id) return
    setLoading(true)
    try {
      const res = await verifyRequest(String(id), null, null)
      setResult(res)
    } catch (err: any) {
      setError(err?.data || 'Verification failed')
    } finally { setLoading(false) }
  }, [id])

  useEffect(() => { fetchVerify() }, [fetchVerify])

  return (
    <Layout>
      <div className="mx-auto max-w-xl">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Verification status</p>
          <h1 className="mt-2 text-2xl font-bold text-slate-900">Verification result</h1>
        {loading && <div className="mt-8 flex items-center gap-3 text-sm text-slate-500"><span className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />Checking your proof...</div>}
        {error && <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{String(error)}</div>}
        {result && (
          <div className="mt-6 space-y-3">
            <div className={`rounded-lg p-4 font-semibold ${result.verified ? 'border border-emerald-200 bg-emerald-50 text-emerald-800' : 'border border-amber-200 bg-amber-50 text-amber-800'}`}>
              {result.verified ? 'Identity verified' : 'Verification not completed'}
            </div>
            <dl className="divide-y divide-slate-100 rounded-lg border border-slate-200 text-sm">
              <div className="flex flex-col gap-1 px-4 py-3 sm:flex-row sm:justify-between"><dt className="text-slate-500">Verified</dt><dd className="font-medium text-slate-900">{String(result.verified)}</dd></div>
              <div className="flex flex-col gap-1 px-4 py-3 sm:flex-row sm:justify-between"><dt className="text-slate-500">Timestamp</dt><dd className="break-all font-medium text-slate-900 sm:text-right">{String(result.timestamp)}</dd></div>
              <div className="flex flex-col gap-1 px-4 py-3 sm:flex-row sm:justify-between"><dt className="text-slate-500">Verification ID</dt><dd className="break-all font-mono text-xs text-slate-700 sm:text-right">{String(result.verification_id)}</dd></div>
            </dl>
          </div>
        )}
        </div>
      </div>
    </Layout>
  )
}
