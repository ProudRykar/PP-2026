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
  depth?: number
  unread?: boolean
}

export function EmailCard({ message, selected, onSelect, depth = 0, unread }: EmailCardProps) {
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
  const hasBorder = depth === 0

  return (
    <div>
      <div
        className={`flex cursor-pointer items-center gap-2 transition hover:bg-gray-50 dark:hover:bg-gray-700/50 ${
          hasBorder ? 'border-b border-gray-50 dark:border-gray-700' : ''
        } ${selected ? 'bg-blue-50 dark:bg-blue-900/30' : ''} ${unread ? 'bg-blue-50/40 dark:bg-blue-900/20' : ''}`}
        onClick={() => onSelect(message)}
      >
        {unread && <div className="ml-2 h-2 w-2 shrink-0 rounded-full bg-blue-500" />}
        <div className="flex min-w-0 flex-1 items-center gap-2 px-1 py-2.5">
          <span className={`truncate text-xs ${
            unread ? 'font-semibold' : 'font-medium'
          } ${depth > 0 ? 'pl-4 text-gray-400 dark:text-gray-500' : 'text-gray-700 dark:text-gray-300'}`}>
            {depth > 0 && <span className="mr-1 select-none">└</span>}
            {depth > 0 ? 'agent' : senderName}
          </span>
          <span className={`truncate text-xs ${unread ? 'font-semibold' : 'font-medium'} text-gray-800 dark:text-gray-100`}>{subject}</span>
          <span className="hidden truncate text-xs text-gray-500 sm:inline dark:text-gray-400">
            {preview || <span className="italic text-gray-300 dark:text-gray-600">(пусто)</span>}
          </span>
        </div>
        <span className="shrink-0 px-3 text-[10px] text-gray-400 dark:text-gray-500">{time}</span>
      </div>
      {selected && (
        <div className="border-b border-gray-100 bg-white px-4 py-3 dark:border-gray-700 dark:bg-gray-800">
          <div className="mb-3 space-y-1.5 border-b border-gray-100 pb-3 text-sm text-gray-600 dark:border-gray-700 dark:text-gray-400">
            <div className="flex gap-2">
              <span className="w-16 shrink-0 font-medium text-gray-400 dark:text-gray-500">От:</span>
              <span>{senderName} {senderEmail !== senderName ? `<${senderEmail}>` : ''}</span>
            </div>
            <div className="flex gap-2">
              <span className="w-16 shrink-0 font-medium text-gray-400 dark:text-gray-500">Кому:</span>
              <span>{toField}</span>
            </div>
            <div className="flex gap-2">
              <span className="w-16 shrink-0 font-medium text-gray-400 dark:text-gray-500">Тема:</span>
              <span className="font-medium text-gray-800 dark:text-gray-100">{subject}</span>
            </div>
            <div className="flex gap-2">
              <span className="w-16 shrink-0 font-medium text-gray-400 dark:text-gray-500">Дата:</span>
              <span>{time}</span>
            </div>
          </div>
          {hasHtml ? <HtmlEmailBody content={message.content} /> : (
            <div className="max-h-96 overflow-y-auto whitespace-pre-wrap text-base text-gray-700 dark:text-gray-300">
              {message.content || <span className="italic text-gray-400 dark:text-gray-500">(пусто)</span>}
            </div>
          )}
        </div>
      )}
    </div>
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
