import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

type Status = 'pending' | 'analyzing' | 'suspected' | 'confirmed' | 'resolved' | 'unknown'
type Severity = 'critical' | 'high' | 'medium' | 'low'

interface StatusBadgeProps {
  status: Status
  className?: string
}

interface SeverityBadgeProps {
  severity: Severity
  className?: string
}

const statusConfig: Record<Status, { bg: string; text: string; dot: string }> = {
  pending: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-800 dark:text-yellow-200', dot: 'bg-yellow-500' },
  analyzing: { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-800 dark:text-blue-200', dot: 'bg-blue-500' },
  suspected: { bg: 'bg-orange-100 dark:bg-orange-900/30', text: 'text-orange-800 dark:text-orange-200', dot: 'bg-orange-500' },
  confirmed: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-800 dark:text-red-200', dot: 'bg-red-500' },
  resolved: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-800 dark:text-green-200', dot: 'bg-green-500' },
  unknown: { bg: 'bg-gray-100 dark:bg-gray-900/30', text: 'text-gray-800 dark:text-gray-200', dot: 'bg-gray-500' },
}

const severityConfig: Record<Severity, { bg: string; text: string; dot: string }> = {
  critical: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-800 dark:text-red-200', dot: 'bg-red-500' },
  high: { bg: 'bg-orange-100 dark:bg-orange-900/30', text: 'text-orange-800 dark:text-orange-200', dot: 'bg-orange-500' },
  medium: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-800 dark:text-yellow-200', dot: 'bg-yellow-500' },
  low: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-800 dark:text-green-200', dot: 'bg-green-500' },
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status]
  return (
    <div className={cn('inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium', config.bg, config.text, className)}>
      <div className={cn('w-2 h-2 rounded-full', config.dot)} />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </div>
  )
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const config = severityConfig[severity]
  return (
    <div className={cn('inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium', config.bg, config.text, className)}>
      <div className={cn('w-2 h-2 rounded-full', config.dot)} />
      {severity.charAt(0).toUpperCase() + severity.slice(1)}
    </div>
  )
}
