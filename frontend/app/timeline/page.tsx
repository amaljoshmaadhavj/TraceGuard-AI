'use client'

import { AppLayout } from '@/components/layout/app-layout'
import { PageHeader } from '@/components/common/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Clock, History, ShieldAlert, Zap } from 'lucide-react'
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

const getEventColor = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'text-red-500'
    case 'high':
      return 'text-orange-500'
    case 'medium':
      return 'text-yellow-500'
    case 'low':
      return 'text-green-500'
    default:
      return 'text-primary/60'
  }
}

const getEventBgColor = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'bg-red-500/10'
    case 'high':
      return 'bg-orange-500/10'
    case 'medium':
      return 'bg-yellow-500/10'
    case 'low':
      return 'bg-green-500/10'
    default:
      return 'bg-primary/5'
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
      <div className="px-4 lg:px-8 py-8 space-y-8">
        <PageHeader
          title="Activity Timeline"
          description="Chronological view of forensic events detected in ingested evidence"
          icon={<Clock className="w-8 h-8" />}
        />

        <div className="relative space-y-0">
          {/* Vertical line */}
          <div className="absolute left-[27px] top-2 bottom-2 w-px bg-primary/10" />

          {loading ? (
            <div className="pl-16 py-8 text-primary/40 font-mono animate-pulse">
              SYNCING_TEMPORAL_DATA...
            </div>
          ) : events.length === 0 ? (
            <div className="pl-16 py-8 text-primary/40 font-mono italic">
              No forensic events detected in the database.
            </div>
          ) : (
            events.map((event, index) => {
              const Icon = getEventIcon(event.category);
              return (
                <div key={index} className="relative pl-16 pb-8">
                  {/* Connector point */}
                  <div className={`absolute left-0 top-0 w-14 h-14 rounded-full flex items-center justify-center border border-primary/20 ${getEventBgColor(event.severity)}`}>
                    <Icon className={`w-6 h-6 ${getEventColor(event.severity)}`} />
                  </div>

                  <Card className="card-premium border-primary/20 bg-background/50 backdrop-blur-sm">
                    <CardHeader className="py-3 bg-primary/5 border-b border-primary/10 flex flex-row items-center justify-between space-y-0">
                      <div>
                        <CardTitle className="text-xs font-black uppercase tracking-widest text-primary">
                          {event.category.replace('_', ' ')}
                        </CardTitle>
                        <CardDescription className="text-[10px] font-mono opacity-60">
                          {event.timestamp}
                        </CardDescription>
                      </div>
                      <div className={`text-[10px] font-mono px-2 py-0.5 rounded border border-current ${getEventColor(event.severity)}`}>
                        {event.severity.toUpperCase()}
                      </div>
                    </CardHeader>
                    <CardContent className="py-4">
                      <p className="text-sm font-mono leading-relaxed text-foreground/80 lowercase">
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
