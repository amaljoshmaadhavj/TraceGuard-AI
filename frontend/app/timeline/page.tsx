'use client'

import { AppLayout } from '@/components/layout/app-layout'
import { PageHeader } from '@/components/common/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Clock, History, ShieldAlert, Zap, Activity } from 'lucide-react'
import { useEffect, useState } from 'react'

interface TimelineEvent {
  timestamp: string;
  category: string;
  description: string;
  severity: string;
}

const getEventIcon = (category: string) => {
  const cat = category.toLowerCase();
  if (cat.includes('credential')) return ShieldAlert;
  if (cat.includes('lateral')) return Zap;
  return History;
}

const getSeverityStyles = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return { text: 'text-rose-600 dark:text-rose-400', bg: 'bg-rose-50 dark:bg-rose-950/30', border: 'border-rose-200 dark:border-rose-900/30' }
    case 'high':
      return { text: 'text-orange-600 dark:text-orange-400', bg: 'bg-orange-50 dark:bg-orange-950/30', border: 'border-orange-200 dark:border-orange-900/30' }
    case 'medium':
      return { text: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-950/30', border: 'border-amber-200 dark:border-amber-900/30' }
    case 'low':
      return { text: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-950/30', border: 'border-emerald-200 dark:border-emerald-900/30' }
    default:
      return { text: 'text-slate-600 dark:text-slate-400', bg: 'bg-slate-50 dark:bg-slate-950/30', border: 'border-slate-200 dark:border-slate-900/30' }
  }
}

export default function TimelinePage() {
  const [events, setEvents] = useState<TimelineEvent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchTimeline() {
      try {
        const response = await fetch('http://localhost:8001/api/stats/timeline')
        const data = await response.json()
        if (data && data.timeline) {
          setEvents(data.timeline)
        }
      } catch (error) {
        console.error('Failed to fetch timeline:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchTimeline()
  }, [])

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8 space-y-8">
        <PageHeader
          title="Evidence Timeline"
          description="Chronological reconstruction of forensic events across all ingested artifacts"
          icon={<Clock className="w-8 h-8 text-primary" />}
        />

        <div className="relative space-y-0 max-w-4xl">
          {/* Vertical line */}
          <div className="absolute left-[27px] top-4 bottom-4 w-[2px] bg-border/60" />

          {loading ? (
            <div className="pl-16 py-12 flex items-center gap-3">
              <Activity className="w-5 h-5 animate-spin text-muted-foreground" />
              <span className="text-sm font-bold uppercase tracking-widest text-muted-foreground/40">Synchronizing timeline data...</span>
            </div>
          ) : events.length === 0 ? (
            <div className="pl-16 py-12 text-center max-w-xs opacity-50">
              <History className="w-10 h-10 text-muted-foreground mx-auto mb-4" />
              <p className="text-sm font-medium">No forensic events identified in current stream.</p>
            </div>
          ) : (
            events.map((event, index) => {
              const Icon = getEventIcon(event.category);
              const styles = getSeverityStyles(event.severity);
              return (
                <div key={index} className="relative pl-16 pb-12 group last:pb-0">
                  {/* Connector point */}
                  <div className={`absolute left-0 top-0 w-14 h-14 rounded-2xl flex items-center justify-center border shadow-sm transition-transform group-hover:scale-105 z-10 ${styles.bg} ${styles.border}`}>
                    <Icon className={`w-6 h-6 ${styles.text}`} />
                  </div>

                  <Card className="card-professional overflow-hidden">
                    <CardHeader className="py-4 px-6 bg-secondary/20 border-b border-border/50 flex flex-row items-center justify-between space-y-0">
                      <div>
                        <CardTitle className="text-sm font-bold tracking-tight">
                          {event.category.replace(/_/g, ' ').toUpperCase()}
                        </CardTitle>
                        <CardDescription className="text-[10px] font-bold uppercase tracking-widest mt-1">
                          {event.timestamp}
                        </CardDescription>
                      </div>
                      <div className={`text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-tighter border ${styles.border} ${styles.text}`}>
                        {event.severity}
                      </div>
                    </CardHeader>
                    <CardContent className="py-5 px-6">
                      <p className="text-sm font-medium leading-relaxed text-foreground/80">
                        {event.description}
                      </p>
                    </CardContent>
                  </Card>
                </div>
              );
            })
          )}
        </div>
      </div>
    </AppLayout>
  )
}
