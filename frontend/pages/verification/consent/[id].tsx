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
      <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold">Consent to Verification</h2>
        <p className="mt-2 text-gray-600">Request ID: {id}</p>
        <div className="mt-4">
          {error && <div className="text-red-600">{String(error)}</div>}
          {success ? (
            <div className="p-4 bg-green-50 rounded">Consent recorded.</div>
          ) : (
            <button disabled={loading} onClick={submit} className="w-full bg-indigo-600 text-white py-2 rounded">{loading ? 'Processing...' : 'Give Consent'}</button>
          )}
        </div>
      </div>
    </Layout>
  )
}
