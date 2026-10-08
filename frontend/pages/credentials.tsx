import Layout from '../src/components/Layout'
import { useEffect, useState } from 'react'
import api from '../src/api/api'
import type { CredentialSummary } from '../src/api/api'

export default function Credentials() {
  const [credentials, setCredentials] = useState<CredentialSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.getCredentials()
      .then(setCredentials)
      .catch(() => setError('Failed to load credentials'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <Layout>
      <div className="mx-auto max-w-3xl">
        <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Your identity</p>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">My credentials</h1>
        <p className="mt-2 text-sm text-slate-500">Verified credentials issued to your identity.</p>
        {loading && <p className="mt-6 text-sm text-slate-500">Loading credentials...</p>}
        {error && <p role="alert" className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{String(error)}</p>}
        {!loading && !error && credentials.length === 0 ? (
          <div className="mt-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
            <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-indigo-50 text-xl font-bold text-indigo-600">+</div>
            <h2 className="mt-5 font-bold text-slate-900">No credentials yet</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">Upload an identity document to create your first verified credential.</p>
          </div>
        ) : !loading && !error && (
          <ul className="mt-4 space-y-3">
            {credentials.map((credential) => (
              <li key={credential.id} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h2 className="font-semibold text-slate-900">{credential.issuer}</h2>
                    <p className="mt-1 font-mono text-xs text-slate-500">{credential.id}</p>
                  </div>
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${credential.status === 'ACTIVE' && credential.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-700'}`}>
                    {credential.status}
                  </span>
                </div>
                <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-2">
                  <div><dt className="text-slate-500">Issued</dt><dd className="font-medium text-slate-800">{new Date(credential.issued_at).toLocaleDateString()}</dd></div>
                  <div><dt className="text-slate-500">Expires</dt><dd className="font-medium text-slate-800">{credential.expires_at ? new Date(credential.expires_at).toLocaleDateString() : 'No expiry set'}</dd></div>
                </dl>
              </li>
            ))}
          </ul>
        )}
      </div>
    </Layout>
  )
}
