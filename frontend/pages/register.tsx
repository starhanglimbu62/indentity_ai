import { useState } from 'react'
import Layout from '../src/components/Layout'
import { register } from '../src/api/api'
import { useRouter } from 'next/router'

export default function Register() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const submit = async (e: any) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const res = await register({ username, password, email })
      // store token
      if (res && res.access) {
        localStorage.setItem('access', res.access)
        router.push('/dashboard')
      }
    } catch (err: any) {
      setError(err?.data || 'Registration failed')
    } finally { setLoading(false) }
  }

  return (
    <Layout>
      <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold">Register</h2>
        <form className="mt-4 space-y-3" onSubmit={submit}>
          <input required placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} className="w-full border px-3 py-2 rounded" />
          <input required placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} className="w-full border px-3 py-2 rounded" />
          <input required type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} className="w-full border px-3 py-2 rounded" />
          {error && <div className="text-red-600">{String(error)}</div>}
          <button disabled={loading} className="w-full bg-indigo-600 text-white py-2 rounded">{loading ? 'Creating...' : 'Register'}</button>
        </form>
      </div>
    </Layout>
  )
}
