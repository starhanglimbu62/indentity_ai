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
      <div className="max-w-xl mx-auto bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold">Upload Identity Document</h2>

        <div className="mt-4 flex flex-wrap gap-2 text-xs font-medium text-gray-600">
          {steps.map((item) => (
            <span
              key={item}
              className={`px-2 py-1 rounded ${step === item || (item === 'Success' && result) ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100'}`}
            >
              {item}
            </span>
          ))}
        </div>

        <form className="mt-4" onSubmit={submit}>
          <input
            type="file"
            accept="image/png,image/jpeg,.pdf"
            onChange={e => setFile(e.target.files?.[0] ?? null)}
            className="w-full border rounded p-2"
          />

          {error && <div className="text-red-600 mt-2">{error}</div>}

          <button disabled={loading} className="mt-4 w-full bg-indigo-600 text-white py-2 rounded disabled:opacity-60">
            {loading ? 'Processing document...' : 'Upload and Verify'}
          </button>
        </form>

        {result && (
          <div className="mt-4 p-4 bg-green-50 rounded">
            <div className="font-semibold text-green-700">KYC status: {result.status || 'verified'}</div>
            <div className="mt-1">Credential ID: {result.credential_id}</div>
          </div>
        )}
      </div>
    </Layout>
  )
}
