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

export interface ChannelIdentity {
  channel: string
  external_id: string
  username: string | null
  display_name: string | null
}

export interface Client {
  id: string
  name: string
  phone: string | null
  email: string | null
  avatar_url: string | null
  channels: ChannelIdentity[]
  metadata: Record<string, unknown>
  created_at: string | null
  last_interaction: string | null
}

export interface ClientUpdatePayload {
  name?: string
  phone?: string
  email?: string
  avatar_url?: string
  metadata?: Record<string, unknown>
}
