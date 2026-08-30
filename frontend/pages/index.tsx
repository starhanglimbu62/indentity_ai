import Link from 'next/link'
import Layout from '../src/components/Layout'

export default function Home() {
  return (
    <Layout>
      <div className="mx-auto max-w-5xl py-10 sm:py-16">
        <section className="grid items-center gap-10 lg:grid-cols-[1.15fr_0.85fr]">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Trust, verified</p>
            <h1 className="mt-4 max-w-2xl text-4xl font-bold tracking-tight text-slate-950 sm:text-6xl">Your identity should work for you.</h1>
            <p className="mt-6 max-w-xl text-base leading-7 text-slate-500">IdentityAI lets you prove what matters without handing over everything else. Build a reusable, privacy-first digital identity.</p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link href="/register" className="rounded-lg bg-indigo-600 px-5 py-3 text-center font-semibold text-white shadow-sm transition hover:bg-indigo-700">Get started</Link>
              <Link href="/bank" className="rounded-lg border border-slate-300 bg-white px-5 py-3 text-center font-semibold text-slate-700 transition hover:border-indigo-300 hover:text-indigo-700">Open bank portal</Link>
            </div>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
            <div className="flex items-center justify-between border-b border-slate-100 pb-5">
              <span className="text-sm font-semibold text-slate-900">Identity status</span>
              <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">Protected</span>
            </div>
            <div className="py-8">
              <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-indigo-50 text-sm font-bold text-indigo-600">OK</div>
              <h2 className="mt-5 text-xl font-bold text-slate-900">Verified when needed</h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">Share only the verification result a bank needs, with your consent every time.</p>
            </div>
            <div className="grid grid-cols-2 gap-3 border-t border-slate-100 pt-5 text-sm"><div><p className="text-slate-400">Disclosure</p><p className="mt-1 font-semibold text-slate-900">Minimal</p></div><div><p className="text-slate-400">Control</p><p className="mt-1 font-semibold text-slate-900">Yours</p></div></div>
          </div>
        </section>
      </div>
    </Layout>
  )
}
