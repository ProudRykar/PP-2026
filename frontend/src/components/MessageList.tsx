import { useEffect, useRef } from 'react'
import type { Message } from '../types'
import { ChatGroup } from './ChatGroup'
import { EmailCard } from './EmailCard'

interface MessageListProps {
  messages: Message[]
  loading: boolean
  selectedId: string | null
  onSelect: (msg: Message) => void
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

function senderLabel(msg: Message): string {
  if (msg.sender_id.startsWith('telegram:') || !isNaN(Number(msg.sender_id))) {
    return `User ${msg.sender_id.slice(0, 6)}`
  }
  return msg.sender_id.split('@')[0]
}

function channelLabel(msg: Message): string {
  return msg.channel.charAt(0).toUpperCase() + msg.channel.slice(1)
}

export function MessageList({ messages, loading, selectedId, onSelect }: MessageListProps) {
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
    return <p className="py-10 text-center text-gray-400">Загрузка сообщений…</p>
  }
  if (messages.length === 0) {
    return <p className="py-10 text-center text-gray-400">Нет сообщений</p>
  }

  const chatMessages = messages.filter(m => m.channel !== 'email')
  const emailMessages = messages.filter(m => m.channel === 'email')

  const chatGroups = groupBySender(chatMessages)

  return (
    <div className="flex flex-col pb-4">
      {chatGroups.map((group, gi) => (
        <ChatGroup
          key={`chat-${group[0].sender_id}-${gi}`}
          messages={group}
          senderLabel={senderLabel(group[0])}
          channelLabel={channelLabel(group[0])}
          selectedId={selectedId}
          onSelect={onSelect}
        />
      ))}
      {emailMessages.length > 0 && (
        <div className="mx-2 my-2 overflow-hidden rounded-xl border border-gray-200 shadow-sm">
          <table className="w-full table-fixed text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-500">
                <th className="w-[22%] px-3 py-2">Отправитель</th>
                <th className="w-[25%] px-3 py-2">Тема</th>
                <th className="px-3 py-2">Содержание</th>
                <th className="w-[18%] px-3 py-2 text-right">Время</th>
              </tr>
            </thead>
            <tbody>
              {emailMessages.map(msg => (
                <EmailCard
                  key={msg.id}
                  message={msg}
                  selected={selectedId === msg.id}
                  onSelect={onSelect}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  )
}
