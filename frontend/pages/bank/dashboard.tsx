import Layout from '../../src/components/Layout'
import { useCallback, useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import api from '../../src/api/api'

export default function BankDashboard() {
  const router = useRouter()
  const [bank, setBank] = useState<any>(null)
  const [requests, setRequests] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const bankData = sessionStorage.getItem('bank')
      if (!bankData) router.push('/bank/login')
      else setBank(JSON.parse(bankData))
    }
  }, [router])

  const fetchRequests = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getBankRequests() as any[]
      setRequests(data)
    } catch (err) {
      setError('Failed to fetch requests')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (bank) fetchRequests()
  }, [bank, fetchRequests])

  const handleLogout = () => {
    sessionStorage.removeItem('bank')
    sessionStorage.removeItem('bank_api_key')
    router.push('/bank/login')
  }

  return (
    <Layout>
      <div className="mx-auto max-w-6xl space-y-6">
        <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Bank Portal</p>
            <h1 className="mt-2 text-2xl font-bold text-slate-900">{bank?.name}</h1>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/bank/request')}
              className="rounded-lg bg-indigo-600 px-4 py-2 font-semibold text-white transition hover:bg-indigo-700"
            >
              + New Request
            </button>
            <button
              onClick={fetchRequests}
              disabled={loading}
              className="rounded-lg border border-slate-300 px-4 py-2 font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
            >
              {loading ? 'Refreshing...' : 'Refresh'}
            </button>
            <button
              onClick={handleLogout}
              className="rounded-lg border border-slate-300 px-4 py-2 font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              Sign out
            </button>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <h2 className="text-xl font-bold text-slate-900">Verification Requests</h2>
          <p className="mt-2 text-sm text-slate-500">Status and results of all verification requests</p>

          {loading && (
            <div className="mt-6 text-center">
              <div className="inline-flex h-8 w-8 animate-spin rounded-full border-2 border-slate-300 border-t-indigo-600" />
              <p className="mt-2 text-sm text-slate-600">Loading requests...</p>
            </div>
          )}

          {error && (
            <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          {!loading && requests.length === 0 && (
            <div className="mt-6 rounded-lg border border-slate-200 bg-slate-50 p-8 text-center">
              <p className="text-sm text-slate-600">No verification requests yet</p>
              <button
                onClick={() => router.push('/bank/request')}
                className="mt-4 inline-flex rounded-lg bg-indigo-600 px-4 py-2 font-semibold text-white transition hover:bg-indigo-700"
              >
                Create your first request
              </button>
            </div>
          )}

          {!loading && requests.length > 0 && (
            <div className="mt-6 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="px-4 py-3 text-left font-semibold text-slate-900">Request</th>
                    <th className="px-4 py-3 text-left font-semibold text-slate-900">Claim</th>
                    <th className="px-4 py-3 text-left font-semibold text-slate-900">Status</th>
                    <th className="px-4 py-3 text-left font-semibold text-slate-900">Created</th>
                    <th className="px-4 py-3 text-left font-semibold text-slate-900">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {requests.map((req) => (
                    <tr key={req.id} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="px-4 py-4">
                        <div className="font-mono text-xs text-slate-600">{req.id}</div>
                      </td>
                      <td className="px-4 py-4">
                        <code className="font-mono text-sm text-indigo-600">{req.claim}</code>
                      </td>
                      <td className="px-4 py-4">
                        <div className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                          req.status === 'VERIFIED' ? 'bg-emerald-100 text-emerald-800' :
                          req.status === 'PENDING' ? 'bg-amber-100 text-amber-800' :
                          req.status === 'APPROVED' ? 'bg-blue-100 text-blue-800' :
                          req.status === 'DENIED' ? 'bg-red-100 text-red-800' :
                          'bg-slate-100 text-slate-800'
                        }`}>
                          {req.status}
                        </div>
                      </td>
                      <td className="px-4 py-4 text-xs text-slate-500">
                        {new Date(req.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-4">
                        <button
                          onClick={() => router.push(`/bank/requests/${req.id}`)}
                          className="text-sm font-semibold text-indigo-600 hover:text-indigo-700"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
