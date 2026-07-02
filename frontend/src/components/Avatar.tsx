const COLORS = [
  'bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-orange-500',
  'bg-pink-500', 'bg-teal-500', 'bg-indigo-500', 'bg-rose-500',
  'bg-cyan-500', 'bg-amber-500', 'bg-violet-500', 'bg-emerald-500',
]

function hashColor(name: string): string {
  let h = 0
  for (let i = 0; i < name.length; i++) {
    h = ((h << 5) - h) + name.charCodeAt(i)
    h |= 0
  }
  return COLORS[Math.abs(h) % COLORS.length]
}

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.slice(0, 2).toUpperCase()
}

interface AvatarProps {
  name: string
  size?: 'sm' | 'md'
}

const sizeClasses = {
  sm: 'h-10 w-10 text-sm',
  md: 'h-11 w-11 text-sm',
}

export function Avatar({ name, size = 'md' }: AvatarProps) {
  return (
    <div
      className={`flex shrink-0 items-center justify-center rounded-full font-bold text-white ${sizeClasses[size]} ${hashColor(name)}`}
    >
      {getInitials(name)}
    </div>
  )
}
