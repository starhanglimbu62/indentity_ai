import Layout from '../src/components/Layout'
import { useEffect, useState } from 'react'

export default function Credentials() {
  const [credentials, setCredentials] = useState<any[]>([])

  useEffect(() => {
    // backend endpoint missing; show empty state
    setCredentials([])
  }, [])

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <h2 className="text-xl font-semibold">My Credentials</h2>
        {credentials.length === 0 ? (
          <div className="mt-4 p-6 bg-white rounded shadow text-gray-600">No credentials found. Upload an identity document to get started.</div>
        ) : (
          <ul className="mt-4 space-y-2">
            {credentials.map(c => (
              <li key={c.id} className="p-4 bg-white rounded shadow">{c.id}</li>
            ))}
          </ul>
        )}
      </div>
    </Layout>
  )
}
