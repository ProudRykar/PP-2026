import type { Message } from '../types'
import { ChatGroup } from './ChatGroup'
import { EmailCard } from './EmailCard'

interface MessageListProps {
  messages: Message[]
  loading: boolean
  selectedId: string | null
  onSelect: (msg: Message) => void
}

function groupBySender(messages: Message[]): Message[][] {
  const groups: Message[][] = []
  for (const msg of messages) {
    const last = groups[groups.length - 1]
    if (last && last[0].sender_id === msg.sender_id) {
      last.push(msg)
    } else {
      groups.push([msg])
    }
  }
  return groups
}

function senderLabel(msg: Message): string {
  if (msg.sender_id.startsWith('telegram:') || !isNaN(Number(msg.sender_id))) {
    return `User ${msg.sender_id.slice(0, 6)}`
  }
  return msg.sender_id.split('@')[0]
}

function channelLabel(msg: Message): string {
  return msg.channel.charAt(0).toUpperCase() + msg.channel.slice(1)
}

export function MessageList({ messages, loading, selectedId, onSelect }: MessageListProps) {
  if (loading) {
    return <p className="py-10 text-center text-gray-400">Загрузка сообщений…</p>
  }
  if (messages.length === 0) {
    return <p className="py-10 text-center text-gray-400">Нет сообщений</p>
  }

  const reversed = [...messages].reverse()
  const chatMessages = reversed.filter(m => m.channel !== 'email')
  const emailMessages = reversed.filter(m => m.channel === 'email')

  const chatGroups = groupBySender(chatMessages)

  return (
    <div className="flex flex-col pb-4">
      {chatGroups.map((group, gi) => (
        <ChatGroup
          key={`chat-${group[0].sender_id}-${gi}`}
          messages={group}
          senderLabel={senderLabel(group[0])}
          channelLabel={channelLabel(group[0])}
          selectedId={selectedId}
          onSelect={onSelect}
        />
      ))}
      {emailMessages.map(msg => (
        <EmailCard
          key={msg.id}
          message={msg}
          selected={selectedId === msg.id}
          onSelect={onSelect}
        />
      ))}
    </div>
  )
}
