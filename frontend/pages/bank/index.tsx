import Layout from '../../src/components/Layout'
import { useRouter } from 'next/router'
import { useEffect } from 'react'

export default function BankPortal() {
  const router = useRouter()

  useEffect(() => {
    const bank = typeof window !== 'undefined' ? sessionStorage.getItem('bank') : null
    if (bank) {
      router.push('/bank/dashboard')
    }
  }, [router])

  return (
    <Layout>
      <div className="mx-auto max-w-2xl space-y-8">
        <div className="rounded-xl border border-slate-200 bg-gradient-to-br from-indigo-50 to-blue-50 p-8 shadow-sm sm:p-12">
          <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Bank Portal</p>
          <h1 className="mt-3 text-3xl font-bold text-slate-900">IdentityAI Verification Platform</h1>
          <p className="mt-4 max-w-lg text-base leading-7 text-slate-600">
            Request privacy-preserving identity verification from your customers. They prove eligibility without revealing personal details.
          </p>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <button
              onClick={() => router.push('/bank/login')}
              className="rounded-lg bg-indigo-600 px-6 py-3 font-semibold text-white transition hover:bg-indigo-700"
            >
              Sign in to bank account
            </button>
            <button
              onClick={() => router.push('/')}
              className="rounded-lg border border-slate-300 px-6 py-3 font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              Learn more
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {[
            {
              title: 'Privacy-Preserving',
              description: 'Users prove eligibility without revealing personal data'
            },
            {
              title: 'Zero-Knowledge Proofs',
              description: 'Cryptographic verification ensures authenticity'
            },
            {
              title: 'Minimal Disclosure',
              description: 'You only receive the verification result'
            }
          ].map((feature) => (
            <div key={feature.title} className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold text-slate-900">{feature.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  )
}

