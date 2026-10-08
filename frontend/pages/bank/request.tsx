import Layout from '../../src/components/Layout'
import { useCallback, useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import api from '../../src/api/api'

export default function BankRequestPage() {
  const router = useRouter()
  const [bank, setBank] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [users, setUsers] = useState<any[]>([])
  const [selectedUserId, setSelectedUserId] = useState<string>('')
  const [claim, setClaim] = useState('AGE_OVER_18')
  const [success, setSuccess] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const bankData = sessionStorage.getItem('bank')
      if (!bankData) router.push('/bank/login')
      else setBank(JSON.parse(bankData))
    }
  }, [router])

  const searchUsers = useCallback(async () => {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      setUsers([])
      return
    }

    try {
      setError(null)
      const data = await api.searchUsers(searchQuery) as any[]
      setUsers(data)
    } catch (err) {
      setError('Failed to search users')
    }
  }, [searchQuery])

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery.length >= 2) {
        searchUsers()
      }
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery, searchUsers])

  const submit = async (e: any) => {
    e.preventDefault()
    if (!selectedUserId || !claim) {
      setError('Please select a user and claim')
      return
    }

    setError(null)
    setLoading(true)

    try {
      const result = await api.createVerificationRequest({
        bank_code: bank.bank_code,
        user_id: selectedUserId,
        claim: claim
      }) as any
      setSuccess(true)
      setSuccessMessage(`Request created: ${result.id}`)
      setTimeout(() => {
        router.push('/bank/dashboard')
      }, 2000)
    } catch (err: any) {
      setError(err?.data?.error || 'Request creation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout>
      <div className="mx-auto max-w-2xl">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Bank Portal</p>
          <h1 className="mt-2 text-2xl font-bold text-slate-900">Create verification request</h1>
          <p className="mt-3 text-sm leading-6 text-slate-500">Request a specific claim while keeping the user&apos;s raw identity data private.</p>

          <form className="mt-8 space-y-6" onSubmit={submit}>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Select a user
              </label>
              <input
                type="text"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="Search by name, email, or username..."
                className="w-full rounded-lg border border-slate-300 px-3 py-3 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100"
              />

              {searchQuery.length > 0 && users.length === 0 && (
                <div className="mt-2 text-sm text-slate-500">No users found</div>
              )}

              {users.length > 0 && (
                <div className="mt-2 space-y-1 max-h-64 overflow-y-auto border border-slate-300 rounded-lg bg-white">
                  {users.map((user) => (
                    <button
                      key={user.id}
                      type="button"
                      onClick={() => {
                        setSelectedUserId(user.id)
                        setSearchQuery('')
                        setUsers([])
                      }}
                      className="w-full text-left px-4 py-3 hover:bg-indigo-50 transition"
                    >
                      <div className="font-semibold text-slate-900">Account ID</div>
                      <div className="break-all font-mono text-xs text-slate-500">{user.id}</div>
                    </button>
                  ))}
                </div>
              )}

              {selectedUserId && (
                <div className="mt-3 flex items-center justify-between rounded-lg border border-emerald-200 bg-emerald-50 p-3">
                  <div>
                    <p className="font-semibold text-emerald-900">
                      Selected account
                    </p>
                    <p className="break-all font-mono text-xs text-emerald-800">{selectedUserId}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectedUserId('')}
                    className="text-emerald-600 hover:text-emerald-700"
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Verification claim
              </label>
              <select
                value={claim}
                onChange={e => setClaim(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-3 outline-none transition focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100"
              >
                <option value="AGE_OVER_18">Age Over 18</option>
              </select>
              <p className="mt-2 text-xs text-slate-500">
                The user will be asked to verify that they are over 18 years old without revealing their date of birth.
              </p>
            </div>

            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {error}
              </div>
            )}

            {success && (
              <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
                <div className="font-semibold">✓ Request created successfully</div>
                <div className="mt-1 font-mono text-xs">{successMessage}</div>
                <p className="mt-2 text-xs">Redirecting to dashboard...</p>
              </div>
            )}

            <button
              disabled={loading || !selectedUserId || !claim}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" aria-hidden="true" />}
              {loading ? 'Creating request...' : 'Create request'}
            </button>
          </form>

          <button
            onClick={() => router.push('/bank/dashboard')}
            className="mt-4 w-full text-center text-sm text-indigo-600 hover:text-indigo-700"
          >
            ← Back to dashboard
          </button>
        </div>
      </div>
    </Layout>
  )
}
