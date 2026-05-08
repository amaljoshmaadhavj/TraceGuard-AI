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
  pending: { bg: 'bg-amber-50 dark:bg-amber-950/20', text: 'text-amber-700 dark:text-amber-400', dot: 'bg-amber-500' },
  analyzing: { bg: 'bg-blue-50 dark:bg-blue-950/20', text: 'text-blue-700 dark:text-blue-400', dot: 'bg-blue-500' },
  suspected: { bg: 'bg-orange-50 dark:bg-orange-950/20', text: 'text-orange-700 dark:text-orange-400', dot: 'bg-orange-500' },
  confirmed: { bg: 'bg-rose-50 dark:bg-rose-950/20', text: 'text-rose-700 dark:text-rose-400', dot: 'bg-rose-500' },
  resolved: { bg: 'bg-emerald-50 dark:bg-emerald-950/20', text: 'text-emerald-700 dark:text-emerald-400', dot: 'bg-emerald-500' },
  unknown: { bg: 'bg-slate-50 dark:bg-slate-950/20', text: 'text-slate-700 dark:text-slate-400', dot: 'bg-slate-500' },
}

const severityConfig: Record<Severity, { bg: string; text: string; dot: string }> = {
  critical: { bg: 'bg-rose-50 dark:bg-rose-950/20', text: 'text-rose-700 dark:text-rose-400', dot: 'bg-rose-500' },
  high: { bg: 'bg-orange-50 dark:bg-orange-950/20', text: 'text-orange-700 dark:text-orange-400', dot: 'bg-orange-500' },
  medium: { bg: 'bg-amber-50 dark:bg-amber-950/20', text: 'text-amber-700 dark:text-amber-400', dot: 'bg-amber-500' },
  low: { bg: 'bg-emerald-50 dark:bg-emerald-950/20', text: 'text-emerald-700 dark:text-emerald-400', dot: 'bg-emerald-500' },
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status]
  return (
    <div className={cn('inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider', config.bg, config.text, className)}>
      <div className={cn('w-1.5 h-1.5 rounded-full', config.dot)} />
      {status}
    </div>
  )
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const config = severityConfig[severity]
  return (
    <div className={cn('inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider', config.bg, config.text, className)}>
      <div className={cn('w-1.5 h-1.5 rounded-full', config.dot)} />
      {severity}
    </div>
  )
}
