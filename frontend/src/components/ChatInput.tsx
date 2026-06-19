import { useState, useRef, useEffect } from 'react'
import { replyToMessage, uploadFile } from '../api'
import type { Message } from '../types'

interface ChatInputProps {
  replyTarget: Message | null
  onSent: () => void
}

export function ChatInput({ replyTarget, onSent }: ChatInputProps) {
  const [text, setText] = useState('')
  const [sending, setSending] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [replyTarget])

  useEffect(() => {
    if (selectedFile) {
      const url = URL.createObjectURL(selectedFile)
      setPreviewUrl(url)
      return () => URL.revokeObjectURL(url)
    }
    setPreviewUrl(null)
  }, [selectedFile])

  const handleSend = async () => {
    const target = replyTarget
    if (!target || sending) return
    if (!text.trim() && !selectedFile) return

    setSending(true)
    try {
      let fileUrl: string | undefined
      if (selectedFile) {
        const result = await uploadFile(selectedFile)
        if (result.file_url) {
          fileUrl = result.file_url
        }
      }
      await replyToMessage({ message_id: target.id, content: text, file_url: fileUrl })
      setText('')
      setSelectedFile(null)
      onSent()
    } finally {
      setSending(false)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-3 dark:border-gray-700 dark:bg-gray-800">
      {replyTarget && (
        <div className="mb-2 flex items-center gap-1.5 text-xs text-gray-400 dark:text-gray-500">
          <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16l-4-4m0 0l4-4m-4 4h18" />
          </svg>
          Ответ на сообщение от {new Date(replyTarget.timestamp).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })} — {replyTarget.content.slice(0, 40)}{replyTarget.content.length > 40 ? '…' : ''}
        </div>
      )}

      {previewUrl && (
        <div className="relative mb-2 inline-block">
          <img src={previewUrl} alt="preview" className="h-20 w-20 rounded-lg object-cover" />
          <button
            className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-white text-xs hover:bg-red-600"
            onClick={() => setSelectedFile(null)}
          >
            ✕
          </button>
        </div>
      )}

      <div className="flex gap-2">
        <button
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gray-100 text-gray-500 transition hover:bg-gray-200 disabled:opacity-40 dark:bg-gray-700 dark:text-gray-400 dark:hover:bg-gray-600"
          onClick={() => fileInputRef.current?.click()}
          disabled={!replyTarget || sending}
          title="Прикрепить изображение"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleFileSelect}
        />
        <input
          ref={inputRef}
          className="flex-1 rounded-xl border border-gray-300 px-4 py-2.5 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 dark:focus:border-blue-500"
          placeholder={replyTarget ? 'Напишите ответ…' : 'Выберите сообщение для ответа…'}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500 text-white transition hover:bg-blue-600 disabled:opacity-40 dark:bg-blue-600 dark:hover:bg-blue-700"
          onClick={handleSend}
          disabled={!replyTarget || (!text.trim() && !selectedFile) || sending}
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  )
}
