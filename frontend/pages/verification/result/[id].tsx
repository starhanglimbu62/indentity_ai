import { useRouter } from 'next/router'
import { useCallback, useEffect, useState } from 'react'
import Layout from '../../../src/components/Layout'
import api from '../../../src/api/api'

export default function ResultPage() {
  const router = useRouter()
  const { id } = router.query
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<any | null>(null)

  const fetchVerify = useCallback(async () => {
    if (!id) return
    setLoading(true)
    try {
      const request = await api.getVerificationRequest(String(id)) as any
      setResult({
        verified: request.status === 'VERIFIED',
        status: request.status,
        claim: request.claim,
        timestamp: request.verified_at,
        verification_id: request.id,
      })
    } catch (err: any) {
      setError(err?.data || 'Verification failed')
    } finally { setLoading(false) }
  }, [id])

  useEffect(() => { fetchVerify() }, [fetchVerify])

  const generateProof = async () => {
    if (!id) return
    setGenerating(true)
    setError(null)
    try {
      await api.generateProof(String(id))
      await fetchVerify()
    } catch (err: any) {
      setError(err?.data?.error || 'Proof generation failed')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <Layout>
      <div className="mx-auto max-w-xl">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Verification status</p>
          <h1 className="mt-2 text-2xl font-bold text-slate-900">Verification result</h1>
        {loading && <div className="mt-8 flex items-center gap-3 text-sm text-slate-500"><span className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />Loading verification status...</div>}
        {error && <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{String(error)}</div>}
        {result && (
          <div className="mt-6 space-y-3">
            <div className={`rounded-lg p-4 font-semibold ${result.verified ? 'border border-emerald-200 bg-emerald-50 text-emerald-800' : 'border border-amber-200 bg-amber-50 text-amber-800'}`}>
              {result.verified ? 'Prototype proof verified' : `Verification status: ${result.status}`}
            </div>
            {result.status === 'APPROVED' && (
              <div className="rounded-lg border border-indigo-200 bg-indigo-50 p-4">
                <p className="text-sm text-indigo-900">Your consent is recorded. Proof generation has not completed yet.</p>
                <button
                  type="button"
                  onClick={generateProof}
                  disabled={generating}
                  className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {generating ? 'Generating and verifying...' : 'Generate and verify proof'}
                </button>
              </div>
            )}
            {result.verified && (
              <p className="text-sm text-amber-800">
                Prototype limitation: the age proof is not cryptographically bound to the verified credential or its source date of birth. Do not use this result as production identity evidence.
              </p>
            )}
            {!result.verified && (
              <button
                type="button"
                onClick={fetchVerify}
                disabled={loading}
                className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 disabled:opacity-60"
              >
                {loading ? 'Refreshing...' : 'Refresh status'}
              </button>
            )}
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
