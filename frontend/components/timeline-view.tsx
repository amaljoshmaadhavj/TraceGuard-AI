'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertCircle, Clock, Shield, Database, Activity, Target } from 'lucide-react'

interface TimelineEvent {
  timestamp: string
  event_id: number
  source_system: string
  user: string
  process_name?: string
  process_id?: number
  description: string
  severity: string
  category: string
  mitre_techniques: string[]
  parent_process?: string
  source_ip?: string
  dest_ip?: string
}

interface TimelineViewProps {
  events: TimelineEvent[]
  summary: string
  dateRange: { start: string; end: string }
  confidence: number
  query: string
}

const severityStyles: Record<string, { text: string; bg: string; border: string }> = {
  critical: { text: 'text-rose-600 dark:text-rose-400', bg: 'bg-rose-50 dark:bg-rose-950/20', border: 'border-rose-200 dark:border-rose-900/30' },
  high: { text: 'text-orange-600 dark:text-orange-400', bg: 'bg-orange-50 dark:bg-orange-950/20', border: 'border-orange-200 dark:border-orange-900/30' },
  medium: { text: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-950/20', border: 'border-amber-200 dark:border-amber-900/30' },
  low: { text: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-950/20', border: 'border-emerald-200 dark:border-emerald-900/30' },
  info: { text: 'text-blue-600 dark:text-blue-400', bg: 'bg-blue-50 dark:bg-blue-950/20', border: 'border-blue-200 dark:border-blue-900/30' }
}

const categoryStyles: Record<string, string> = {
  credential_access: 'bg-rose-100 text-rose-700 dark:bg-rose-950/40 dark:text-rose-400',
  execution: 'bg-orange-100 text-orange-700 dark:bg-orange-950/40 dark:text-orange-400',
  lateral_movement: 'bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400',
  persistence: 'bg-purple-100 text-purple-700 dark:bg-purple-950/40 dark:text-purple-400',
  discovery: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-950/40 dark:text-cyan-400',
  collection: 'bg-pink-100 text-pink-700 dark:bg-pink-950/40 dark:text-pink-400',
  defense_evasion: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950/40 dark:text-indigo-400',
  exfiltration: 'bg-rose-200 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300',
  unknown: 'bg-slate-100 text-slate-700 dark:bg-slate-900/40 dark:text-slate-400'
}

export function TimelineView({
  events,
  summary,
  dateRange,
  confidence,
  query
}: TimelineViewProps) {
  const formatTimestamp = (ts: string) => {
    try {
      const date = new Date(ts)
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
      })
    } catch {
      return ts
    }
  }

  const formatDate = (ts: string) => {
    try {
      const date = new Date(ts)
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    } catch {
      return 'Unknown'
    }
  }

  return (
    <div className="space-y-8">
      {/* Timeline Summary Card */}
      <Card className="card-professional overflow-hidden">
        <CardHeader className="bg-secondary/30 border-b border-border/50">
          <div className="flex items-center gap-3">
            <Clock className="w-4 h-4 text-primary" />
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Forensic Timeline Summary</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="p-8 space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="space-y-2">
              <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest">Date Range</p>
              <div className="flex items-center gap-2">
                <Database className="w-3.5 h-3.5 text-muted-foreground/60" />
                <p className="text-sm font-bold">
                  {dateRange.start ? formatDate(dateRange.start) : 'No Data'}
                </p>
              </div>
              {dateRange.end && dateRange.start !== dateRange.end && (
                <p className="text-[10px] text-muted-foreground font-semibold px-5">
                  to {formatDate(dateRange.end)}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest">Artifact Count</p>
              <div className="flex items-center gap-2 text-primary">
                <Activity className="w-3.5 h-3.5" />
                <p className="text-2xl font-black">{events.length}</p>
              </div>
            </div>
            <div className="space-y-2">
              <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest">Engine Confidence</p>
              <div className="flex items-center gap-3 mt-1">
                <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary transition-all duration-1000"
                    style={{ width: `${confidence * 100}%` }}
                  />
                </div>
                <span className="text-xs font-black">{(confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-border/50">
            <div className="flex items-center gap-2 mb-3">
              <Target className="w-3.5 h-3.5 text-muted-foreground/60" />
              <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest">Operational Query</p>
            </div>
            <p className="text-sm font-bold text-foreground/80 italic bg-secondary/20 p-4 rounded-xl border border-border/50">
              "{query}"
            </p>
          </div>

          <div className="pt-6 border-t border-border/50">
            <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest mb-3">Executive Summary</p>
            <p className="text-sm leading-relaxed font-medium text-foreground/90 bg-primary/5 p-5 rounded-xl border border-primary/10">
              {summary}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Events Timeline */}
      <Card className="card-professional overflow-hidden">
        <CardHeader className="bg-secondary/30 border-b border-border/50">
          <div className="flex items-center gap-3">
            <Shield className="w-4 h-4 text-primary" />
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Forensic Event Sequence</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {events.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-muted-foreground/40 gap-4">
              <AlertCircle className="w-12 h-12" />
              <p className="text-xs font-bold uppercase tracking-widest">No sequential data identified</p>
            </div>
          ) : (
            <div className="divide-y divide-border/50">
              {events.map((event, idx) => {
                const styles = severityStyles[event.severity as keyof typeof severityStyles] || severityStyles.info;
                return (
                  <div
                    key={idx}
                    className="group flex flex-col md:flex-row gap-4 md:gap-8 p-8 hover:bg-secondary/20 transition-all duration-300"
                  >
                    {/* Time marker */}
                    <div className="flex md:flex-col items-baseline md:items-end flex-shrink-0 md:w-28 gap-2">
                      <span className="text-[10px] font-black uppercase tracking-tighter text-muted-foreground">
                        {formatTimestamp(event.timestamp)}
                      </span>
                      <div className={`hidden md:block w-3 h-3 rounded-full border-2 border-background shadow-sm ${styles.text.split(' ')[0].replace('text-', 'bg-')}`} />
                    </div>

                    {/* Event details */}
                    <div className="flex-1 min-w-0 space-y-4">
                      {/* Header row */}
                      <div className="flex items-center gap-3 flex-wrap">
                        <span className="text-[10px] font-black text-muted-foreground border border-border px-2 py-0.5 rounded uppercase tracking-tighter bg-background">
                          EVT-{event.event_id}
                        </span>
                        <span
                          className={`text-[10px] px-3 py-1 rounded-full font-bold uppercase tracking-widest ${
                            categoryStyles[
                              event.category.toLowerCase() as keyof typeof categoryStyles
                            ] || categoryStyles.unknown
                          }`}
                        >
                          {event.category.replace(/_/g, ' ')}
                        </span>
                        <span className={`text-[10px] px-3 py-1 rounded-full font-black uppercase tracking-tighter border ${styles.border} ${styles.text}`}>
                          {event.severity}
                        </span>
                      </div>

                      {/* Description */}
                      <p className="text-sm font-bold text-foreground leading-relaxed">
                        {event.description}
                      </p>

                      {/* Metadata Grid */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-2 gap-x-8 pt-2">
                        {event.user && event.user !== 'N/A' && event.user !== 'Unknown' && (
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest w-16">Investigator</span>
                            <span className="text-[10px] font-black text-foreground uppercase">{event.user}</span>
                          </div>
                        )}
                        {event.process_name && event.process_name !== 'N/A' && event.process_name !== 'Unknown' && (
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest w-16">Artifact</span>
                            <span className="text-[10px] font-black text-foreground uppercase truncate">
                              {event.process_name}
                              {event.process_id !== undefined && event.process_id !== null && event.process_id !== 0 && ` (PID: ${event.process_id})`}
                            </span>
                          </div>
                        )}
                        {event.source_system && (
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest w-16">Origin</span>
                            <span className="text-[10px] font-black text-foreground uppercase">{event.source_system}</span>
                          </div>
                        )}
                        {(event.source_ip || event.dest_ip) && (
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest w-16">Network</span>
                            <span className="text-[10px] font-black text-foreground uppercase">
                              {event.source_ip || '---'} → {event.dest_ip || '---'}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* MITRE Techniques */}
                      {event.mitre_techniques.length > 0 && (
                        <div className="flex gap-2 pt-2 flex-wrap">
                          {event.mitre_techniques.map((tech, i) => (
                            <div
                              key={i}
                              className="group/tech flex items-center gap-1.5 bg-secondary/40 hover:bg-primary/10 border border-border/50 hover:border-primary/30 px-3 py-1 rounded-lg transition-all"
                            >
                              <div className="w-1 h-1 rounded-full bg-primary" />
                              <span className="text-[10px] font-bold text-muted-foreground group-hover/tech:text-primary uppercase tracking-widest">
                                {tech}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
