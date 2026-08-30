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
      <div className="mx-auto max-w-3xl">
        <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Your identity</p>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">My credentials</h1>
        <p className="mt-2 text-sm text-slate-500">Verified credentials issued to your identity.</p>
        {credentials.length === 0 ? (
          <div className="mt-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
            <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-indigo-50 text-xl font-bold text-indigo-600">+</div>
            <h2 className="mt-5 font-bold text-slate-900">No credentials yet</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">Upload an identity document to create your first verified credential.</p>
          </div>
        ) : (
          <ul className="mt-4 space-y-2">
            {credentials.map(c => (
              <li key={c.id} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition hover:border-indigo-200 hover:shadow-md">{c.id}</li>
            ))}
          </ul>
        )}
      </div>
    </Layout>
  )
}
