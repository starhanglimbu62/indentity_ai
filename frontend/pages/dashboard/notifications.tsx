import Layout from '../../src/components/Layout'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import api from '../../src/api/api'

export default function NotificationsPage() {
  const router = useRouter()
  const [notifications, setNotifications] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const t = sessionStorage.getItem('access')
      if (!t) router.push('/login')
    }
  }, [router])

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const data = await api.getNotifications() as any[]
        setNotifications(data)
      } catch (err: any) {
        setError(err?.data || 'Failed to fetch notifications')
      } finally {
        setLoading(false)
      }
    }

    if (typeof window !== 'undefined' && sessionStorage.getItem('access')) {
      fetchNotifications()
    }
  }, [])

  return (
    <Layout>
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <h1 className="text-2xl font-bold text-slate-900">Notifications</h1>
          <p className="mt-2 text-sm text-slate-500">Stay informed about verification requests and results</p>
        </div>

        {loading && (
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-8 text-center">
            <div className="inline-flex h-8 w-8 animate-spin rounded-full border-2 border-slate-300 border-t-indigo-600" />
            <p className="mt-2 text-sm text-slate-600">Loading notifications...</p>
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {!loading && notifications.length === 0 && (
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-8 text-center">
            <p className="text-sm text-slate-600">No notifications yet</p>
          </div>
        )}

        {!loading && notifications.length > 0 && (
          <div className="space-y-3">
            {notifications.map((notif) => (
              <div key={notif.id} className="rounded-lg border border-slate-200 bg-white p-4 hover:border-indigo-200 hover:shadow-md transition">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p className="font-semibold text-slate-900">{notif.title}</p>
                    <p className="mt-1 text-sm text-slate-600">{notif.message}</p>
                    <p className="mt-2 text-xs text-slate-500">
                      {new Date(notif.created_at).toLocaleString()}
                    </p>
                  </div>
                  {notif.verification_request_id && (
                    <button
                      onClick={() => router.push(`/verification/consent/${notif.verification_request_id}`)}
                      className="whitespace-nowrap rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700"
                    >
                      Review
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}
