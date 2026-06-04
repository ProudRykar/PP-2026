export interface Message {
  id: string
  channel: string
  sender_id: string
  content: string
  timestamp: string
  metadata: Record<string, unknown>
  recipient: string | null
  subject: string | null
}

export interface ChannelList {
  channels: string[]
}

export interface ReplyPayload {
  message_id: string
  content: string
  subject?: string
}

export interface HealthStatus {
  status: string
  service: string
}
