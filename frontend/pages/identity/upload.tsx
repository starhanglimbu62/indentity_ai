import { useState } from 'react'
import Layout from '../../src/components/Layout'
import { uploadIdentity } from '../../src/api/api'
import { useRouter } from 'next/router'

export default function Upload() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<any>(null)
  const router = useRouter()

  const submit = async (e: any) => {
    e.preventDefault()
    setError(null)
    if (!file) return setError('Please choose a file')
    setLoading(true)
    const fd = new FormData()
    fd.append('document_file', file)
    fd.append('document_type', 'CITIZENSHIP')
    try {
      const res = await uploadIdentity(fd)
      setResult(res)
    } catch (err: any) {
      setError(err?.data || 'Upload failed')
    } finally { setLoading(false) }
  }

  return (
    <Layout>
      <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold">Upload Identity Document</h2>
        <form className="mt-4" onSubmit={submit}>
          <input type="file" accept="image/*,.pdf" onChange={e => setFile(e.target.files?.[0] ?? null)} className="w-full" />
          {error && <div className="text-red-600 mt-2">{error}</div>}
          <button disabled={loading} className="mt-4 w-full bg-indigo-600 text-white py-2 rounded">{loading ? 'Uploading...' : 'Upload and Verify'}</button>
        </form>

        {result && (
          <div className="mt-4 p-4 bg-green-50 rounded">
            <div>Status: {result.status || 'verified'}</div>
            <div>Credential ID: {result.credential_id}</div>
          </div>
        )}
      </div>
    </Layout>
  )
}
