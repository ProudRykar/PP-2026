import type { Message, ChannelList, ReplyPayload, HealthStatus, UploadResult, Client, ClientUpdatePayload, Curator, AssignCuratorPayload, TransferPayload, AssignmentHistoryEntry, AuthResponse } from './types'

const BASE = ''

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('auth_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...getAuthHeaders(),
    ...(init?.headers as Record<string, string> | undefined),
  }
  console.debug('[API]', init?.method || 'GET', path, { hasAuth: !!headers.Authorization })
  const res = await fetch(`${BASE}${path}`, {
    headers,
    ...init,
  })
  console.debug('[API] response:', res.status, path)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    console.debug('[API] error body:', body)
    throw new Error(body.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export function fetchMessages(channel?: string, senderId?: string): Promise<Message[]> {
  const params = new URLSearchParams()
  if (channel && channel !== 'all') params.set('channel', channel)
  if (senderId) params.set('sender_id', senderId)
  const qs = params.toString()
  return request<Message[]>(`/api/messages${qs ? `?${qs}` : ''}`)
}

export function fetchMessage(id: string): Promise<Message> {
  return request<Message>(`/api/messages/${encodeURIComponent(id)}`)
}

export function replyToMessage(payload: ReplyPayload): Promise<{ status: string }> {
  return request<{ status: string }>('/api/messages/reply', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function fetchChannels(): Promise<ChannelList> {
  return request<ChannelList>('/api/channels')
}

export function fetchHealth(): Promise<HealthStatus> {
  return request<HealthStatus>('/health')
}

export function fetchAllClients(): Promise<Client[]> {
  return request<Client[]>('/api/clients')
}

export function fetchClientByChannel(channel: string, externalId: string): Promise<Client | null> {
  const params = new URLSearchParams({ channel, external_id: externalId })
  return request<Client | null>(`/api/clients/by-channel?${params}`)
}

export function fetchClient(id: string): Promise<Client> {
  return request<Client>(`/api/clients/${encodeURIComponent(id)}`)
}

export function updateClient(id: string, payload: ClientUpdatePayload): Promise<Client> {
  return request<Client>(`/api/clients/${encodeURIComponent(id)}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export async function uploadFile(file: File): Promise<UploadResult> {
  const buffer = await file.arrayBuffer()
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  const base64 = btoa(binary)

  const res = await fetch(`${BASE}/api/upload`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      file: base64,
      filename: file.name,
      content_type: file.type,
    }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export function fetchCurators(status?: string): Promise<Curator[]> {
  const params = status ? `?status=${status}` : ''
  return request<Curator[]>(`/api/curators${params}`)
}

export function fetchCurator(id: string): Promise<Curator> {
  return request<Curator>(`/api/curators/${encodeURIComponent(id)}`)
}

export function assignCurator(messageId: string, payload: AssignCuratorPayload): Promise<{ status: string }> {
  return request<{ status: string }>(`/api/messages/${encodeURIComponent(messageId)}/assign`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function transferCurator(messageId: string, payload: TransferPayload): Promise<{ status: string }> {
  return request<{ status: string }>(`/api/messages/${encodeURIComponent(messageId)}/transfer`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function fetchAssignmentHistory(messageId: string): Promise<AssignmentHistoryEntry[]> {
  return request<AssignmentHistoryEntry[]>(`/api/messages/${encodeURIComponent(messageId)}/assignments`)
}

export function login(login: string, password: string): Promise<AuthResponse> {
  return request<AuthResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ login, password }),
  })
}

export function register(full_name: string, login: string, email: string, password: string, role?: string): Promise<AuthResponse> {
  return request<AuthResponse>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ full_name, login, email, password, role: role ?? 'agent' }),
  })
}

export function fetchMe(): Promise<AuthResponse> {
  return request<AuthResponse>('/api/auth/me')
}
