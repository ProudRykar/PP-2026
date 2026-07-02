export function Footer({ curatorName, curatorRole }: { curatorName?: string; curatorRole?: string }) {
  return (
    <div className="border-t border-gray-200 bg-gray-800 px-3 py-1.5 dark:border-gray-700">
      <p className="text-[10px] font-medium text-gray-300">Омниканал</p>
      {curatorName && (
        <p className="text-[10px] text-gray-400">{curatorName}{curatorRole ? ` (${curatorRole})` : ''}</p>
      )}
    </div>
  )
}
