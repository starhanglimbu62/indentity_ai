import Layout from '../../src/components/Layout'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'

export default function Dashboard() {
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    // read token to ensure logged in
    const t = localStorage.getItem('access')
    if (!t) router.push('/login')
  }, [])

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <h2 className="text-2xl font-semibold">Dashboard</h2>
        <p className="mt-4 text-gray-600">Quick actions</p>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <button onClick={() => router.push('/identity/upload')} className="p-4 bg-white rounded shadow">Upload identity document</button>
          <button onClick={() => router.push('/credentials')} className="p-4 bg-white rounded shadow">My credentials</button>
          <button onClick={() => router.push('/requests')} className="p-4 bg-white rounded shadow">Pending requests</button>
          <button onClick={() => router.push('/bank')} className="p-4 bg-white rounded shadow">Bank portal</button>
        </div>
      </div>
    </Layout>
  )
}
