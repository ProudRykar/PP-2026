import { useState, useEffect } from 'react'
import type { Client, ClientUpdatePayload } from '../types'
import { fetchClientByChannel, updateClient } from '../api'

interface ClientCardProps {
  channel: string
  senderId: string
  onClose: () => void
}

export function ClientCard({ channel, senderId, onClose }: ClientCardProps) {
  const [client, setClient] = useState<Client | null>(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState<ClientUpdatePayload>({})

  useEffect(() => {
    setLoading(true)
    fetchClientByChannel(channel, senderId)
      .then((c) => {
        setClient(c)
        if (c) {
          setForm({ name: c.name, phone: c.phone ?? '', email: c.email ?? '', avatar_url: c.avatar_url ?? '' })
        }
      })
      .catch(() => setClient(null))
      .finally(() => setLoading(false))
  }, [channel, senderId])

  const handleSave = async () => {
    if (!client) return
    const updated = await updateClient(client.id, form)
    setClient(updated)
    setEditing(false)
  }

  if (loading) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <p className="text-sm text-gray-400 dark:text-gray-500">Загрузка профиля...</p>
      </div>
    )
  }

  if (!client) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <p className="text-sm text-gray-400 dark:text-gray-500">Профиль не найден</p>
      </div>
    )
  }

  const channelMeta: Record<string, { label: string; icon: string }> = {
    telegram: { label: 'Telegram', icon: '✈️' },
    email: { label: 'Email', icon: '📧' },
    whatsapp: { label: 'WhatsApp', icon: '💬' },
    vk: { label: 'VK', icon: '🌐' },
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Карточка клиента</h3>
        <div className="flex gap-2">
          <button
            className="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
            onClick={() => setEditing(!editing)}
          >
            {editing ? 'Отмена' : 'Редактировать'}
          </button>
          <button className="text-xs text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-400" onClick={onClose}>
            ✕
          </button>
        </div>
      </div>

      <div className="p-4">
        <div className="mb-3 flex items-center gap-3">
          {client.avatar_url ? (
            <img src={client.avatar_url} alt="" className="h-10 w-10 rounded-full object-cover" />
          ) : (
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-600 dark:bg-blue-900 dark:text-blue-300">
              {client.name.charAt(0).toUpperCase()}
            </div>
          )}
          <div className="min-w-0 flex-1">
            {editing ? (
              <input
                className="w-full rounded border border-gray-300 px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
                value={form.name ?? ''}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="ФИО"
              />
            ) : (
              <p className="text-sm font-semibold text-gray-800 dark:text-gray-100">{client.name}</p>
            )}
            <p className="text-xs text-gray-400 dark:text-gray-500">
              {client.last_interaction
                ? `Последняя активность: ${new Date(client.last_interaction).toLocaleString('ru-RU')}`
                : 'Нет активности'}
            </p>
          </div>
        </div>

        <div className="mb-3 space-y-1.5">
          <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
            <span className="w-16 shrink-0 text-gray-400 dark:text-gray-500">Телефон</span>
            {editing ? (
              <input
                className="flex-1 rounded border border-gray-300 px-2 py-1 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
                value={form.phone ?? ''}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                placeholder="+7..."
              />
            ) : (
              <span>{client.phone || '—'}</span>
            )}
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
            <span className="w-16 shrink-0 text-gray-400 dark:text-gray-500">Email</span>
            {editing ? (
              <input
                className="flex-1 rounded border border-gray-300 px-2 py-1 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
                value={form.email ?? ''}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="email@example.com"
              />
            ) : (
              <span className="truncate">{client.email || '—'}</span>
            )}
          </div>
        </div>

        <div className="mb-2">
          <p className="mb-1 text-xs font-medium text-gray-500 dark:text-gray-400">Каналы связи</p>
          <div className="flex flex-wrap gap-1.5">
            {client.channels.map((ch) => {
              const m = channelMeta[ch.channel]
              return (
                <span
                  key={`${ch.channel}:${ch.external_id}`}
                  className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-600 dark:bg-gray-700 dark:text-gray-400"
                >
                  <span>{m?.icon || '🔗'}</span>
                  <span>{m?.label ?? ch.channel}</span>
                </span>
              )
            })}
          </div>
        </div>

        <div className="flex items-center justify-between border-t border-gray-100 pt-2 text-[10px] text-gray-400 dark:border-gray-700 dark:text-gray-500">
          <span>Создан: {client.created_at ? new Date(client.created_at).toLocaleDateString('ru-RU') : '—'}</span>
        </div>

        {editing && (
          <button
            className="mt-3 w-full rounded bg-blue-600 py-1.5 text-sm text-white hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600"
            onClick={handleSave}
          >
            Сохранить
          </button>
        )}
      </div>
    </div>
  )
}
