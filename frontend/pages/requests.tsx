import Layout from '../src/components/Layout'
import { useState } from 'react'
import { useRouter } from 'next/router'

export default function Requests() {
  const [requestId, setRequestId] = useState('')
  const router = useRouter()

  return (
    <Layout>
      <div className="mx-auto max-w-xl rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Review access</p>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">Pending requests</h1>
        <p className="mt-3 text-sm leading-6 text-slate-500">Enter the request ID provided by a bank to review the verification request and give consent.</p>
        <div className="mt-8">
          <label className="block text-sm font-semibold text-slate-700">Request ID<input value={requestId} onChange={e => setRequestId(e.target.value)} placeholder="Paste request UUID" className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-3 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100" /></label>
          <div className="mt-3 flex gap-2">
            <button disabled={!requestId.trim()} onClick={() => router.push(`/verification/consent/${requestId}`)} className="rounded-lg bg-indigo-600 px-4 py-3 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50">Review request</button>
          </div>
        </div>
      </div>
    </Layout>
  )
}
