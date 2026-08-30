import { useState } from 'react'
import Layout from '../../src/components/Layout'
import { uploadIdentity } from '../../src/api/api'

const MAX_FILE_SIZE = 10 * 1024 * 1024

export default function Upload() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<any>(null)
  const [step, setStep] = useState('Upload')

  const validateClientFile = (candidate: File) => {
    const allowed = ['.jpg', '.jpeg', '.png', '.pdf']
    const ext = candidate.name.slice(candidate.name.lastIndexOf('.')).toLowerCase()

    if (!allowed.includes(ext)) {
      throw new Error('Unsupported file type. Use JPG, JPEG, PNG, or PDF.')
    }

    if (candidate.size > MAX_FILE_SIZE) {
      throw new Error('The uploaded document exceeds the 10MB file limit.')
    }
  }

  const submit = async (e: any) => {
    e.preventDefault()
    setError(null)
    setResult(null)

    if (!file) {
      setStep('Upload')
      return setError('Please choose a file to continue.')
    }

    try {
      validateClientFile(file)
      setStep('Validation')
      setLoading(true)

      const fd = new FormData()
      fd.append('document_file', file)
      fd.append('document_type', 'CITIZENSHIP')

      const res = await uploadIdentity(fd)
      setStep('Verification complete')
      setResult(res)
    } catch (err: any) {
      const message = err?.data?.document_file?.[0] || err?.data?.error || err?.message || 'Upload failed'
      setStep('File validation failed')
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const steps = ['Upload', 'Validation', 'OCR', 'Identity verification', 'Success']

  return (
    <Layout>
      <div className="mx-auto max-w-2xl">
        <div className="mb-8">
          <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Identity verification</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">Upload your document</h1>
          <p className="mt-2 max-w-xl text-sm leading-6 text-slate-500">Submit a clear citizenship document. We will securely validate it and create your verified credential.</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <h2 className="text-lg font-bold text-slate-900">Document details</h2>

        <div className="mt-6 grid grid-cols-2 gap-2 text-xs font-semibold text-slate-500 sm:grid-cols-5">
          {steps.map((item) => (
            <div
              key={item}
              className={`rounded-lg px-3 py-2 text-center ${step === item || (item === 'Success' && result) ? 'bg-indigo-50 text-indigo-700' : 'bg-slate-100'}`}
            >
              {item}
            </div>
          ))}
        </div>

        <form className="mt-8" onSubmit={submit}>
          <label className="block text-sm font-semibold text-slate-700" htmlFor="identity-document">Choose a document</label>
          <input
            id="identity-document"
            type="file"
            accept="image/png,image/jpeg,.pdf"
            onChange={e => setFile(e.target.files?.[0] ?? null)}
            className="mt-2 block w-full cursor-pointer rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500 transition file:mr-4 file:rounded-lg file:border-0 file:bg-indigo-600 file:px-4 file:py-2 file:font-semibold file:text-white hover:border-indigo-300 hover:bg-indigo-50"
          />
          <p className="mt-2 text-xs text-slate-400">JPG, JPEG, PNG, or PDF up to 10MB.</p>

          {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

          <button type="submit" disabled={loading} className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">
            {loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" aria-hidden="true" />}
            {loading ? 'Processing document...' : 'Upload and verify'}
          </button>
        </form>

        {result && (
          <div className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
            <div className="font-semibold text-emerald-800">KYC status: {result.status || 'verified'}</div>
            <div className="mt-2 break-all text-sm text-emerald-700">Credential ID: {result.credential_id}</div>
          </div>
        )}
        </div>
      </div>
    </Layout>
  )
}
