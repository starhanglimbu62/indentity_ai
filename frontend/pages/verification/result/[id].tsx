import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'
import Layout from '../../../src/components/Layout'
import { verifyRequest } from '../../../src/api/api'

export default function ResultPage() {
  const router = useRouter()
  const { id } = router.query
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<any | null>(null)

  const fetchVerify = async () => {
    if (!id) return
    setLoading(true)
    try {
      const res = await verifyRequest(String(id))
      setResult(res)
    } catch (err: any) {
      setError(err?.data || 'Verification failed')
    } finally { setLoading(false) }
  }

  useEffect(() => { fetchVerify() }, [id])

  return (
    <Layout>
      <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold">Verification Result</h2>
        {loading && <div className="mt-4">Processing...</div>}
        {error && <div className="mt-4 text-red-600">{String(error)}</div>}
        {result && (
          <div className="mt-4">
            <div>Verified: {String(result.verified)}</div>
            <div>Timestamp: {String(result.timestamp)}</div>
            <div>ID: {String(result.verification_id)}</div>
          </div>
        )}
      </div>
    </Layout>
  )
}
