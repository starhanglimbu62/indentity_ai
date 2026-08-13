import Link from 'next/link'
import Layout from '../src/components/Layout'

export default function Home() {
  return (
    <Layout>
      <div className="text-center py-12">
        <h1 className="text-3xl font-bold">IdentityAI</h1>
        <p className="mt-4 text-gray-600">Privacy-preserving identity verification platform prototype.</p>

        <div className="mt-8 flex items-center justify-center gap-4">
          <Link href="/register" className="px-4 py-2 bg-indigo-600 text-white rounded">Get Started</Link>
          <Link href="/bank" className="px-4 py-2 border rounded">Bank Portal</Link>
        </div>
      </div>
    </Layout>
  )
}
