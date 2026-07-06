import { useEffect, useRef } from 'react'
import type { Message } from '../types'
import { ChatGroup } from './ChatGroup'
import { EmailCard } from './EmailCard'
import { DateSeparator } from './DateSeparator'

interface MessageListProps {
  messages: Message[]
  loading: boolean
  selectedId: string | null
  onSelect: (msg: Message) => void
  onReply?: (msg: Message) => void
  readMessageIds?: Set<string>
  curatorName?: string
}

function groupBySender(messages: Message[]): Message[][] {
  const groups: Message[][] = []
  for (const msg of messages) {
    const last = groups[groups.length - 1]
    if (last && last[0].sender_id === msg.sender_id) {
      last.push(msg)
    } else {
      groups.push([msg])
    }
  }
  return groups
}

function senderLabel(msg: Message, ownName?: string): string {
  if (msg.sender_id === "agent") return ownName || "Agent"
  if (msg.sender_id.startsWith('telegram:') || !isNaN(Number(msg.sender_id))) {
    return `User ${msg.sender_id.slice(0, 6)}`
  }
  return msg.sender_id.split('@')[0]
}

function channelLabel(msg: Message): string {
  return msg.channel.charAt(0).toUpperCase() + msg.channel.slice(1)
}

function formatDate(date: Date): string {
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function buildRenderItems(groups: Message[][]) {
  const items: Array<{ type: 'group' | 'separator'; messages?: Message[]; date?: string; key: string }> = []
  let prevDateKey = ''
  for (let gi = 0; gi < groups.length; gi++) {
    const g = groups[gi]
    if (!g.length) continue
    const dateKey = new Date(g[0].timestamp).toDateString()
    if (!prevDateKey || dateKey !== prevDateKey) {
      items.push({ type: 'separator', date: formatDate(new Date(g[0].timestamp)), key: `sep-${dateKey}` })
    }
    prevDateKey = dateKey
    items.push({ type: 'group', messages: g, key: `group-${gi}` })
  }
  return items
}

function buildEmailThreads(messages: Message[]): Message[][] {
  const sorted = [...messages].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  )
  const children = new Map<string, Message[]>()
  const roots: Message[] = []
  const ids = new Set(sorted.map(m => m.id))

  for (const msg of sorted) {
    if (msg.parent_id && ids.has(msg.parent_id)) {
      const list = children.get(msg.parent_id) ?? []
      list.push(msg)
      children.set(msg.parent_id, list)
    } else {
      roots.push(msg)
    }
  }

  return roots.map(root => [root, ...(children.get(root.id) ?? [])])
}

export function MessageList({ messages, loading, selectedId, onSelect, onReply, readMessageIds, curatorName }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)
  const isNearBottomRef = useRef(true)

  useEffect(() => {
    const el = bottomRef.current
    if (!el) return
    let parent = el.parentElement
    while (parent) {
      const style = getComputedStyle(parent)
      if (style.overflowY === 'auto' || style.overflowY === 'scroll') break
      parent = parent.parentElement
    }
    if (!parent) return

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = parent
      isNearBottomRef.current = scrollHeight - scrollTop - clientHeight < 150
    }

    parent.addEventListener('scroll', handleScroll, { passive: true })
    handleScroll()
    return () => parent.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    if (isNearBottomRef.current) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  if (loading) {
    return <p className="py-10 text-center text-gray-400 dark:text-gray-500">Загрузка сообщений…</p>
  }
  if (messages.length === 0) {
    return <p className="py-10 text-center text-gray-400 dark:text-gray-500">Нет сообщений</p>
  }

  const chatMessages = messages.filter(m => m.channel !== 'email')
  const emailMessages = messages.filter(m => m.channel === 'email')

  const chatGroups = groupBySender(chatMessages)
  const emailThreads = buildEmailThreads(emailMessages)

  const renderItems = buildRenderItems(chatGroups)

  return (
    <div className="flex flex-col pb-4">
      {renderItems.map(item =>
        item.type === 'separator'
          ? <DateSeparator key={item.key} date={item.date!} />
          : <ChatGroup
              key={item.key}
              messages={item.messages!}
              senderLabel={senderLabel(item.messages![0], curatorName)}
              channelLabel={channelLabel(item.messages![0])}
              selectedId={selectedId}
              onSelect={onSelect}
              onReply={onReply}
            />
      )}
      {emailThreads.length > 0 && (
        <div className="mx-2 my-2 space-y-2">
          {emailThreads.map((thread, ti) => (
            <div
              key={`thread-${ti}`}
              className="overflow-hidden rounded-xl border border-gray-200 shadow-sm dark:border-gray-700"
            >
              {thread.map((msg, mi) => (
                <EmailCard
                  key={msg.id}
                  message={msg}
                  selected={selectedId === msg.id}
                  onSelect={onSelect}
                  depth={mi}
                  unread={!readMessageIds?.has(msg.id)}
                />
              ))}
            </div>
          ))}
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  )
}
