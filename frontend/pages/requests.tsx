import Layout from '../src/components/Layout'
import { useState } from 'react'
import { useRouter } from 'next/router'

export default function Requests() {
  const [requestId, setRequestId] = useState('')
  const router = useRouter()

  return (
    <Layout>
      <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold">Pending Requests</h2>
        <p className="mt-2 text-gray-600">If you have a request UUID (provided by a bank), paste it here to view and consent.</p>
        <div className="mt-4">
          <input value={requestId} onChange={e => setRequestId(e.target.value)} placeholder="Request UUID" className="w-full border px-3 py-2 rounded" />
          <div className="mt-3 flex gap-2">
            <button onClick={() => router.push(`/verification/consent/${requestId}`)} className="px-4 py-2 bg-indigo-600 text-white rounded">Open</button>
          </div>
        </div>
      </div>
    </Layout>
  )
}
