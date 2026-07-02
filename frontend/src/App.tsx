import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import type { Message, Client, Curator } from './types'
import { fetchMessages, fetchChannels, fetchHealth, fetchAllClients, fetchCurators as apiFetchCurators, assignCurator, transferCurator, fetchCuratorAssignments } from './api'
import { MessageList } from './components/MessageList'
import { ChatInput } from './components/ChatInput'
import { EmailReplyForm } from './components/EmailReplyForm'
import { Avatar } from './components/Avatar'
import { ClientCard } from './components/ClientCard'
import { ContactList, type Contact, type ContactChannel } from './components/ContactList'
import { ThemeToggle } from './components/ThemeToggle'
import { Footer } from './components/Footer'
import { useWebSocket } from './hooks/useWebSocket'
import { LoginPage } from './components/LoginPage'
import { RegisterPage } from './components/RegisterPage'
import { useAuth } from './hooks/AuthContext'

export default function App() {
  const { isAuthenticated, loading: authLoading, curator, logout } = useAuth()
  const [showRegister, setShowRegister] = useState(false)

  const [allMessages, setAllMessages] = useState<Message[]>([])
  const [clients, setClients] = useState<Map<string, Client>>(new Map())
  const [backendOk, setBackendOk] = useState(true)
  const [selected, setSelected] = useState<Message | null>(null)
  const [activeContact, setActiveContact] = useState<Contact | null>(null)

  const [curators, setCurators] = useState<Curator[]>([])
  const [showClientCard, setShowClientCard] = useState(false)
  const [unreadCounts, setUnreadCounts] = useState<Map<string, number>>(new Map())
  const [readMessageIds, setReadMessageIds] = useState<Set<string>>(new Set())
  const countedUnreadRef = useRef(new Set<string>())
  const [delegationNotif, setDelegationNotif] = useState<{ fromName: string; entryId: string; clientName: string; channel: string }[] | null>(null)
  const shownDelegationsRef = useRef(new Set<string>())
  const [delegatedContactKeys, setDelegatedContactKeys] = useState<Set<string>>(new Set())
  const [showDelegatePopup, setShowDelegatePopup] = useState(false)
  const [pendingAction, setPendingAction] = useState<string | null>(null)

  console.debug('[App] render:', { isAuthenticated, authLoading, curator: curator?.full_name, msgs: allMessages.length, backendOk })

  useEffect(() => {
    console.debug('[App] data useEffect fired:', { isAuthenticated, authLoading })
    if (!isAuthenticated) return
    let cancelled = false
    ;(async () => {
      try {
        console.debug('[App] starting data load...')
        const [healthOk, channelsOk, curators, [msgs, cls]] = await Promise.all([
          fetchHealth().then(() => { console.debug('[App] health ok'); return true }).catch(e => { console.debug('[App] health fail:', e); return false }),
          fetchChannels().then(() => { console.debug('[App] channels ok'); return true }).catch(e => { console.debug('[App] channels fail:', e); return false }),
          apiFetchCurators().catch(e => { console.debug('[App] curators fail:', e); return [] }),
          Promise.all([
            fetchMessages().catch(e => { console.debug('[App] messages fail:', e); throw e }),
            fetchAllClients().catch(e => { console.debug('[App] clients fail:', e); throw e }),
          ]),
        ])
        if (cancelled) { console.debug('[App] cancelled after load'); return }
        console.debug('[App] data loaded:', { msgs: msgs?.length, clients: cls?.length, curators: curators?.length, healthOk, channelsOk })
        if (!healthOk || !channelsOk) { setBackendOk(false); return }
        setBackendOk(true)
        setCurators(curators)
        setAllMessages(msgs)
        setReadMessageIds(new Set(msgs.map(m => m.id)))
        countedUnreadRef.current = new Set(msgs.map(m => m.id))
        const map = new Map<string, Client>()
        for (const c of cls) map.set(c.id, c)
        setClients(map)
        if (curator) {
          try {
            const history = await fetchCuratorAssignments(curator.id)
            const seen = new Set(JSON.parse(localStorage.getItem('seen_delegations') ?? '[]'))
            for (const id of shownDelegationsRef.current) seen.add(id)
            const unseen = history
              .filter(e => e.to_curator_id === curator.id && e.from_curator_id && !seen.has(e.id))
              .sort((a, b) => new Date(b.created_at!).getTime() - new Date(a.created_at!).getTime())
            const delegatedKeys = new Set<string>()
            if (unseen.length > 0) {
              const items: { fromName: string; entryId: string; clientName: string; channel: string }[] = []
              for (const e of unseen) {
                seen.add(e.id)
                shownDelegationsRef.current.add(e.id)
                const fromCurator = curators.find(c => c.id === e.from_curator_id)
                const msg = msgs.find(m => m.id === e.message_id)
                const client = msg ? findClientForMessage(msg, map) : null
                if (msg) delegatedKeys.add(convKey(msg))
                items.push({
                  fromName: fromCurator?.full_name ?? 'Куратор',
                  entryId: e.id,
                  clientName: clientDisplayName(msg, client),
                  channel: msg?.channel ?? '',
                })
              }
              localStorage.setItem('seen_delegations', JSON.stringify([...seen]))
              setDelegationNotif(items)
            }
            setDelegatedContactKeys(delegatedKeys)
            if (delegatedKeys.size > 0) {
              setUnreadCounts(prev => {
                const next = new Map(prev)
                for (const key of delegatedKeys) {
                  if (!next.get(key)) next.set(key, 1)
                }
                return next
              })
            }
          } catch {}
        }
      } catch (e) {
        console.debug('[App] data load error:', e)
        if (!cancelled) setBackendOk(false)
      }
    })()
    return () => { console.debug('[App] data effect cleanup'); cancelled = true }
  }, [isAuthenticated, curator])

  useWebSocket((data) => {
    const ev = data as Record<string, unknown>
    if (ev.type === 'new_message' && typeof ev.id === 'string') {
      const msg = ev as unknown as Message

      setAllMessages(prev => {
        if (prev.some(m => m.id === msg.id)) return prev
        return [...prev, msg]
      })

      if (msg.sender_id !== 'agent') {
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
      } else {
        setReadMessageIds(prev => {
          if (prev.has(msg.id)) return prev
          const next = new Set(prev)
          next.add(msg.id)
          return next
        })
      }

      fetchAllClients().then(cls => {
        const map = new Map<string, Client>()
        for (const c of cls) map.set(c.id, c)
        setClients(map)
      }).catch(() => {})
    }

    if (ev.type === 'curator_assigned' && typeof ev.message_id === 'string') {
      console.debug('[WS] curator_assigned:', ev)
      setAllMessages(prev => prev.map(m =>
        m.id === ev.message_id ? { ...m, curator_id: ev.curator_id as string } : m
      ))
      if (curator && ev.curator_id === curator.id && ev.assigned_by && ev.assigned_by !== curator.id) {
        const assignerId = ev.assigned_by as string
        const assigner = curators.find(c => c.id === assignerId)
        if (assigner) {
          const eid = (ev.assignment_id as string) ?? ev.message_id as string
          if (shownDelegationsRef.current.has(eid)) return
          shownDelegationsRef.current.add(eid)
          const seen = new Set(JSON.parse(localStorage.getItem('seen_delegations') ?? '[]'))
          seen.add(eid)
          localStorage.setItem('seen_delegations', JSON.stringify([...seen]))
          const msg = allMessages.find(m => m.id === ev.message_id)
          const client = msg ? findClientForMessage(msg, clients) : null
          if (msg) {
            const key = convKey(msg)
            setDelegatedContactKeys(prev => new Set(prev).add(key))
            setUnreadCounts(prev => {
              if (prev.get(key) && prev.get(key)! > 0) return prev
              const next = new Map(prev)
              next.set(key, (next.get(key) || 0) + 1)
              return next
            })
          }
          setDelegationNotif(prev => {
            const item = { fromName: assigner.full_name, entryId: eid, clientName: clientDisplayName(msg, client), channel: msg?.channel ?? '' }
            if (prev === null) return [item]
            if (prev.some(d => d.entryId === eid)) return prev
            return [...prev, item]
          })
        }
      }
    }

    if (ev.type === 'curator_transferred' && typeof ev.message_id === 'string') {
      console.debug('[WS] curator_transferred:', ev)
      setAllMessages(prev => prev.map(m =>
        m.id === ev.message_id ? { ...m, curator_id: ev.curator_id as string } : m
      ))
      if (curator && ev.to_curator_id === curator.id) {
        const fromId = ev.from_curator_id as string
        const fromCurator = curators.find(c => c.id === fromId)
        if (fromCurator) {
          const eid = (ev.assignment_id as string) ?? ev.message_id as string
          if (shownDelegationsRef.current.has(eid)) return
          shownDelegationsRef.current.add(eid)
          const seen = new Set(JSON.parse(localStorage.getItem('seen_delegations') ?? '[]'))
          seen.add(eid)
          localStorage.setItem('seen_delegations', JSON.stringify([...seen]))
          const msg = allMessages.find(m => m.id === ev.message_id)
          const client = msg ? findClientForMessage(msg, clients) : null
          if (msg) {
            const key = convKey(msg)
            setDelegatedContactKeys(prev => new Set(prev).add(key))
            setUnreadCounts(prev => {
              if (prev.get(key) && prev.get(key)! > 0) return prev
              const next = new Map(prev)
              next.set(key, (next.get(key) || 0) + 1)
              return next
            })
          }
          setDelegationNotif(prev => {
            const item = { fromName: fromCurator.full_name, entryId: eid, clientName: clientDisplayName(msg, client), channel: msg?.channel ?? '' }
            if (prev === null) return [item]
            if (prev.some(d => d.entryId === eid)) return prev
            return [...prev, item]
          })
        }
      } else if (curator && ev.from_curator_id === curator.id) {
        const msg = allMessages.find(m => m.id === ev.message_id)
        if (msg) setDelegatedContactKeys(prev => {
          const next = new Set(prev)
          next.delete(convKey(msg))
          return next
        })
      }
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

  function msgMatch(msg: Message, channel: string, senderId: string): boolean {
    if (msg.channel !== channel) return false
    if (msg.sender_id === 'agent') return msg.recipient === senderId
    return extractId(msg.sender_id) === senderId
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

  const filteredMessages = useMemo(() => {
    if (!activeContact) return []
    const msgs = allMessages.filter((m) => msgMatch(m, activeContact.channel, activeContact.senderId))
    return msgs.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
  }, [activeContact, allMessages])

  const markRead = useCallback((id: string) => {
    setReadMessageIds(prev => {
      if (prev.has(id)) return prev
      const next = new Set(prev)
      next.add(id)
      return next
    })
  }, [])

  const handleSelectContact = useCallback((contact: Contact) => {
    setActiveContact(contact)
    setSelected(null)
    setShowClientCard(false)
    setUnreadCounts(prev => {
      const next = new Map(prev)
      for (const ch of contact.channels) {
        next.set(`${ch.channel}:${ch.senderId}`, 0)
      }
      return next
    })
    setReadMessageIds(prev => {
      const next = new Set(prev)
      for (const m of allMessages) {
        for (const ch of contact.channels) {
          if (msgMatch(m, ch.channel, ch.senderId)) next.add(m.id)
        }
      }
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
    markRead(msg.id)
    setShowClientCard(false)
  }, [markRead])

  const handleReplyMessage = useCallback((msg: Message) => {
    setSelected(msg)
    markRead(msg.id)
    setShowClientCard(false)
  }, [markRead])

  const handleTakeTicket = useCallback(async (messageId: string) => {
    if (!curator || pendingAction) return
    setPendingAction(messageId)
    try {
      await assignCurator(messageId, { curator_id: curator.id })
      setAllMessages(prev => prev.map(m =>
        m.id === messageId ? { ...m, curator_id: curator.id } : m
      ))
      setSelected(prev => prev?.id === messageId ? { ...prev, curator_id: curator.id } : prev)
    } catch (e) {
      console.error('[App] take ticket failed:', e)
    } finally {
      setPendingAction(null)
    }
  }, [curator, pendingAction])

  const handleDelegate = useCallback(async (messageId: string, toCuratorId: string) => {
    if (!curator || pendingAction) return
    setPendingAction(messageId)
    try {
      await transferCurator(messageId, { from_curator_id: curator.id, to_curator_id: toCuratorId })
      setAllMessages(prev => prev.map(m =>
        m.id === messageId ? { ...m, curator_id: toCuratorId } : m
      ))
      setSelected(prev => prev?.id === messageId ? { ...prev, curator_id: toCuratorId } : prev)
    } catch (e) {
      console.error('[App] delegate failed:', e)
    } finally {
      setPendingAction(null)
    }
  }, [curator, pendingAction])

  useEffect(() => {
    if (!showDelegatePopup) return
    const close = () => setShowDelegatePopup(false)
    document.addEventListener('click', close)
    return () => document.removeEventListener('click', close)
  }, [showDelegatePopup])

  if (!isAuthenticated) {
    if (authLoading) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-gray-100 dark:bg-gray-950">
          <p className="text-gray-400">Загрузка...</p>
        </div>
      )
    }
    if (showRegister) {
      return <RegisterPage onSwitchToLogin={() => setShowRegister(false)} />
    }
    return <LoginPage onSwitchToRegister={() => setShowRegister(true)} />
  }

  if (!backendOk) {
    return (
      <div className="mx-auto max-w-2xl py-20 text-center">
        <p className="text-lg text-red-500">Сервер недоступен</p>
        <p className="mt-1 text-sm text-gray-400 dark:text-gray-500">Проверьте, запущен ли бэкенд</p>
      </div>
    )
  }

  return (
    <div className="flex h-screen flex-col bg-gray-100 dark:bg-gray-950">
      <div className="flex items-center justify-between border-b border-gray-200 bg-gray-800 px-4 py-3 text-white dark:border-gray-700 shrink-0">
        <div className="min-w-0">
          <h1 className="text-lg font-bold">Омниканал</h1>
          <p className="mt-0.5 text-xs text-gray-300">{contacts.length} контактов</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <div className="hidden truncate text-right text-xs text-gray-300 sm:block">
            <p className="font-medium text-white">{curator?.full_name}</p>
            <p className="text-gray-400">{curator?.role}</p>
          </div>
          <button
            onClick={logout}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-300 transition hover:bg-gray-700 hover:text-white"
            title="Выйти"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
          <ThemeToggle />
        </div>
      </div>
      <div className="flex flex-1 overflow-hidden">
        <div className="relative z-10 flex w-80 shrink-0 flex-col bg-white shadow-sm dark:bg-gray-800">
        <div className="min-h-0 flex-1 overflow-hidden">
          <ContactList
            contacts={contacts}
            activeKey={activeContact?.key ?? null}
            activeChannel={activeContact?.channel ?? null}
            unreadCounts={unreadCounts}
            delegatedKeys={delegatedContactKeys}
            onSelect={handleSelectContact}
          />
        </div>
        <Footer curatorName={curator?.full_name} curatorRole={curator?.role} />
      </div>

      <div className="flex flex-1 flex-col bg-white shadow-sm dark:bg-gray-900">
        {activeContact ? (
          <>
            {showClientCard && activeContact.clientId && (
              <div className="border-b border-gray-200 px-4 py-2 dark:border-gray-700">
                <ClientCard
                  channel={activeContact.channel}
                  senderId={activeContact.senderId}
                  onClose={() => setShowClientCard(false)}
                  messageCuratorId={selected?.curator_id ?? null}
                />
              </div>
            )}
            <div className="border-b border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-800">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Avatar name={activeContact.name} size="sm" />
                  <div>
                    <p className="text-base font-semibold text-gray-800 dark:text-gray-100">{activeContact.name}</p>
                    <p className="text-xs text-gray-400 dark:text-gray-500">{activeContact.channel}</p>
                  </div>
                </div>
                {activeContact.clientId && (
                  <button
                    className="rounded-lg bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm ring-1 ring-gray-200 transition hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:ring-gray-600 dark:hover:bg-gray-600"
                    onClick={() => setShowClientCard(!showClientCard)}
                  >
                    {showClientCard ? 'Закрыть профиль' : 'Профиль'}
                  </button>
                )}
              </div>
              <div className="mt-2 flex items-center gap-2">
                {(() => {
                  const msgCur = selected?.curator_id ?? null
                  const isMyTicket = msgCur && msgCur === curator?.id
                  const canTake = !!selected && !isMyTicket && !!curator?.id
                  if (!selected) return null
                  if (!isMyTicket) {
                    const loading = pendingAction === selected.id
                    return (
                      <button
                        className="rounded bg-blue-600 px-3 py-1 text-xs text-white hover:bg-blue-700 disabled:opacity-50 dark:bg-blue-700 dark:hover:bg-blue-600"
                        disabled={!canTake || !!pendingAction}
                        onClick={() => handleTakeTicket(selected.id)}
                      >
                        {loading ? '...' : 'Взять обращение'}
                      </button>
                    )
                  }
                  return (
                    <div className="relative">
                      <button
                        className="rounded bg-green-600 px-3 py-1 text-xs text-white hover:bg-green-700 disabled:opacity-50 dark:bg-green-700 dark:hover:bg-green-600"
                        disabled={!!pendingAction}
                        onClick={(e) => { e.stopPropagation(); setShowDelegatePopup(true) }}
                      >
                        Делегировать
                      </button>
                      {showDelegatePopup && (
                        <div
                          className="absolute left-0 z-10 mt-1 max-h-32 w-48 overflow-y-auto rounded-lg border bg-white p-1 shadow-lg dark:border-gray-600 dark:bg-gray-800"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {curators.filter(c => c.id !== curator?.id && c.status === 'active').map(c => (
                            <button
                              key={c.id}
                              className="block w-full rounded px-2 py-1 text-left text-xs hover:bg-gray-100 dark:hover:bg-gray-700"
                              onClick={() => { handleDelegate(selected.id, c.id); setShowDelegatePopup(false) }}
                            >
                              {c.full_name}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  )
                })()}
              </div>
            </div>
            <div className="flex-1 overflow-y-auto px-4">
              <MessageList
                messages={filteredMessages}
                loading={authLoading}
                selectedId={selected?.id ?? null}
                onSelect={handleSelectMessage}
                onReply={handleReplyMessage}
                readMessageIds={readMessageIds}
                curatorName={curator?.full_name}
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
              <p className="text-lg text-gray-400 dark:text-gray-500">Выберите контакт</p>
              <p className="mt-1 text-sm text-gray-300 dark:text-gray-500">Чтобы начать переписку</p>
            </div>
          </div>
        )}
        </div>
      </div>
      {delegationNotif && delegationNotif.length > 0 && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setDelegationNotif(null)}>
          <div className="mx-4 w-full max-w-sm rounded-xl border border-green-200 bg-white p-6 shadow-xl dark:border-green-800 dark:bg-gray-800" onClick={(e) => e.stopPropagation()}>
            <div className="mb-4">
              <div className="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-green-100 text-2xl dark:bg-green-900">
                🔔
              </div>
              <p className="text-center text-base font-semibold text-gray-800 dark:text-gray-100">
                Новое делегирование{delegationNotif.length > 1 ? ` (${delegationNotif.length})` : ''}
              </p>
            </div>
            <div className="mb-4 max-h-48 space-y-2 overflow-y-auto">
              {delegationNotif.map(d => (
                <p key={d.entryId} className="text-sm text-gray-600 dark:text-gray-400">
                  {d.fromName} передал вам обращение от <span className="font-medium text-gray-800 dark:text-gray-200">{d.clientName}</span>
                  {d.channel && <span className="text-gray-400"> ({d.channel})</span>}
                </p>
              ))}
            </div>
            <button
              className="w-full rounded-lg bg-blue-600 py-2 text-sm font-medium text-white hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600"
              onClick={() => {
                const seen = new Set(JSON.parse(localStorage.getItem('seen_delegations') ?? '[]'))
                for (const d of delegationNotif) {
                  shownDelegationsRef.current.add(d.entryId)
                  seen.add(d.entryId)
                }
                localStorage.setItem('seen_delegations', JSON.stringify([...seen]))
                setDelegationNotif(null)
              }}
            >
              Ок
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function findClientForMessage(msg: Message, clients: Map<string, Client>): Client | null {
  const rawId = msg.sender_id === 'agent' ? (msg.recipient ?? msg.sender_id) : msg.sender_id
  const matchEmail = rawId.match(/<([^>]+)>/)
  const lookupId = matchEmail ? matchEmail[1] : rawId
  for (const client of clients.values()) {
    for (const ch of client.channels) {
      if (ch.channel === msg.channel && ch.external_id === lookupId) {
        return client
      }
    }
  }
  return null
}

function clientDisplayName(msg: Message | undefined, client: Client | null): string {
  if (client?.name) return client.name
  if (!msg) return 'пользователь'
  if (msg.sender_id === 'agent') return msg.recipient ?? 'пользователь'
  return msg.sender_id
}
