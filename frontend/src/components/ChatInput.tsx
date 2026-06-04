import { useState, useRef, useEffect } from 'react'
import { replyToMessage } from '../api'
import type { Message } from '../types'

interface ChatInputProps {
  replyTarget: Message | null
  onSent: () => void
}

export function ChatInput({ replyTarget, onSent }: ChatInputProps) {
  const [text, setText] = useState('')
  const [sending, setSending] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [replyTarget])

  const handleSend = async () => {
    const target = replyTarget
    if (!target || !text.trim() || sending) return
    setSending(true)
    try {
      await replyToMessage({ message_id: target.id, content: text })
      setText('')
      onSent()
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-3">
      {replyTarget && (
        <div className="mb-2 flex items-center gap-1.5 text-xs text-gray-400">
          <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16l-4-4m0 0l4-4m-4 4h18" />
          </svg>
          Ответ на сообщение от {new Date(replyTarget.timestamp).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })} — {replyTarget.content.slice(0, 40)}{replyTarget.content.length > 40 ? '…' : ''}
        </div>
      )}
      <div className="flex gap-2">
        <input
          ref={inputRef}
          className="flex-1 rounded-xl border border-gray-300 px-4 py-2.5 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
          placeholder={replyTarget ? 'Напишите ответ…' : 'Выберите сообщение для ответа…'}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button
          className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500 text-white transition hover:bg-blue-600 disabled:opacity-40"
          onClick={handleSend}
          disabled={!replyTarget || !text.trim() || sending}
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  )
}
