const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ||
  "http://127.0.0.1:8000";

type RequestOptions = RequestInit & {
  auth?: boolean;
};

export type RegisterPayload = {
  legal_name: string;
  username: string;
  email: string;
  password: string;
  phone_number?: string;
};

export type LoginPayload = {
  username: string;
  password: string;
};

export type ApiError = {
  status: number;
  data: unknown;
};

async function request<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const {
    auth = false,
    headers: customHeaders,
    ...requestOptions
  } = options;

  const headers: Record<string, string> = {
    Accept: "application/json",
  };

  if (customHeaders) {
    Object.assign(
      headers,
      customHeaders as Record<string, string>
    );
  }

  if (auth && typeof window !== "undefined") {
    const token = sessionStorage.getItem("access");

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(
    `${API_BASE}${path}`,
    {
      ...requestOptions,
      headers,
    }
  );

  const text = await response.text();

  let data: unknown = null;

  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!response.ok) {
    const error: ApiError = {
      status: response.status,
      data,
    };

    throw error;
  }

  return data as T;
}
export async function login(payload: LoginPayload) {
  return request("/api/accounts/login/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function register(
  payload: RegisterPayload
): Promise<RegisterResponse> {
  return request<RegisterResponse>(
    "/api/accounts/register/",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }
  );
}

export async function uploadIdentity(formData: FormData) {
  return request("/api/identity/documents/", {
    method: "POST",
    body: formData,
    auth: true,
  });
}

export async function createVerificationRequest(payload: {
  bank_code: string;
  user_id: string;
  claim: string;
}) {
  return request("/api/verification/request/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    auth: true,
  });
}

export async function consentRequest(id: string, approved: boolean = true) {
  return request(`/api/verification/${id}/consent/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ approved }),
    auth: true,
  });
}

export async function denyRequest(id: string) {
  return consentRequest(id, false);
}

export async function getNotifications() {
  return request("/api/verification/notifications/", {
    method: "GET",
    auth: true,
  });
}

export async function markNotificationAsRead(id: string) {
  return request(`/api/verification/notifications/${id}/read/`, {
    method: "POST",
    auth: true,
  });
}

export async function getVerificationRequests() {
  return request("/api/verification/requests/", {
    method: "GET",
    auth: true,
  });
}

export async function getVerificationRequest(id: string) {
  return request(`/api/verification/requests/${id}/`, {
    method: "GET",
    auth: true,
  });
}

export async function searchUsers(query: string) {
  return request(`/api/verification/search-users/?q=${encodeURIComponent(query)}`, {
    method: "GET",
    auth: true,
  });
}

export async function getBankRequests() {
  return request("/api/verification/bank-requests/", {
    method: "GET",
    auth: true,
  });
}

export async function getBankRequestDetail(id: string) {
  return request(`/api/verification/bank-requests/${id}/`, {
    method: "GET",
    auth: true,
  });
}

export async function bankLogin(payload: {
  bank_code: string;
  api_key: string;
}) {
  return request("/api/banks/login/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function getBankInfo(apiKey: string) {
  return request("/api/banks/info/", {
    method: "GET",
    headers: { "X-Bank-API-Key": apiKey },
  });
}

export async function verifyRequest(
  id: string,
  proof: unknown,
  publicSignals: unknown
) {
  return request(`/api/verification/${id}/verify/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ proof, publicSignals }),
    auth: true,
  });
}
export type RegisterResponse = {
  user_id: string | number;
  access: string;
  refresh: string;
};

const api = {
  request,
  login,
  register,
  uploadIdentity,
  createVerificationRequest,
  consentRequest,
  denyRequest,
  getNotifications,
  markNotificationAsRead,
  getVerificationRequests,
  getVerificationRequest,
  searchUsers,
  getBankRequests,
  getBankRequestDetail,
  bankLogin,
  getBankInfo,
  verifyRequest,
};

export default api;

