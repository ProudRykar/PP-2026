import { useState, useRef, useEffect } from 'react'
import { replyToMessage } from '../api'
import type { Message } from '../types'

interface EmailReplyFormProps {
  replyTarget: Message
  onSent: () => void
}

export function EmailReplyForm({ replyTarget, onSent }: EmailReplyFormProps) {
  const extractEmail = (raw: string) => {
    const m = raw.match(/<([^>]+)>/)
    return m ? m[1] : raw
  }
  const [to, setTo] = useState(extractEmail(replyTarget.sender_id))
  const [subject, setSubject] = useState(replyTarget.subject || '')
  const [body, setBody] = useState('')
  const [sending, setSending] = useState(false)
  const bodyRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bodyRef.current?.focus()
  }, [replyTarget.id])

  useEffect(() => {
    setTo(extractEmail(replyTarget.sender_id))
    setSubject(replyTarget.subject || '')
    setBody('')
  }, [replyTarget.id, replyTarget.sender_id, replyTarget.subject])

  const handleSend = async () => {
    if (!body.trim() || sending) return
    setSending(true)
    try {
      await replyToMessage({
        message_id: replyTarget.id,
        content: body,
        subject: subject || undefined,
      })
      setBody('')
      onSent()
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="border-t border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      <div className="px-4 py-3">
        <div className="mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wide dark:text-gray-500">
          Ответить на письмо
        </div>

        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="w-12 shrink-0 text-xs font-medium text-gray-500 dark:text-gray-400">Кому:</span>
            <input
              className="flex-1 rounded-lg border border-gray-300 px-3 py-1.5 text-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 dark:focus:border-blue-500"
              value={to}
              onChange={e => setTo(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-2">
            <span className="w-12 shrink-0 text-xs font-medium text-gray-500 dark:text-gray-400">Тема:</span>
            <input
              className="flex-1 rounded-lg border border-gray-300 px-3 py-1.5 text-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 dark:focus:border-blue-500"
              value={subject}
              onChange={e => setSubject(e.target.value)}
            />
          </div>
          <textarea
            ref={bodyRef}
            className="min-h-[80px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 dark:focus:border-blue-500"
            placeholder="Ваш ответ…"
            value={body}
            onChange={e => setBody(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && (e.metaKey || e.ctrlKey) && handleSend()}
          />
          <div className="flex justify-end gap-2">
            <button
              className="rounded-lg bg-blue-500 px-4 py-1.5 text-sm font-medium text-white transition hover:bg-blue-600 disabled:opacity-40 dark:bg-blue-600 dark:hover:bg-blue-700"
              onClick={handleSend}
              disabled={!body.trim() || sending}
            >
              {sending ? 'Отправка…' : 'Отправить'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
