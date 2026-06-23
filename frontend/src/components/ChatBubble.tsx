import { useState } from 'react'
import type { Message } from '../types'
import { StickerRenderer } from './StickerRenderer'
import { normalizeFileUrl } from '../utils'

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
  const [lightbox, setLightbox] = useState<{ url: string; isVideo: boolean } | null>(null)
  const time = new Date(message.timestamp).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  const date = new Date(message.timestamp).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })

  const isAnimation = message.message_type === 'animation' && message.metadata?.file_url
  const isPhoto = message.message_type === 'photo' && message.metadata?.file_url

  const getFileUrl = () => normalizeFileUrl(message.metadata!.file_url as string)
  const mimeType = message.metadata?.mime_type as string | undefined

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
          <span className={`text-[10px] ${isOwn ? 'text-blue-200' : 'text-gray-400 dark:text-gray-500'}`}>{time}</span>
          {isLast && <span className={`text-[10px] ${isOwn ? 'text-blue-200' : 'text-gray-400 dark:text-gray-500'}`}>{date}</span>}
        </div>
      </div>
      {renderLightbox()}
    </div>
  )
}
