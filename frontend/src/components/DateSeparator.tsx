export function DateSeparator({ date }: { date: string }) {
  return (
    <div className="py-1 flex justify-center">
      <span className="px-3 py-1 rounded-full bg-gray-200/70 dark:bg-gray-700/70 text-xs text-gray-500 dark:text-gray-400 select-none">
        {date}
      </span>
    </div>
  )
}
