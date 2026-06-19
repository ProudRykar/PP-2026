import type { Message } from '../types'

interface EmailCardProps {
  message: Message
  selected: boolean
  onSelect: (msg: Message) => void
}

export function EmailCard({ message, selected, onSelect }: EmailCardProps) {
  const time = new Date(message.timestamp).toLocaleString('ru-RU', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  })
  const hasHtml = message.metadata?.has_html ?? false
  const isSent = message.sender_id === 'agent' || message.metadata?.is_reply === true

  return (
    <div
      className={`my-2 rounded-xl border shadow-sm transition cursor-pointer ${
        selected ? 'border-blue-400 ring-2 ring-blue-200' : 'border-gray-200 hover:border-gray-300'
      } ${isSent ? 'ml-8 border-blue-100 bg-blue-50/30' : ''}`}
      onClick={() => onSelect(message)}
    >
      <div className={`border-b px-4 py-3 ${isSent ? 'border-blue-100 bg-blue-50' : 'border-gray-100 bg-gray-50'}`}>
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-gray-800">{message.subject || '(без темы)'}</span>
          <span className="shrink-0 text-xs text-gray-400">{time}</span>
        </div>
        {isSent ? (
          <p className="mt-1 text-xs text-blue-600">Кому: {message.recipient || message.sender_id}</p>
        ) : (
          <p className="mt-1 text-xs text-gray-500">{message.sender_id}</p>
        )}
      </div>
      {hasHtml ? (
        <iframe
          className="h-64 w-full rounded-b-xl"
          srcDoc={message.content}
          sandbox="allow-same-origin"
          title="email body"
        />
      ) : (
        <div className="px-4 py-3 text-sm text-gray-700 whitespace-pre-wrap">
          {message.content || <span className="italic text-gray-400">(пусто)</span>}
        </div>
      )}
    </div>
  )
}
