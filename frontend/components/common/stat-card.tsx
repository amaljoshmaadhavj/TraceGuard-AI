import { ReactNode } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowUp, ArrowDown } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StatCardProps {
  title: string
  value: string | number
  icon?: ReactNode
  change?: {
    value: number
    label: string
    trend: 'up' | 'down'
  }
  className?: string
}

export function StatCard({
  title,
  value,
  icon,
  change,
  className,
}: StatCardProps) {
  return (
    <Card className={cn('card-professional', className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
          {title}
        </CardTitle>
        {icon && <div className="text-muted-foreground/60">{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold tracking-tight">{value}</div>
        {change && (
          <div
            className={cn(
              'flex items-center gap-1.5 text-[11px] font-semibold mt-3 px-2 py-0.5 rounded-full w-fit',
              change.trend === 'up'
                ? 'text-emerald-700 bg-emerald-50 dark:text-emerald-400 dark:bg-emerald-950/30'
                : 'text-rose-700 bg-rose-50 dark:text-rose-400 dark:bg-rose-950/30'
            )}
          >
            {change.trend === 'up' ? (
              <ArrowUp className="w-3 h-3" />
            ) : (
              <ArrowDown className="w-3 h-3" />
            )}
            <span>{change.value}% {change.label}</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
