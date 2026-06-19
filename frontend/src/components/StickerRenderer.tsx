import { useState, useEffect } from 'react'
import pako from 'pako'
import '@dotlottie/player-component'
import { normalizeFileUrl } from '../utils'

interface StickerRendererProps {
  metadata: Record<string, unknown>
}

export function StickerRenderer({ metadata }: StickerRendererProps) {
  const url = metadata.file_url as string | undefined
  if (!url) return null

  const displayUrl = normalizeFileUrl(url)

  if (url.split('?')[0].endsWith('.webm')) {
    return (
      <video
        src={displayUrl}
        controls
        autoPlay
        loop
        muted
        className="max-w-[200px] rounded-lg"
      />
    )
  }

  if (url.split('?')[0].endsWith('.tgs')) {
    return <TgsRenderer src={displayUrl} />
  }

  return (
    <img
      src={displayUrl}
      alt="sticker"
      className="max-w-[200px] rounded-lg"
    />
  )
}

function TgsRenderer({ src }: { src: string }) {
  const [lottieSrc, setLottieSrc] = useState<string | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const res = await fetch(src)
        const buffer = await res.arrayBuffer()
        const jsonStr = pako.ungzip(new Uint8Array(buffer), { to: 'string' })
        if (cancelled) return
        const blob = new Blob([jsonStr], { type: 'application/json' })
        setLottieSrc(URL.createObjectURL(blob))
      } catch {
        if (!cancelled) setError(true)
      }
    }

    load()

    return () => {
      cancelled = true
    }
  }, [src])

  if (error) {
    return <div className="text-xs text-gray-400">Ошибка загрузки стикера</div>
  }

  if (!lottieSrc) {
    return <div className="text-xs text-gray-400">Загрузка...</div>
  }

  return (
    <div className="max-w-[200px]">
      <dotlottie-player
        src={lottieSrc}
        autoplay={true}
        loop={true}
        style={{ width: 200, height: 200 }}
      />
    </div>
  )
}
