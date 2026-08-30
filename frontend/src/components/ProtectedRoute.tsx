import { useEffect } from 'react'
import { useRouter } from 'next/router'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access')
      if (!token) router.push('/login')
    }
  }, [router])

  return <>{children}</>
}
