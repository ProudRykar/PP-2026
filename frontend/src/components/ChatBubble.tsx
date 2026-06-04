import type { Message } from '../types'

interface ChatBubbleProps {
  message: Message
  isOwn: boolean
  isFirst: boolean
  isLast: boolean
  senderLabel: string
  channelLabel: string
  selected: boolean
  onSelect: (msg: Message) => void
}

export function ChatBubble({ message, isOwn, isFirst, isLast, senderLabel, channelLabel, selected, onSelect }: ChatBubbleProps) {
  const time = new Date(message.timestamp).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  const date = new Date(message.timestamp).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })

  return (
    <div
      className={`group relative max-w-[75%] ${isFirst ? 'mt-4' : 'mt-0.5'} ${selected ? 'opacity-100' : ''}`}
      onClick={() => onSelect(message)}
    >
      {isFirst && (
        <div className={`mb-1 flex items-center gap-2 ${isOwn ? 'justify-end' : ''}`}>
          {!isOwn && <span className="text-xs font-semibold text-gray-500">{senderLabel}</span>}
          {!isOwn && <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-500">{channelLabel}</span>}
          {isOwn && <span className="text-[10px] text-gray-400">Вы</span>}
        </div>
      )}
      <div
        className={`
          relative rounded-2xl px-3.5 py-2 text-sm leading-relaxed transition cursor-pointer
          ${isFirst ? (isOwn ? 'rounded-tr-md' : 'rounded-tl-md') : ''}
          ${isLast ? (isOwn ? 'rounded-br-md' : 'rounded-bl-md') : ''}
          ${isOwn ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-800'}
          ${selected ? (isOwn ? 'ring-2 ring-blue-300' : 'bg-blue-100 ring-2 ring-blue-300') : ''}
          ${isOwn ? 'hover:bg-blue-600' : 'hover:bg-gray-200'}
        `}
      >
        <p>{message.content || <span className="italic opacity-70">Нет текста</span>}</p>
        <div className={`mt-0.5 flex items-center justify-end gap-1 ${isLast ? '' : 'opacity-0 group-hover:opacity-100'}`}>
          <span className={`text-[10px] ${isOwn ? 'text-blue-200' : 'text-gray-400'}`}>{time}</span>
          {isLast && <span className={`text-[10px] ${isOwn ? 'text-blue-200' : 'text-gray-400'}`}>{date}</span>}
        </div>
      </div>
    </div>
  )
}
