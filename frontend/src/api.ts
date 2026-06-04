import type { Message, ChannelList, ReplyPayload, HealthStatus } from './types'

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

export function fetchMessages(channel?: string): Promise<Message[]> {
  const params = new URLSearchParams()
  if (channel && channel !== 'all') params.set('channel', channel)
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
