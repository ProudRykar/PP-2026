interface FilterBarProps {
  channels: string[]
  current: string
  onChange: (channel: string) => void
}

const ALL = 'all'

const labels: Record<string, string> = {
  all: 'Все',
  telegram: 'Telegram',
  email: 'Email',
}

export function FilterBar({ channels, current, onChange }: FilterBarProps) {
  const items = [ALL, ...channels]
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((ch) => (
        <button
          key={ch}
          className={`rounded px-3 py-1.5 text-sm font-medium transition ${
            ch === current
              ? 'bg-blue-500 text-white shadow-sm'
              : 'bg-white text-gray-600 ring-1 ring-gray-200 hover:bg-gray-50'
          }`}
          onClick={() => onChange(ch)}
        >
          {labels[ch] ?? ch}
        </button>
      ))}
    </div>
  )
}
