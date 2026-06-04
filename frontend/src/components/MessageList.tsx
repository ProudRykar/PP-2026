import type { Message } from '../types'
import { MessageCard } from './MessageCard'

interface MessageListProps {
  messages: Message[]
  loading: boolean
}

export function MessageList({ messages, loading }: MessageListProps) {
  if (loading) {
    return <p className="py-10 text-center text-gray-400">Загрузка сообщений…</p>
  }
  if (messages.length === 0) {
    return <p className="py-10 text-center text-gray-400">Нет сообщений</p>
  }
  return (
    <div className="grid gap-3">
      {messages.map((msg) => (
        <MessageCard key={msg.id} message={msg} />
      ))}
    </div>
  )
}
