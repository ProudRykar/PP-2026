import { useState, useEffect, useCallback } from 'react'
import type { Message } from './types'
import { fetchMessages, fetchChannels, fetchHealth } from './api'
import { MessageList } from './components/MessageList'
import { FilterBar } from './components/FilterBar'
import { useWebSocket } from './hooks/useWebSocket'

export default function App() {
  const [channel, setChannel] = useState('all')
  const [channels, setChannels] = useState<string[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [backendOk, setBackendOk] = useState(true)

  const load = useCallback(async (ch: string) => {
    setLoading(true)
    try {
      const data = await fetchMessages(ch)
      setMessages(data)
    } catch {
      setBackendOk(false)
    } finally {
      setLoading(false)
    }
  }, [])

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
    <div className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-6 rounded-xl bg-gray-800 p-6 text-white">
        <h1 className="text-2xl font-bold">Омниканальные сообщения</h1>
        <p className="mt-1 text-sm text-gray-300">Единый просмотр всех ваших сообщений</p>
      </header>

      <FilterBar channels={channels} current={channel} onChange={setChannel} />

      <div className="mt-4">
        <MessageList messages={messages} loading={loading} />
      </div>
    </div>
  )
}
