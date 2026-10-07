import Layout from '../../src/components/Layout'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import api from '../../src/api/api'

export default function Dashboard() {
  const router = useRouter()
  const [notifications, setNotifications] = useState<any[]>([])
  const [requests, setRequests] = useState<any[]>([])
  const [notificationsLoading, setNotificationsLoading] = useState(true)
  const [requestsLoading, setRequestsLoading] = useState(true)

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const t = sessionStorage.getItem('access')
      if (!t) router.push('/login')
    }
  }, [router])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const notifData = await api.getNotifications() as any[]
        setNotifications(notifData)
      } catch (err) {
        console.error('Failed to fetch notifications')
      } finally {
        setNotificationsLoading(false)
      }
    }

    if (typeof window !== 'undefined' && sessionStorage.getItem('access')) {
      fetchData()
    }
  }, [])

  useEffect(() => {
    const fetchRequests = async () => {
      try {
        const reqData = await api.getVerificationRequests() as any[]
        setRequests(reqData)
      } catch (err) {
        console.error('Failed to fetch requests')
      } finally {
        setRequestsLoading(false)
      }
    }

    if (typeof window !== 'undefined' && sessionStorage.getItem('access')) {
      fetchRequests()
    }
  }, [])

  const pendingNotifications = notifications.filter(n => !n.is_read).length
  const pendingRequests = requests.filter(r => r.status === 'PENDING').length

  return (
    <Layout>
      <div className="space-y-8">
        <section className="overflow-hidden rounded-xl bg-slate-950 px-6 py-8 text-white shadow-sm sm:px-8">
          <p className="text-sm font-semibold uppercase tracking-widest text-indigo-300">Identity workspace</p>
          <h1 className="mt-3 max-w-xl text-3xl font-bold tracking-tight sm:text-4xl">Your verified identity, in your hands.</h1>
          <p className="mt-3 max-w-lg text-sm leading-6 text-slate-300">Manage your credentials and approve privacy-preserving verification requests from one secure place.</p>
        </section>

        <section>
          <div className="flex items-end justify-between gap-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Quick actions</h2>
              <p className="mt-1 text-sm text-slate-500">Move your identity forward in a few clicks.</p>
            </div>
          </div>
          <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { title: 'Upload document', detail: 'Start your verification', href: '/identity/upload', accent: 'bg-indigo-50 text-indigo-700' },
              { title: 'My credentials', detail: 'View verified credentials', href: '/credentials', accent: 'bg-emerald-50 text-emerald-700' },
              { title: 'Notifications', detail: pendingNotifications > 0 ? `${pendingNotifications} new` : 'No new alerts', href: '/dashboard/notifications', accent: pendingNotifications > 0 ? 'bg-red-50 text-red-700' : 'bg-amber-50 text-amber-700' },
              { title: 'Bank portal', detail: 'Create a verification request', href: '/bank', accent: 'bg-slate-100 text-slate-700' },
            ].map((action) => (
              <button key={action.href} onClick={() => router.push(action.href)} className="group rounded-xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-md">
                <span className={`flex h-10 w-10 items-center justify-center rounded-lg text-lg font-bold ${action.accent}`}>+</span>
                <span className="mt-5 block font-semibold text-slate-900">{action.title}</span>
                <span className="mt-1 block text-sm text-slate-500">{action.detail}</span>
                <span className="mt-5 block text-sm font-semibold text-indigo-600 transition group-hover:text-indigo-700">Open <span aria-hidden="true">-&gt;</span></span>
              </button>
            ))}
          </div>
        </section>

        {!requestsLoading && requests.length > 0 && (
          <section>
            <div className="flex items-end justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold text-slate-900">Pending requests</h2>
                <p className="mt-1 text-sm text-slate-500">Banks requesting your verification</p>
              </div>
            </div>
            <div className="mt-5 space-y-3">
              {requests.filter(r => r.status === 'PENDING').slice(0, 3).map((req) => (
                <div key={req.id} className="rounded-lg border border-slate-200 bg-white p-4 hover:border-indigo-200 transition">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-semibold text-slate-900">{req.bank?.name}</p>
                      <p className="mt-1 text-sm text-slate-600">Claiming: <span className="font-mono text-indigo-600">{req.claim}</span></p>
                      <p className="mt-2 text-xs text-slate-500">
                        {new Date(req.created_at).toLocaleString()}
                      </p>
                    </div>
                    <button
                      onClick={() => router.push(`/verification/consent/${req.id}`)}
                      className="whitespace-nowrap rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700"
                    >
                      Review
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </Layout>
  )
}

