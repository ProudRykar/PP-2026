import { useSyncExternalStore } from 'react'
import type { Message } from '../types'

function useIsDark() {
  return useSyncExternalStore(
    (cb) => {
      const observer = new MutationObserver(cb)
      observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
      return () => observer.disconnect()
    },
    () => document.documentElement.classList.contains('dark'),
  )
}

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
        className={`cursor-pointer border-b border-gray-50 transition hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-700/50 ${
          selected ? 'bg-blue-50 dark:bg-blue-900/30' : ''
        }`}
        onClick={() => onSelect(message)}
      >
        <td className="truncate px-3 py-2.5 text-xs font-medium text-gray-700 dark:text-gray-300">{senderName}</td>
        <td className="truncate px-3 py-2.5 text-xs font-medium text-gray-800 dark:text-gray-100">{subject}</td>
        <td className="truncate px-3 py-2.5 text-xs text-gray-500 dark:text-gray-400">{preview || <span className="italic text-gray-300 dark:text-gray-600">(пусто)</span>}</td>
        <td className="whitespace-nowrap px-3 py-2.5 text-right text-[10px] text-gray-400 dark:text-gray-500">{time}</td>
      </tr>
      {selected && (
        <tr className="border-b border-gray-100 dark:border-gray-700">
          <td colSpan={4} className="bg-white px-4 py-3 dark:bg-gray-800">
            <div className="mb-3 space-y-1 border-b border-gray-100 pb-3 text-xs text-gray-600 dark:border-gray-700 dark:text-gray-400">
              <div className="flex gap-2">
                <span className="w-14 shrink-0 font-medium text-gray-400 dark:text-gray-500">От:</span>
                <span>{senderName} {senderEmail !== senderName ? `<${senderEmail}>` : ''}</span>
              </div>
              <div className="flex gap-2">
                <span className="w-14 shrink-0 font-medium text-gray-400 dark:text-gray-500">Кому:</span>
                <span>{toField}</span>
              </div>
              <div className="flex gap-2">
                <span className="w-14 shrink-0 font-medium text-gray-400 dark:text-gray-500">Тема:</span>
                <span className="font-medium text-gray-800 dark:text-gray-100">{subject}</span>
              </div>
              <div className="flex gap-2">
                <span className="w-14 shrink-0 font-medium text-gray-400 dark:text-gray-500">Дата:</span>
                <span>{time}</span>
              </div>
            </div>
            {hasHtml ? <HtmlEmailBody content={message.content} /> : (
              <div className="max-h-96 overflow-y-auto whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300">
                {message.content || <span className="italic text-gray-400 dark:text-gray-500">(пусто)</span>}
              </div>
            )}
          </td>
        </tr>
      )}
    </>
  )
}

function HtmlEmailBody({ content }: { content: string }) {
  const isDark = useIsDark()
  const darkStyles = '<style>body{color:#e5e7eb;background-color:#1f2937;}a{color:#93c5fd;}</style>'
  const srcdoc = isDark ? darkStyles + content : content

  return (
    <iframe
      className="w-full rounded-lg border border-gray-100 dark:border-gray-700"
      style={{ height: Math.min(640, Math.max(200, (content || '').length / 10)) }}
      srcDoc={srcdoc}
      sandbox="allow-same-origin"
      title="email body"
    />
  )
}
