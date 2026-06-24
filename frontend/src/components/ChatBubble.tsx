import { useState, useEffect } from 'react'
import type { Message, Curator, AssignmentHistoryEntry } from '../types'
import { StickerRenderer } from './StickerRenderer'
import { normalizeFileUrl } from '../utils'
import { fetchCurators, fetchCurator, assignCurator, transferCurator, fetchAssignmentHistory } from '../api'
import { useAuth } from '../hooks/AuthContext'

interface ChatBubbleProps {
  message: Message
  isOwn: boolean
  isFirst: boolean
  isLast: boolean
  senderLabel: string
  channelLabel: string
  selected: boolean
  onSelect: (msg: Message) => void
}

export function ChatBubble({ message, isOwn, isFirst, isLast, senderLabel, channelLabel, selected, onSelect }: ChatBubbleProps) {
  const { curator: me } = useAuth()
  const [lightbox, setLightbox] = useState<{ url: string; isVideo: boolean } | null>(null)
  const [curators, setCurators] = useState<Curator[]>([])
  const [showAssign, setShowAssign] = useState(false)
  const [showTransfer, setShowTransfer] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [historyEntries, setHistoryEntries] = useState<AssignmentHistoryEntry[]>([])
  const [curatorName, setCuratorName] = useState<string | null>(null)
  const time = new Date(message.timestamp).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  const date = new Date(message.timestamp).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })

  const isAnimation = message.message_type === 'animation' && message.metadata?.file_url
  const isPhoto = message.message_type === 'photo' && message.metadata?.file_url
  const isDocument = message.message_type === 'document' && message.metadata?.file_url

  const getFileUrl = () => normalizeFileUrl(message.metadata!.file_url as string)
  const mimeType = message.metadata?.mime_type as string | undefined

  useEffect(() => {
    if (message.curator_id) {
      fetchCurator(message.curator_id).then(c => setCuratorName(c.full_name)).catch(() => {})
    }
  }, [message.curator_id])

  const handleAssign = async (curatorId: string) => {
    try {
      await assignCurator(message.id, { curator_id: curatorId })
      const c = curators.find(c => c.id === curatorId)
      setCuratorName(c?.full_name || null)
      setShowAssign(false)
    } catch {}
  }

  const handleTransfer = async (toCuratorId: string) => {
    try {
      await transferCurator(message.id, {
        from_curator_id: message.curator_id!,
        to_curator_id: toCuratorId,
      })
      const c = curators.find(c => c.id === toCuratorId)
      setCuratorName(c?.full_name || null)
      setShowTransfer(false)
    } catch {}
  }

  const openHistory = async () => {
    try {
      const entries = await fetchAssignmentHistory(message.id)
      setHistoryEntries(entries)
      setShowHistory(true)
    } catch {}
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const getFileIcon = () => {
    const ext = (message.metadata?.file_name as string || '').split('.').pop()?.toLowerCase()
    if (ext === 'pdf') return '📄'
    if (['doc', 'docx'].includes(ext || '')) return '📝'
    if (['xls', 'xlsx', 'csv'].includes(ext || '')) return '📊'
    if (ext === 'txt') return '📃'
    return '📎'
  }

  const renderContent = () => {
    if (message.message_type === 'sticker' && message.metadata?.file_url) {
      return <StickerRenderer metadata={message.metadata} />
    }

    if (isPhoto) {
      return (
        <div className="-mx-3.5 -mt-2 mb-1">
          <img
            src={getFileUrl()}
            alt="photo"
            className="w-full max-w-[400px] rounded-t-2xl object-cover cursor-pointer"
            loading="lazy"
            onClick={(e) => { e.stopPropagation(); setLightbox({ url: getFileUrl(), isVideo: false }) }}
          />
          {message.content && message.content !== '[photo]' && (
            <p className="px-3.5 pt-2">{message.content}</p>
          )}
        </div>
      )
    }

    if (isAnimation) {
      const isGif = mimeType === 'image/gif' || getFileUrl().endsWith('.gif')
      return (
        <div className="-mx-3.5 -mt-2 mb-1">
          {isGif ? (
            <img
              src={getFileUrl()}
              alt="animation"
              className="w-full max-w-[400px] rounded-t-2xl object-cover cursor-pointer"
              loading="lazy"
              onClick={(e) => { e.stopPropagation(); setLightbox({ url: getFileUrl(), isVideo: false }) }}
            />
          ) : (
            <video
              src={getFileUrl()}
              autoPlay
              loop
              muted
              playsInline
              className="w-full max-w-[400px] rounded-t-2xl object-cover cursor-pointer"
              onClick={(e) => { e.stopPropagation(); setLightbox({ url: getFileUrl(), isVideo: true }) }}
            />
          )}
          {message.content && message.content !== '[animation]' && (
            <p className="px-3.5 pt-2">{message.content}</p>
          )}
        </div>
      )
    }

    if (isDocument) {
      const fileName = (message.metadata?.file_name as string) || 'document'
      const fileSize = formatFileSize((message.metadata?.file_size as number) || 0)
      const fileUrl = getFileUrl()
      return (
        <div className="-mx-3.5 -mt-2 mb-1">
          <a
            href={fileUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 rounded-t-2xl bg-gray-50 px-3.5 py-3 transition hover:bg-gray-100 dark:bg-gray-600 dark:hover:bg-gray-500"
          >
            <span className="text-2xl">{getFileIcon()}</span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{fileName}</p>
              <p className="text-xs opacity-60">{fileSize}</p>
            </div>
            <svg className="h-5 w-5 shrink-0 opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </a>
          {message.content && message.content !== '[document]' && (
            <p className="px-3.5 pt-2">{message.content}</p>
          )}
        </div>
      )
    }

    return <p>{message.content || <span className="italic opacity-70 dark:opacity-50">Нет текста</span>}</p>
  }

  const renderLightbox = () => {
    if (!lightbox) return null
    return (
      <div
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
        onClick={() => setLightbox(null)}
      >
        <button
          className="absolute right-4 top-4 flex h-10 w-10 items-center justify-center rounded-full bg-white/20 text-2xl text-white transition hover:bg-white/40"
          onClick={() => setLightbox(null)}
        >
          ✕
        </button>
        {lightbox.isVideo ? (
          <video
            src={lightbox.url}
            autoPlay
            loop
            muted
            controls
            className="max-h-[90vh] max-w-[90vw] rounded-xl object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        ) : (
          <img
            src={lightbox.url}
            alt="full"
            className="max-h-[90vh] max-w-[90vw] rounded-xl object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        )}
      </div>
    )
  }

  return (
    <div
      className={`group relative max-w-[75%] ${isFirst ? 'mt-4' : 'mt-0.5'} ${selected ? 'opacity-100' : ''}`}
      onClick={() => onSelect(message)}
    >
      {isFirst && (
        <div className={`mb-1 flex items-center gap-2 ${isOwn ? 'justify-end' : ''}`}>
          {!isOwn && <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">{senderLabel}</span>}
          {!isOwn && <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-500 dark:bg-gray-700 dark:text-gray-400">{channelLabel}</span>}
          {isOwn && <span className="text-[10px] text-gray-400 dark:text-gray-500">Вы</span>}
        </div>
      )}
      <div
        className={`
          relative rounded-2xl px-3.5 py-2 text-sm leading-relaxed transition cursor-pointer
          ${(message.message_type === 'photo' || message.message_type === 'animation') && message.metadata?.file_url ? 'overflow-hidden' : ''}
          ${isFirst ? (isOwn ? 'rounded-tr-md' : 'rounded-tl-md') : ''}
          ${isLast ? (isOwn ? 'rounded-br-md' : 'rounded-bl-md') : ''}
          ${isOwn ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100'}
          ${selected ? (isOwn ? 'ring-2 ring-blue-300' : 'bg-blue-100 ring-2 ring-blue-300 dark:bg-blue-900/30') : ''}
          ${isOwn ? 'hover:bg-blue-600' : 'hover:bg-gray-200 dark:hover:bg-gray-600'}
        `}
      >
        {renderContent()}
        <div className={`mt-0.5 flex items-center justify-end gap-1 ${isLast ? '' : 'opacity-0 group-hover:opacity-100'}`}>
          {curatorName && (
            <span className={`mr-auto text-[10px] ${isOwn ? 'text-blue-200' : 'text-gray-400 dark:text-gray-500'}`}>
              👤 {curatorName}
            </span>
          )}
          {!isOwn && !curatorName && (
            <button
              className="mr-auto text-[10px] text-blue-400 hover:text-blue-600 dark:text-blue-300"
              onClick={(e) => { e.stopPropagation(); fetchCurators('active').then(setCurators).then(() => setShowAssign(!showAssign)).catch(() => {}) }}
            >
              + Назначить
            </button>
          )}
          {showAssign && (
            <div
              className="absolute bottom-full left-0 z-10 mb-1 max-h-32 overflow-y-auto rounded-lg border bg-white p-1 shadow-lg dark:border-gray-600 dark:bg-gray-800"
              onClick={(e) => e.stopPropagation()}
            >
              {curators.filter(c => c.id !== me?.id).map(c => (
                <button
                  key={c.id}
                  className="block w-full rounded px-2 py-1 text-left text-xs hover:bg-gray-100 dark:hover:bg-gray-700"
                  onClick={() => handleAssign(c.id)}
                >
                  {c.full_name}
                </button>
              ))}
            </div>
          )}
          {!isOwn && curatorName && (
            <div className="mr-auto flex gap-1">
              <button
                className="text-[10px] text-blue-400 hover:text-blue-600 dark:text-blue-300"
                onClick={(e) => { e.stopPropagation(); fetchCurators('active').then(setCurators).then(() => setShowTransfer(!showTransfer)).catch(() => {}) }}
              >
                ↻ Переназначить
              </button>
              <button
                className="text-[10px] text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
                onClick={(e) => { e.stopPropagation(); openHistory() }}
              >
                ⓘ
              </button>
            </div>
          )}
          {showTransfer && (
            <div
              className="absolute bottom-full left-0 z-10 mb-1 max-h-32 overflow-y-auto rounded-lg border bg-white p-1 shadow-lg dark:border-gray-600 dark:bg-gray-800"
              onClick={(e) => e.stopPropagation()}
            >
              {curators.filter(c => c.id !== message.curator_id).map(c => (
                <button
                  key={c.id}
                  className="block w-full rounded px-2 py-1 text-left text-xs hover:bg-gray-100 dark:hover:bg-gray-700"
                  onClick={() => handleTransfer(c.id)}
                >
                  {c.full_name}
                </button>
              ))}
            </div>
          )}
          {showHistory && (
            <div
              className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
              onClick={() => setShowHistory(false)}
            >
              <div
                className="max-h-80 w-72 overflow-y-auto rounded-xl bg-white p-4 shadow-lg dark:bg-gray-800"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-gray-800 dark:text-gray-100">История назначений</h3>
                  <button
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    onClick={() => setShowHistory(false)}
                  >
                    ✕
                  </button>
                </div>
                {historyEntries.length === 0 && (
                  <p className="text-xs text-gray-400">Нет записей</p>
                )}
                {historyEntries.map(entry => (
                  <div key={entry.id} className="mb-2 border-b border-gray-100 pb-2 last:border-0 dark:border-gray-700">
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {entry.from_curator_id
                        ? `с ${entry.from_curator_id.slice(0, 8)}…`
                        : '—'} → {entry.to_curator_id
                          ? `${entry.to_curator_id.slice(0, 8)}…`
                          : '—'}
                    </p>
                    {entry.reason && (
                      <p className="text-[10px] text-gray-400">{entry.reason}</p>
                    )}
                    {entry.created_at && (
                      <p className="text-[10px] text-gray-400">
                        {new Date(entry.created_at).toLocaleString('ru-RU')}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          <span className={`text-[10px] ${isOwn ? 'text-blue-200' : 'text-gray-400 dark:text-gray-500'}`}>{time}</span>
          {isLast && <span className={`text-[10px] ${isOwn ? 'text-blue-200' : 'text-gray-400 dark:text-gray-500'}`}>{date}</span>}
        </div>
      </div>
      {renderLightbox()}
    </div>
  )
}
