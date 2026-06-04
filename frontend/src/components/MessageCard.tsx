import { useState } from 'react'
import type { Message } from '../types'
import { replyToMessage } from '../api'

const channelColors: Record<string, string> = {
  telegram: 'bg-sky-500',
  email: 'bg-red-500',
}

interface MessageCardProps {
  message: Message
}

export function MessageCard({ message }: MessageCardProps) {
  const [replyText, setReplyText] = useState('')
  const [sending, setSending] = useState(false)
  const [sent, setSent] = useState(false)

  const handleReply = async () => {
    if (!replyText.trim()) return
    setSending(true)
    try {
      await replyToMessage({ message_id: message.id, content: replyText })
      setReplyText('')
      setSent(true)
      setTimeout(() => setSent(false), 3000)
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-center justify-between gap-2">
        <span className="font-semibold text-gray-800">{message.sender}</span>
        <span
          className={`rounded px-2 py-0.5 text-xs font-bold text-white ${channelColors[message.channel] ?? 'bg-gray-500'}`}
        >
          {message.channel}
        </span>
      </div>

      <p className="mt-1 text-xs text-gray-400">
        {new Date(message.timestamp).toLocaleString('ru-RU')}
      </p>

      <p className="mt-3 leading-relaxed text-gray-700">
        {message.content || <span className="italic text-gray-400">(пусто)</span>}
      </p>

      <div className="mt-3 flex gap-2">
        <input
          className="flex-1 rounded border border-gray-300 px-3 py-1.5 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
          placeholder="Ответить…"
          value={replyText}
          onChange={(e) => setReplyText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleReply()}
        />
        <button
          className="rounded bg-blue-500 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-blue-600 disabled:opacity-50"
          onClick={handleReply}
          disabled={sending || !replyText.trim()}
        >
          {sending ? '…' : sent ? '✓' : '→'}
        </button>
      </div>
    </div>
  )
}
