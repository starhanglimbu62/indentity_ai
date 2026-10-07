import Layout from '../../../src/components/Layout'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import api from '../../../src/api/api'

export default function BankRequestDetailPage() {
  const router = useRouter()
  const { id } = router.query
  const [request, setRequest] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const bankData = sessionStorage.getItem('bank')
      if (!bankData) router.push('/bank/login')
    }
  }, [router])

  useEffect(() => {
    const fetchRequest = async () => {
      if (!id) return
      try {
        const data = await api.getBankRequestDetail(String(id))
        setRequest(data)
      } catch (err) {
        setError('Failed to load request')
      } finally {
        setLoading(false)
      }
    }

    if (id && typeof window !== 'undefined' && sessionStorage.getItem('bank')) {
      fetchRequest()
    }
  }, [id])

  if (loading) {
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

  if (error) {
    return (
      <Layout>
        <div className="mx-auto max-w-2xl rounded-xl border border-red-200 bg-red-50 p-6 shadow-sm">
          <p className="text-red-700">{error}</p>
          <button
            onClick={() => router.push('/bank/dashboard')}
            className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 font-semibold text-white transition hover:bg-indigo-700"
          >
            Back to dashboard
          </button>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="mx-auto max-w-2xl space-y-6">
        <button
          onClick={() => router.push('/bank/dashboard')}
          className="text-sm font-semibold text-indigo-600 hover:text-indigo-700"
        >
          ← Back to dashboard
        </button>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Verification Request</p>
          <h1 className="mt-2 text-2xl font-bold text-slate-900">{request?.user?.name}</h1>

          <div className="mt-6 space-y-4">
            <div className="rounded-lg bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-600">User</p>
              <p className="mt-2 font-semibold text-slate-900">{request?.user?.name}</p>
              <p className="text-sm text-slate-600">{request?.user?.email}</p>
            </div>

            <div className="rounded-lg bg-indigo-50 border border-indigo-200 p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-indigo-600">Claim</p>
              <p className="mt-2 font-semibold text-indigo-900">{request?.claim}</p>
            </div>

            <div className={`rounded-lg border p-4 ${
              request?.status === 'VERIFIED' ? 'bg-emerald-50 border-emerald-200' :
              request?.status === 'PENDING' ? 'bg-amber-50 border-amber-200' :
              request?.status === 'APPROVED' ? 'bg-blue-50 border-blue-200' :
              request?.status === 'DENIED' ? 'bg-red-50 border-red-200' :
              'bg-slate-50 border-slate-200'
            }`}>
              <p className={`text-xs font-semibold uppercase tracking-wider ${
                request?.status === 'VERIFIED' ? 'text-emerald-600' :
                request?.status === 'PENDING' ? 'text-amber-600' :
                request?.status === 'APPROVED' ? 'text-blue-600' :
                request?.status === 'DENIED' ? 'text-red-600' :
                'text-slate-600'
              }`}>
                Status
              </p>
              <div className="mt-2 flex items-center gap-3">
                <div className={`inline-flex rounded-full px-3 py-1 text-sm font-semibold ${
                  request?.status === 'VERIFIED' ? 'bg-emerald-100 text-emerald-800' :
                  request?.status === 'PENDING' ? 'bg-amber-100 text-amber-800' :
                  request?.status === 'APPROVED' ? 'bg-blue-100 text-blue-800' :
                  request?.status === 'DENIED' ? 'bg-red-100 text-red-800' :
                  'bg-slate-100 text-slate-800'
                }`}>
                  {request?.status}
                </div>
              </div>
            </div>

            {request?.status === 'VERIFIED' && (
              <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
                <p className="flex items-center gap-2 text-sm font-semibold text-emerald-900">
                  <span className="text-lg">✓</span>
                  Verification Successful
                </p>
                <div className="mt-3 space-y-2 text-sm text-emerald-800">
                  <div className="flex justify-between gap-4">
                    <span>Verified at:</span>
                    <span className="font-mono text-xs">
                      {request?.verified_at ? new Date(request.verified_at).toLocaleString() : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between gap-4">
                    <span>Verification ID:</span>
                    <span className="font-mono text-xs">{request?.id}</span>
                  </div>
                </div>
                <p className="mt-3 text-xs text-emerald-700">
                  The user has proven they meet the verification criteria without revealing personal details.
                </p>
              </div>
            )}

            {request?.status === 'DENIED' && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4">
                <p className="flex items-center gap-2 text-sm font-semibold text-red-900">
                  <span className="text-lg">✕</span>
                  Request Denied
                </p>
                <p className="mt-2 text-sm text-red-800">
                  The user declined to verify the requested claim.
                </p>
              </div>
            )}

            {request?.status === 'PENDING' && (
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
                <p className="text-sm font-semibold text-amber-900">
                  Awaiting user response
                </p>
                <p className="mt-2 text-sm text-amber-800">
                  The verification request has been sent to the user. We&apos;ll update this page as soon as they respond.
                </p>
              </div>
            )}

            {request?.status === 'APPROVED' && (
              <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
                <p className="text-sm font-semibold text-blue-900">
                  User approved - Verification in progress
                </p>
                <p className="mt-2 text-sm text-blue-800">
                  The user has approved the verification. Generating and verifying zero-knowledge proof...
                </p>
              </div>
            )}

            <div className="mt-6 space-y-2 rounded-lg bg-slate-50 p-4">
              <p className="text-sm font-semibold text-slate-900">Request Details</p>
              <div className="space-y-1 text-xs text-slate-600">
                <div className="flex justify-between">
                  <span>Created:</span>
                  <span>{new Date(request?.created_at).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Bank:</span>
                  <span>{request?.bank?.name} ({request?.bank?.code})</span>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={() => router.push('/bank/dashboard')}
            className="mt-6 w-full rounded-lg border border-slate-300 px-4 py-3 font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Back to dashboard
          </button>
        </div>
      </div>
    </Layout>
  )
}
