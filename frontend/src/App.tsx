import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import type { Message, Client } from './types'
import { fetchMessages, fetchChannels, fetchHealth, fetchAllClients } from './api'
import { MessageList } from './components/MessageList'
import { ChatInput } from './components/ChatInput'
import { EmailReplyForm } from './components/EmailReplyForm'
import { ClientCard } from './components/ClientCard'
import { ContactList, type Contact, type ContactChannel } from './components/ContactList'
import { useWebSocket } from './hooks/useWebSocket'

export default function App() {
  const [allMessages, setAllMessages] = useState<Message[]>([])
  const [clients, setClients] = useState<Map<string, Client>>(new Map())
  const [loading, setLoading] = useState(true)
  const [backendOk, setBackendOk] = useState(true)
  const [selected, setSelected] = useState<Message | null>(null)
  const [activeContact, setActiveContact] = useState<Contact | null>(null)

  const [showClientCard, setShowClientCard] = useState(false)
  const [unreadCounts, setUnreadCounts] = useState<Map<string, number>>(new Map())
  const countedUnreadRef = useRef(new Set<string>())

  const loadAll = useCallback(async () => {
    setLoading(true)
    try {
      const [msgs, cls] = await Promise.all([
        fetchMessages(),
        fetchAllClients(),
      ])
      setAllMessages(msgs)
      countedUnreadRef.current = new Set(msgs.map(m => m.id))
      const map = new Map<string, Client>()
      for (const c of cls) map.set(c.id, c)
      setClients(map)
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
    fetchChannels().catch(() => setBackendOk(false))
    loadAll()
  }, [loadAll])

  useWebSocket((data) => {
    const ev = data as Record<string, unknown>
    if (ev.type === 'new_message' && typeof ev.id === 'string') {
      const msg = ev as unknown as Message

      setAllMessages(prev => {
        if (prev.some(m => m.id === msg.id)) return prev
        return [...prev, msg]
      })

      const key = convKey(msg)
      if (!activeContact || activeContact.key !== key) {
        if (!countedUnreadRef.current.has(msg.id)) {
          countedUnreadRef.current.add(msg.id)
          setUnreadCounts(prev => {
            const next = new Map(prev)
            next.set(key, (next.get(key) || 0) + 1)
            return next
          })
        }
      }

      fetchAllClients().then(cls => {
        const map = new Map<string, Client>()
        for (const c of cls) map.set(c.id, c)
        setClients(map)
      }).catch(() => {})
    }
  })

  function extractId(raw: string): string {
    const m = raw.match(/<([^>]+)>/)
    return m ? m[1] : raw
  }

  function convKey(msg: Message): string {
    if (msg.sender_id === 'agent') return `${msg.channel}:${msg.recipient}`
    return `${msg.channel}:${extractId(msg.sender_id)}`
  }

  function convSenderId(msg: Message): string {
    if (msg.sender_id === 'agent') return msg.recipient ?? msg.sender_id
    return extractId(msg.sender_id)
  }

  const contacts = useMemo(() => {
    const senderGroups = new Map<string, { messages: Message[]; client: Client | null }>()

    for (const msg of allMessages) {
      const key = convKey(msg)
      if (!senderGroups.has(key)) {
        const lookupMsg = msg.sender_id === 'agent'
          ? { ...msg, sender_id: msg.recipient ?? '' }
          : msg
        const client = findClientForMessage(lookupMsg, clients)
        senderGroups.set(key, { messages: [], client })
      }
      senderGroups.get(key)!.messages.push(msg)
    }

    const byClient = new Map<string, { messages: Message[]; channels: Map<string, string>; client: Client }>()
    const standalone: { key: string; messages: Message[]; client: Client | null }[] = []

    for (const [key, group] of senderGroups) {
      if (group.client) {
        const cid = group.client.id
        if (!byClient.has(cid)) {
          byClient.set(cid, { messages: [], channels: new Map(), client: group.client })
        }
        const entry = byClient.get(cid)!
        entry.messages.push(...group.messages)
        const ch = key.split(':')[0]
        const sid = convSenderId({ ...group.messages[0], channel: ch } as Message)
        entry.channels.set(ch, sid)
      } else {
        standalone.push({ key, messages: group.messages, client: null })
      }
    }

    const result: Contact[] = []

    for (const [, entry] of byClient) {
      const sorted = entry.messages.sort(
        (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      )
      const latest = sorted[0]
      const channels: ContactChannel[] = [...entry.channels.entries()].map(([ch, sid]) => {
        const ci = entry.client.channels.find(c => c.channel === ch)
        return { channel: ch, senderId: sid, username: ci?.username ?? undefined }
      })
      const firstChannel = channels[0] ?? { channel: '', senderId: '' }
      result.push({
        key: entry.client.id,
        name: entry.client.name,
        channel: firstChannel.channel,
        senderId: firstChannel.senderId,
        channels,
        clientId: entry.client.id,
        avatarUrl: entry.client.avatar_url ?? null,
        lastMessage: latest.content || '[media]',
        lastTimestamp: latest.timestamp,
      })
    }

    for (const { key, messages, client } of standalone) {
      const sorted = messages.sort(
        (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      )
      const latest = sorted[0]
      const sid = convSenderId(latest)
      const name = client?.name ?? sid
      result.push({
        key,
        name,
        channel: latest.channel,
        senderId: sid,
        channels: [{ channel: latest.channel, senderId: sid }],
        clientId: client?.id ?? null,
        avatarUrl: client?.avatar_url ?? null,
        lastMessage: latest.content || '[media]',
        lastTimestamp: latest.timestamp,
      })
    }

    result.sort((a, b) => new Date(b.lastTimestamp).getTime() - new Date(a.lastTimestamp).getTime())
    return result
  }, [allMessages, clients])

  function msgMatch(msg: Message, channel: string, senderId: string): boolean {
    if (msg.channel !== channel) return false
    if (msg.sender_id === 'agent') return msg.recipient === senderId
    return extractId(msg.sender_id) === senderId
  }

  const filteredMessages = useMemo(() => {
    if (!activeContact) return []
    return allMessages
      .filter((m) => msgMatch(m, activeContact.channel, activeContact.senderId))
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
  }, [activeContact, allMessages])

  const handleSelectContact = useCallback((contact: Contact) => {
    setActiveContact(contact)
    setSelected(null)
    setShowClientCard(false)
      setUnreadCounts(prev => {
        const next = new Map(prev)
        next.set(contact.key, 0)
        return next
      })
      const msgs = allMessages.filter((m) => msgMatch(m, contact.channel, contact.senderId))
    if (msgs.length > 0) {
      const sorted = msgs.sort(
        (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      )
      setSelected(sorted[0])
    }
  }, [allMessages])

  const handleSelectMessage = useCallback((msg: Message) => {
    setSelected(prev => prev?.id === msg.id ? null : msg)
    setShowClientCard(false)
  }, [])

  if (!backendOk) {
    return (
      <div className="mx-auto max-w-2xl py-20 text-center">
        <p className="text-lg text-red-500">Сервер недоступен</p>
        <p className="mt-1 text-sm text-gray-400">Проверьте, запущен ли бэкенд</p>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="relative z-10 flex w-80 shrink-0 flex-col bg-white shadow-sm">
        <div className="border-b border-gray-200 bg-gray-800 px-4 py-4 text-white">
          <h1 className="text-lg font-bold">Омниканал</h1>
          <p className="mt-0.5 text-xs text-gray-300">{contacts.length} контактов</p>
        </div>
        <div className="min-h-0 flex-1 overflow-hidden">
          <ContactList
            contacts={contacts}
            activeKey={activeContact?.key ?? null}
            activeChannel={activeContact?.channel ?? null}
            unreadCounts={unreadCounts}
            onSelect={handleSelectContact}
          />
        </div>
      </div>

      <div className="flex flex-1 flex-col bg-white shadow-sm">
        {activeContact ? (
          <>
            {showClientCard && activeContact.clientId && (
              <div className="border-b border-gray-200 px-4 py-2">
                <ClientCard
                  channel={activeContact.channel}
                  senderId={activeContact.senderId}
                  onClose={() => setShowClientCard(false)}
                />
              </div>
            )}
            <div className="flex items-center justify-between border-b border-gray-200 bg-gray-50 px-4 py-2">
              <div className="flex items-center gap-2">
                {activeContact.avatarUrl ? (
                  <img src={activeContact.avatarUrl} alt="" className="h-8 w-8 rounded-full object-cover" />
                ) : (
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-600">
                    {activeContact.name.charAt(0).toUpperCase()}
                  </div>
                )}
                <div>
                  <p className="text-sm font-semibold text-gray-800">{activeContact.name}</p>
                  <p className="text-[10px] text-gray-400">{activeContact.channel}</p>
                </div>
              </div>
              {activeContact.clientId && (
                <button
                  className="rounded-lg bg-white px-3 py-1.5 text-xs font-medium text-gray-600 shadow-sm ring-1 ring-gray-200 transition hover:bg-gray-50"
                  onClick={() => setShowClientCard(!showClientCard)}
                >
                  {showClientCard ? 'Закрыть профиль' : 'Профиль'}
                </button>
              )}
            </div>
            <div className="flex-1 overflow-y-auto px-4">
              <MessageList
                messages={filteredMessages}
                loading={loading}
                selectedId={selected?.id ?? null}
                onSelect={handleSelectMessage}
              />
            </div>
            {selected?.channel === 'email' ? (
              <EmailReplyForm replyTarget={selected} onSent={() => {}} />
            ) : (
              <ChatInput replyTarget={selected} onSent={() => {}} />
            )}
          </>
        ) : (
          <div className="flex flex-1 items-center justify-center">
            <div className="text-center">
              <p className="text-lg text-gray-400">Выберите контакт</p>
              <p className="mt-1 text-sm text-gray-300">Чтобы начать переписку</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function findClientForMessage(msg: Message, clients: Map<string, Client>): Client | null {
  const matchEmail = msg.sender_id.match(/<([^>]+)>/)
  const lookupId = matchEmail ? matchEmail[1] : msg.sender_id
  for (const client of clients.values()) {
    for (const ch of client.channels) {
      if (ch.channel === msg.channel && ch.external_id === lookupId) {
        return client
      }
    }
  }
  return null
}
