import type { Message, ChannelList, ReplyPayload, HealthStatus, UploadResult, Client, ClientUpdatePayload } from './types'

const BASE = ''

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
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
