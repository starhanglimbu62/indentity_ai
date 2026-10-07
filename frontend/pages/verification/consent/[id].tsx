import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'
import Layout from '../../../src/components/Layout'
import api from '../../../src/api/api'

export default function ConsentPage() {
  const router = useRouter()
  const { id } = router.query
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [request, setRequest] = useState<any>(null)
  const [fetching, setFetching] = useState(true)

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const t = sessionStorage.getItem('access')
      if (!t) router.push('/login')
    }
  }, [router])

  useEffect(() => {
    const fetchRequest = async () => {
      if (!id) return
      try {
        const data = await api.getVerificationRequest(String(id))
        setRequest(data)
      } catch (err: any) {
        setError('Failed to load request')
      } finally {
        setFetching(false)
      }
    }

    if (id && typeof window !== 'undefined' && sessionStorage.getItem('access')) {
      fetchRequest()
    }
  }, [id])

  const submit = async (approved: boolean) => {
    if (!id) return
    setLoading(true)
    setError(null)
    try {
      await api.consentRequest(String(id), approved)
      setSuccess(true)
      setTimeout(() => {
        router.push('/dashboard')
      }, 2000)
    } catch (err: any) {
      setError(err?.data?.error || (approved ? 'Consent failed' : 'Denial failed'))
    } finally {
      setLoading(false)
    }
  }

  if (fetching) {
    return (
      <Layout>
        <div className="mx-auto max-w-2xl rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <div className="flex items-center justify-center gap-2">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-indigo-600" />
            <p className="text-slate-600">Loading request...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="mx-auto max-w-2xl">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Your approval</p>
          <h1 className="mt-2 text-2xl font-bold text-slate-900">Consent to verification</h1>
          <p className="mt-3 text-sm leading-6 text-slate-500">A bank is requesting identity verification. Review the details below before deciding.</p>

          {request && (
            <div className="mt-8 space-y-6">
              <div className="rounded-lg bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-600">Requesting bank</p>
                <p className="mt-2 text-lg font-semibold text-slate-900">{request.bank?.name}</p>
              </div>

              <div className="rounded-lg bg-indigo-50 border border-indigo-200 p-4">
                <p className="text-xs font-semibold uppercase tracking-wider text-indigo-600">Requested claim</p>
                <p className="mt-2 text-lg font-semibold text-indigo-900">{request.claim}</p>
                <p className="mt-2 text-sm text-indigo-700">The bank wants to verify that you are over 18 years old.</p>
              </div>

              <div className="space-y-4">
                <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
                  <p className="text-sm font-semibold text-emerald-900 flex items-center gap-2">
                    <span className="text-lg">✓</span>
                    What the bank WILL receive
                  </p>
                  <ul className="mt-3 space-y-2 text-sm text-emerald-800">
                    <li>• Verification status (VERIFIED or DENIED)</li>
                    <li>• Claim (AGE_OVER_18)</li>
                    <li>• Verification ID</li>
                    <li>• Timestamp of verification</li>
                  </ul>
                </div>

                <div className="rounded-lg border border-red-200 bg-red-50 p-4">
                  <p className="text-sm font-semibold text-red-900 flex items-center gap-2">
                    <span className="text-lg">✕</span>
                    What the bank will NOT receive
                  </p>
                  <ul className="mt-3 space-y-2 text-sm text-red-800">
                    <li>• Your date of birth</li>
                    <li>• National ID number</li>
                    <li>• Identity document or images</li>
                    <li>• Raw credential data</li>
                    <li>• Your address or personal details</li>
                  </ul>
                </div>
              </div>

              {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              {success ? (
                <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 font-semibold text-emerald-800">
                  ✓ Your decision has been recorded. Redirecting to dashboard...
                </div>
              ) : (
                <div className="mt-6 flex gap-3">
                  <button
                    disabled={loading}
                    onClick={() => submit(true)}
                    className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" aria-hidden="true" />}
                    {loading ? 'Processing...' : 'Allow verification'}
                  </button>
                  <button
                    disabled={loading}
                    onClick={() => submit(false)}
                    className="flex-1 rounded-lg border border-slate-300 px-4 py-3 font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    Deny
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

