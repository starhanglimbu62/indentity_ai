import Link from 'next/link'
import { useRouter } from 'next/router'
import { useAuth } from '../hooks/useAuth'

export default function NavBar() {
  const { token, setToken } = useAuth()
  const router = useRouter()

  const links = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/credentials', label: 'Credentials' },
    { href: '/requests', label: 'Requests' },
  ]

  return (
    <nav className="sticky top-0 z-10 border-b border-slate-200/80 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex min-w-0 items-center gap-6">
          <Link href="/" className="flex items-center gap-2 text-lg font-bold tracking-tight text-slate-950">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-sm text-white">I</span>
            <span>IdentityAI</span>
          </Link>
          {token && (
            <div className="hidden items-center gap-1 md:flex">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`rounded-lg px-3 py-2 text-sm font-medium transition ${router.pathname.startsWith(link.href) ? 'bg-indigo-50 text-indigo-700' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'}`}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          )}
        </div>
        <div className="flex shrink-0 items-center gap-3">
          {token ? (
            <button className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-700" onClick={() => setToken(null)}>Log out</button>
          ) : (
            <>
              <Link href="/login" className="hidden text-sm font-medium text-slate-600 hover:text-slate-950 sm:block">Log in</Link>
              <Link href="/register" className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700">Create account</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
