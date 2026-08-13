const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

type RequestOpts = RequestInit & { auth?: boolean }

async function request(path: string, opts: RequestOpts = {}) {
  const url = `${API_BASE}${path}`
  const headers: Record<string, string> = {
    'Accept': 'application/json'
  }

  if (opts.headers) Object.assign(headers, opts.headers as Record<string,string>)

  if (opts.auth) {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access') : null
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(url, {
    ...opts,
    headers,
  })

  const text = await res.text()
  let data = null
  try { data = text ? JSON.parse(text) : null } catch(e) { data = text }

  if (!res.ok) {
    throw { status: res.status, data }
  }

  return data
}

export async function register(payload: { username: string, password: string, email?: string }) {
  return request('/api/accounts/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function loginWithToken(token: string) {
  // store token locally (no server call) - used for demo when user pastes a token
  localStorage.setItem('access', token)
  return { ok: true }
}

export async function uploadIdentity(formData: FormData) {
  return request('/api/identity/documents/', {
    method: 'POST',
    body: formData,
    auth: true,
  })
}

export async function createVerificationRequest(payload: { bank_code: string, user_id: string, claim: string }) {
  return request('/api/verification/request/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    auth: true,
  })
}

export async function consentRequest(id: string) {
  return request(`/api/verification/${id}/consent/`, {
    method: 'POST',
    auth: true,
  })
}

export async function verifyRequest(id: string) {
  return request(`/api/verification/${id}/verify/`, {
    method: 'POST',
    auth: true,
  })
}

export default { request }
