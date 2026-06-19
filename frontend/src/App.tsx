import { useState, useEffect, useCallback, useRef } from 'react'
import type { Message } from './types'
import { fetchMessages, fetchChannels, fetchHealth } from './api'
import { MessageList } from './components/MessageList'
import { ChatInput } from './components/ChatInput'
import { EmailReplyForm } from './components/EmailReplyForm'
import { FilterBar } from './components/FilterBar'
import { useWebSocket } from './hooks/useWebSocket'

export default function App() {
  const [channel, setChannel] = useState('all')
  const [channels, setChannels] = useState<string[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [backendOk, setBackendOk] = useState(true)
  const [selected, setSelected] = useState<Message | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  const load = useCallback(async (ch: string) => {
    setLoading(true)
    try {
      const data = await fetchMessages(ch)
      setMessages(data)
      if (data.length > 0) {
        setSelected(data[0])
      }
    } catch {
      setBackendOk(false)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    fetchHealth()
      .then(() => setBackendOk(true))
      .catch(() => setBackendOk(false))

    fetchChannels()
      .then((d) => setChannels(d.channels))
      .catch(() => setBackendOk(false))
  }, [])

  useEffect(() => {
    load(channel)
  }, [channel, load])

  useWebSocket((data) => {
    if ((data as { type?: string }).type === 'new_message') {
      load(channel)
    }
  })

  if (!backendOk) {
    return (
      <div className="mx-auto max-w-2xl py-20 text-center">
        <p className="text-lg text-red-500">Сервер недоступен</p>
        <p className="mt-1 text-sm text-gray-400">Проверьте, запущен ли бэкенд</p>
      </div>
    )
  }

  return (
    <div className="mx-auto flex h-screen max-w-3xl flex-col bg-white shadow-sm">
      <header className="border-b border-gray-200 bg-gray-800 px-4 py-4 text-white">
        <h1 className="text-lg font-bold">Омниканальные сообщения</h1>
        <p className="mt-0.5 text-xs text-gray-300">Единый просмотр всех ваших сообщений</p>
      </header>

      <div className="border-b border-gray-200 bg-gray-50 px-4 py-2">
        <FilterBar channels={channels} current={channel} onChange={setChannel} />
      </div>

      <div className="flex-1 overflow-y-auto px-4">
        <MessageList messages={messages} loading={loading} selectedId={selected?.id ?? null} onSelect={setSelected} />
        <div ref={bottomRef} />
      </div>

      {selected?.channel === 'email' ? (
        <EmailReplyForm replyTarget={selected} onSent={() => load(channel)} />
      ) : (
        <ChatInput replyTarget={selected} onSent={() => load(channel)} />
      )}
    </div>
  )
}
