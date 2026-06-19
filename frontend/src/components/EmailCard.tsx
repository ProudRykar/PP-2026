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
  const isSent = message.sender_id === 'agent' || message.metadata?.is_reply === true
  const senderEmail = typeof message.metadata?.email === 'string'
    ? message.metadata.email
    : message.sender_id.replace(/.*<([^>]+)>/, '$1')
  const senderName = isSent
    ? 'Вы'
    : message.sender_id.replace(/<[^>]+>/, '').replace(/^["\s]+|["\s]+$/g, '') || senderEmail
  const subject = message.subject || '(без темы)'
  const preview = (message.content || '').replace(/<[^>]+>/g, '').slice(0, 80)
  const hasHtml = message.metadata?.has_html === true
  const toField = isSent
    ? message.recipient
    : (typeof message.metadata?.to === 'string' ? message.metadata.to : message.recipient) || '—'

  return (
    <>
      <tr
        className={`cursor-pointer border-b border-gray-50 transition hover:bg-gray-50 ${
          selected ? 'bg-blue-50' : ''
        }`}
        onClick={() => onSelect(message)}
      >
        <td className="truncate px-3 py-2.5 text-xs font-medium text-gray-700">{senderName}</td>
        <td className="truncate px-3 py-2.5 text-xs font-medium text-gray-800">{subject}</td>
        <td className="truncate px-3 py-2.5 text-xs text-gray-500">{preview || <span className="italic text-gray-300">(пусто)</span>}</td>
        <td className="whitespace-nowrap px-3 py-2.5 text-right text-[10px] text-gray-400">{time}</td>
      </tr>
      {selected && (
        <tr className="border-b border-gray-100">
          <td colSpan={4} className="bg-white px-4 py-3">
            <div className="mb-3 space-y-1 border-b border-gray-100 pb-3 text-xs text-gray-600">
              <div className="flex gap-2">
                <span className="w-14 shrink-0 font-medium text-gray-400">От:</span>
                <span>{senderName} {senderEmail !== senderName ? `<${senderEmail}>` : ''}</span>
              </div>
              <div className="flex gap-2">
                <span className="w-14 shrink-0 font-medium text-gray-400">Кому:</span>
                <span>{toField}</span>
              </div>
              <div className="flex gap-2">
                <span className="w-14 shrink-0 font-medium text-gray-400">Тема:</span>
                <span className="font-medium text-gray-800">{subject}</span>
              </div>
              <div className="flex gap-2">
                <span className="w-14 shrink-0 font-medium text-gray-400">Дата:</span>
                <span>{time}</span>
              </div>
            </div>
            {hasHtml ? (
              <iframe
                className="w-full rounded-lg border border-gray-100"
                style={{ height: Math.min(640, Math.max(200, (message.content || '').length / 10)) }}
                srcDoc={message.content}
                sandbox="allow-same-origin"
                title="email body"
              />
            ) : (
              <div className="max-h-96 overflow-y-auto whitespace-pre-wrap text-sm text-gray-700">
                {message.content || <span className="italic text-gray-400">(пусто)</span>}
              </div>
            )}
          </td>
        </tr>
      )}
    </>
  )
}
