export interface Message {
  id: string
  channel: string
  sender_id: string
  content: string
  timestamp: string
  message_type?: string
  metadata: Record<string, unknown>
  recipient: string | null
  subject: string | null
  parent_id: string | null
}

export interface ChannelList {
  channels: string[]
}

export interface ReplyPayload {
  message_id: string
  content: string
  subject?: string
  file_url?: string
}

export interface UploadResult {
  status: string
  file_url?: string
  detail?: string
}

export interface HealthStatus {
  status: string
  service: string
}
