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
      <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold">Bank Portal (Prototype)</h2>
        <form className="mt-4" onSubmit={submit}>
          <input value={bankCode} onChange={e => setBankCode(e.target.value)} placeholder="Bank code" className="w-full border px-3 py-2 rounded mb-2" />
          <input value={userId} onChange={e => setUserId(e.target.value)} placeholder="User ID" className="w-full border px-3 py-2 rounded mb-2" />
          <input value={claim} onChange={e => setClaim(e.target.value)} placeholder="Claim (e.g., age_over_18)" className="w-full border px-3 py-2 rounded mb-2" />
          {error && <div className="text-red-600">{error}</div>}
          <button disabled={loading} className="w-full bg-indigo-600 text-white py-2 rounded">{loading ? 'Creating...' : 'Create Verification Request'}</button>
        </form>

        {result && (
          <div className="mt-4 p-4 bg-green-50 rounded">
            <div>Request created.</div>
            <div className="break-all">{JSON.stringify(result)}</div>
          </div>
        )}
      </div>
    </Layout>
  )
}
