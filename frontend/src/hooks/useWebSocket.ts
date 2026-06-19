import { useEffect, useRef } from 'react'

const RECONNECT_DELAY = 3000

export function useWebSocket(onMessage: (data: unknown) => void) {
  const onMessageRef = useRef(onMessage)
  const wsRef = useRef<WebSocket | null>(null)
  const intentionalCloseRef = useRef(false)
  onMessageRef.current = onMessage

  useEffect(() => {
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null

    function connect() {
      if (wsRef.current) return

      const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
      const url = `${protocol}//${location.host}/ws`
      const ws = new WebSocket(url)

      ws.onopen = () => {
        wsRef.current = ws
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessageRef.current(data)
        } catch {
          // ignore non-json messages
        }
      }

      ws.onclose = () => {
        wsRef.current = null
        if (!intentionalCloseRef.current) {
          reconnectTimer = setTimeout(connect, RECONNECT_DELAY)
        }
      }

      ws.onerror = () => {
        ws.close()
      }
    }

    connect()

    return () => {
      intentionalCloseRef.current = true
      if (reconnectTimer) clearTimeout(reconnectTimer)
      wsRef.current?.close()
      wsRef.current = null
    }
  }, [])
}
