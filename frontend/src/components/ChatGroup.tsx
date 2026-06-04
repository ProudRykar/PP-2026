import type { Message } from '../types'
import { ChatBubble } from './ChatBubble'

interface ChatGroupProps {
  messages: Message[]
  senderLabel: string
  channelLabel: string
  selectedId: string | null
  onSelect: (msg: Message) => void
}

export function ChatGroup({ messages, senderLabel, channelLabel, selectedId, onSelect }: ChatGroupProps) {
  const isOwn = messages[0].sender_id === "agent"
  return (
    <div className={`flex flex-col ${isOwn ? 'items-end' : 'items-start'}`}>
      {messages.map((msg, i) => (
        <ChatBubble
          key={msg.id}
          message={msg}
          isOwn={isOwn}
          isFirst={i === 0}
          isLast={i === messages.length - 1}
          senderLabel={senderLabel}
          channelLabel={channelLabel}
          selected={selectedId === msg.id}
          onSelect={onSelect}
        />
      ))}
    </div>
  )
}
