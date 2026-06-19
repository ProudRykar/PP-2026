import { useState, useRef, useEffect, useCallback } from 'react'

export interface ContactChannel {
  channel: string
  senderId: string
  username?: string
}

export interface Contact {
  key: string
  name: string
  channel: string
  senderId: string
  channels: ContactChannel[]
  clientId: string | null
  avatarUrl: string | null
  lastMessage: string
  lastTimestamp: string
}

interface ContactListProps {
  contacts: Contact[]
  activeKey: string | null
  activeChannel: string | null
  unreadCounts: Map<string, number>
  onSelect: (contact: Contact) => void
}

function totalUnread(contact: Contact, counts: Map<string, number>): number {
  let total = 0
  for (const ch of contact.channels) {
    total += counts.get(`${ch.channel}:${ch.senderId}`) || 0
  }
  return total
}

const channelIcons: Record<string, string> = {
  telegram: '✈️',
  email: '📧',
  whatsapp: '💬',
  vk: '🌐',
}

const channelBadge: Record<string, { label: string; bg: string; text: string }> = {
  telegram: { label: 'Telegram', bg: 'bg-blue-100', text: 'text-blue-700' },
  email: { label: 'Email', bg: 'bg-amber-100', text: 'text-amber-700' },
  whatsapp: { label: 'WhatsApp', bg: 'bg-green-100', text: 'text-green-700' },
  vk: { label: 'VK', bg: 'bg-sky-100', text: 'text-sky-700' },
}

function formatTime(ts: string): string {
  const d = new Date(ts)
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffDays = Math.floor(diffMs / 86400000)
  if (diffDays === 0) return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  if (diffDays === 1) return 'вчера'
  if (diffDays < 7) return d.toLocaleDateString('ru-RU', { weekday: 'short' })
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

type SortMode = 'time_desc' | 'time_asc' | 'name_asc' | 'name_desc'

export function ContactList({ contacts, activeKey, activeChannel, unreadCounts, onSelect }: ContactListProps) {
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState<SortMode>('time_desc')
  const [unreadOnly, setUnreadOnly] = useState(false)
  const [channelFilter, setChannelFilter] = useState<string | null>(null)
  const [menuOpen, setMenuOpen] = useState(false)
  const [menuPos, setMenuPos] = useState({ top: 0, left: 0 })
  const btnRef = useRef<HTMLButtonElement>(null)
  const menuRef = useRef<HTMLDivElement>(null)
  const [expandedKeys, setExpandedKeys] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (!menuOpen) return
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node) &&
          btnRef.current && !btnRef.current.contains(e.target as Node)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [menuOpen])

  const toggleMenu = () => {
    if (menuOpen) {
      setMenuOpen(false)
    } else {
      const rect = btnRef.current?.getBoundingClientRect()
      if (rect) {
        setMenuPos({ top: rect.bottom + 4, left: rect.left })
      }
      setMenuOpen(true)
    }
  }

  const toggleExpand = (key: string) => {
    setExpandedKeys(prev => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }

  const channels = [...new Set(contacts.flatMap(c => c.channels.map(ch => ch.channel)))]

  const hasActiveFilters = unreadOnly || channelFilter !== null || sortBy !== 'time_desc'

  const unreadTotal = useCallback((c: Contact) => totalUnread(c, unreadCounts), [unreadCounts])

  const processed = contacts
    .filter(c => !search || c.name.toLowerCase().includes(search.toLowerCase()))
    .filter(c => !unreadOnly || unreadTotal(c) > 0)
    .filter(c => !channelFilter || c.channels.some(ch => ch.channel === channelFilter))
    .sort((a, b) => {
      const aUnread = unreadTotal(a) > 0
      const bUnread = unreadTotal(b) > 0
      if (aUnread !== bUnread) return aUnread ? -1 : 1
      switch (sortBy) {
        case 'time_asc': return new Date(a.lastTimestamp).getTime() - new Date(b.lastTimestamp).getTime()
        case 'name_asc': return a.name.localeCompare(b.name)
        case 'name_desc': return b.name.localeCompare(a.name)
        default: return new Date(b.lastTimestamp).getTime() - new Date(a.lastTimestamp).getTime()
      }
    })

  function renderContact(contact: Contact) {
    const isMulti = contact.channels.length > 1
    const expanded = expandedKeys.has(contact.key)

    return (
      <div key={contact.clientId ?? contact.key}>
        <button
          className={`flex w-full items-center gap-3 border-b border-gray-50 px-3 py-3 text-left transition hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-700/50 ${
            activeKey === contact.key ? 'bg-blue-50 dark:bg-blue-900/30' : ''
          }`}
          onClick={() => {
            if (isMulti) toggleExpand(contact.key)
            else onSelect(contact)
          }}
        >
          {contact.avatarUrl ? (
            <img src={contact.avatarUrl} alt="" className="h-11 w-11 shrink-0 rounded-full object-cover" />
          ) : (
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-600 dark:bg-blue-900 dark:text-blue-300">
              {contact.name.charAt(0).toUpperCase()}
            </div>
          )}
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1">
              {contact.channels.map((ch) => {
                const b = channelBadge[ch.channel]
                return b ? (
                  <span
                    key={ch.channel}
                    className={`inline-flex items-center rounded px-1.5 py-0.5 text-[10px] font-medium ${b.bg} ${b.text}`}
                  >
                    {b.label}
                  </span>
                ) : (
                  <span key={ch.channel} className="inline-flex items-center rounded bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-600 dark:bg-gray-700 dark:text-gray-400">
                    {ch.channel}
                  </span>
                )
              })}
            </div>
            <div className="flex items-center justify-between">
              <span className="truncate text-sm font-medium text-gray-900 dark:text-gray-100">{contact.name}</span>
              <div className="flex shrink-0 items-center gap-1.5 pl-2">
                {(() => {
                  const cnt = totalUnread(contact, unreadCounts)
                  return cnt > 0 ? (
                    <span className="flex h-5 min-w-[20px] items-center justify-center rounded-full bg-blue-500 px-1.5 text-[10px] font-bold text-white">
                      {cnt > 99 ? '99+' : cnt}
                    </span>
                  ) : null
                })()}
                {contact.lastTimestamp && (
                  <span className="text-[10px] text-gray-400 dark:text-gray-500">{formatTime(contact.lastTimestamp)}</span>
                )}
              </div>
            </div>
            <div className="mt-0.5 flex items-center gap-1.5">
              <span className="truncate text-xs text-gray-500 dark:text-gray-400">{contact.lastMessage || 'Нет сообщений'}</span>
            </div>
          </div>
          {isMulti && (
            <svg
              className={`h-4 w-4 shrink-0 text-gray-400 transition-transform dark:text-gray-500 ${expanded ? 'rotate-90' : ''}`}
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          )}
        </button>

        {isMulti && expanded && (
          <div className="border-b border-gray-50 bg-gray-50/50 dark:border-gray-700 dark:bg-gray-800/50">
            {contact.channels.map((ch) => {
              const b = channelBadge[ch.channel]
              return (
                <button
                  key={ch.channel}
                  className={`flex w-full items-center gap-3 py-2.5 pl-14 pr-3 text-left text-sm transition hover:bg-gray-100 dark:hover:bg-gray-700 ${
                    activeKey === contact.key && activeChannel === ch.channel ? 'bg-blue-50 dark:bg-blue-900/30' : ''
                  }`}
                  onClick={() => onSelect({ ...contact, channel: ch.channel, senderId: ch.senderId })}
                >
                  <span>{channelIcons[ch.channel] || '🔗'}</span>
                  <span className="font-medium text-gray-700 dark:text-gray-300">{b?.label ?? ch.channel}</span>
                  {(() => {
                    const chCnt = unreadCounts.get(`${ch.channel}:${ch.senderId}`) || 0
                    return chCnt > 0 ? (
                      <span className="flex h-4 min-w-[16px] items-center justify-center rounded-full bg-blue-500 px-1 text-[9px] font-bold text-white">
                        {chCnt > 99 ? '99+' : chCnt}
                      </span>
                    ) : null
                  })()}
                  <span className="ml-auto text-[10px] text-gray-400 dark:text-gray-500">{ch.channel === 'telegram' && ch.username ? `@${ch.username}` : ch.senderId}</span>
                </button>
              )
            })}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col border-r border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      <div className="border-b border-gray-200 px-3 py-3 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <input
            className="flex-1 rounded-lg bg-gray-100 px-3 py-2 text-sm outline-none transition focus:bg-gray-50 focus:ring-2 focus:ring-blue-100 dark:bg-gray-700 dark:text-gray-100 dark:focus:bg-gray-600"
            placeholder="Поиск контактов..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <div className="shrink-0">
            <button
              ref={btnRef}
              className={`flex h-9 w-9 items-center justify-center rounded-lg transition ${
                hasActiveFilters
                  ? 'bg-blue-100 text-blue-600 hover:bg-blue-200 dark:bg-blue-900/50 dark:text-blue-300'
                  : 'bg-gray-100 text-gray-500 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-400 dark:hover:bg-gray-600'
              }`}
              onClick={toggleMenu}
              title="Фильтры и сортировка"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
            </button>

            {menuOpen && (
              <div
                ref={menuRef}
                className="fixed z-50 flex gap-0 rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-600 dark:bg-gray-800"
                style={{ top: menuPos.top, left: menuPos.left }}
              >
                <div className="py-2">
                  <label className="flex cursor-pointer items-center gap-2 px-3 py-1.5 text-sm text-gray-700 transition hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700">
                    <input
                      type="checkbox"
                      className="h-4 w-4 accent-blue-500"
                      checked={unreadOnly}
                      onChange={e => setUnreadOnly(e.target.checked)}
                    />
                    Непрочитанные
                  </label>

                  <div className="my-1 border-t border-gray-100 dark:border-gray-700" />

                  <p className="px-3 pb-1 text-[10px] font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Сортировка</p>
                  {([['time_desc', 'Новые ↑'], ['time_asc', 'Старые ↓'], ['name_asc', 'А→Я'], ['name_desc', 'Я→А']] as const).map(([val, label]) => (
                    <button
                      key={val}
                      className={`flex w-full items-center gap-2 whitespace-nowrap px-3 py-1.5 text-left text-sm transition ${
                        sortBy === val ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-300' : 'text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
                      }`}
                      onClick={() => { setSortBy(val); setMenuOpen(false) }}
                    >
                      {sortBy === val && (
                        <svg className="h-3.5 w-3.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                      <span className={sortBy === val ? '' : 'ml-7'}>{label}</span>
                    </button>
                  ))}
                </div>

                <div className="w-px bg-gray-200 dark:bg-gray-700" />

                <div className="py-2">
                  <p className="px-3 pb-1 text-[10px] font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Канал</p>
                  <button
                    className={`flex w-full items-center gap-2 whitespace-nowrap px-3 py-1.5 text-left text-sm transition ${
                      channelFilter === null ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-300' : 'text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
                    }`}
                    onClick={() => { setChannelFilter(null); setMenuOpen(false) }}
                  >
                    {channelFilter === null && (
                      <svg className="h-3.5 w-3.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                    <span className={channelFilter === null ? '' : 'ml-7'}>Все каналы</span>
                  </button>
                  {channels.map(ch => (
                    <button
                      key={ch}
                      className={`flex w-full items-center gap-2 whitespace-nowrap px-3 py-1.5 text-left text-sm transition ${
                        channelFilter === ch ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-300' : 'text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
                      }`}
                      onClick={() => { setChannelFilter(ch); setMenuOpen(false) }}
                    >
                      {channelFilter === ch && (
                        <svg className="h-3.5 w-3.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                      <span className={channelFilter === ch ? '' : 'ml-7'}>{channelBadge[ch]?.label ?? ch}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {processed.length === 0 && (
          <p className="py-10 text-center text-xs text-gray-400 dark:text-gray-500">
            {search ? 'Ничего не найдено' : 'Нет контактов'}
          </p>
        )}
        {processed.map(c => renderContact(c))}
      </div>
    </div>
  )
}
