'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertCircle, Clock, Shield } from 'lucide-react'

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

const severityColors: Record<string, string> = {
  critical: 'border-red-500 text-red-500',
  high: 'border-orange-500 text-orange-500',
  medium: 'border-yellow-500 text-yellow-500',
  low: 'border-blue-500 text-blue-500',
  info: 'border-green-500 text-green-500'
}

const categoryColors: Record<string, string> = {
  credential_access: 'bg-red-500/20 text-red-400',
  execution: 'bg-orange-500/20 text-orange-400',
  lateral_movement: 'bg-yellow-500/20 text-yellow-400',
  persistence: 'bg-purple-500/20 text-purple-400',
  discovery: 'bg-cyan-500/20 text-cyan-400',
  collection: 'bg-pink-500/20 text-pink-400',
  defense_evasion: 'bg-indigo-500/20 text-indigo-400',
  exfiltration: 'bg-red-600/20 text-red-400',
  unknown: 'bg-gray-500/20 text-gray-400'
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
    <div className="space-y-6">
      {/* Timeline Summary Card */}
      <Card className="card-premium border-primary/20 bg-primary/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-primary">
            <Clock className="w-5 h-5" />
            Timeline Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-muted-foreground uppercase font-mono">Date Range</p>
              <p className="text-sm font-mono mt-1">
                {dateRange.start ? formatDate(dateRange.start) : 'N/A'}
              </p>
              {dateRange.end && dateRange.start !== dateRange.end && (
                <p className="text-xs text-muted-foreground font-mono">
                  to {formatDate(dateRange.end)}
                </p>
              )}
            </div>
            <div>
              <p className="text-xs text-muted-foreground uppercase font-mono">Total Events</p>
              <p className="text-2xl font-bold text-primary mt-1">{events.length}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground uppercase font-mono">Confidence</p>
              <div className="flex items-center gap-2 mt-1">
                <div className="w-12 h-2 bg-primary/20 rounded overflow-hidden">
                  <div 
                    className="h-full bg-primary transition-all"
                    style={{ width: `${confidence * 100}%` }}
                  />
                </div>
                <span className="text-sm font-mono">{(confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>

          <div className="border-t border-primary/20 pt-4">
            <p className="text-xs text-muted-foreground uppercase font-mono mb-2">Query</p>
            <p className="text-sm font-mono text-primary/80 italic">"{query}"</p>
          </div>

          <div className="border-t border-primary/20 pt-4">
            <p className="text-xs text-muted-foreground uppercase font-mono mb-2">Summary</p>
            <p className="text-sm leading-relaxed text-foreground">{summary}</p>
          </div>
        </CardContent>
      </Card>

      {/* Events Timeline */}
      <Card className="card-premium border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Event Sequence
          </CardTitle>
        </CardHeader>
        <CardContent>
          {events.length === 0 ? (
            <div className="flex items-center gap-2 text-muted-foreground">
              <AlertCircle className="w-4 h-4" />
              <p>No events to display</p>
            </div>
          ) : (
            <div className="space-y-4">
              {events.map((event, idx) => (
                <div
                  key={idx}
                  className={`flex gap-4 border-l-4 pl-4 py-3 transition-colors ${
                    severityColors[event.severity as keyof typeof severityColors] ||
                    'border-gray-500 text-gray-500'
                  }`}
                >
                  {/* Time marker */}
                  <div className="flex flex-col items-center flex-shrink-0">
                    <div className={`w-3 h-3 rounded-full ${severityColors[event.severity as keyof typeof severityColors]?.split(' ')[1]} -ml-3.5`} />
                    <span className="text-xs text-muted-foreground mt-2 font-mono whitespace-nowrap">
                      {formatTimestamp(event.timestamp)}
                    </span>
                  </div>

                  {/* Event details */}
                  <div className="flex-1 min-w-0">
                    {/* Header row */}
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <span className="text-sm font-bold font-mono">
                        [{event.event_id}]
                      </span>
                      <span
                        className={`text-xs px-2 py-1 rounded font-mono ${
                          categoryColors[
                            event.category.toLowerCase() as keyof typeof categoryColors
                          ] || categoryColors.unknown
                        }`}
                      >
                        {event.category.replace(/_/g, ' ').toUpperCase()}
                      </span>
                      <span className="text-xs text-muted-foreground">{event.source_system}</span>
                    </div>

                    {/* Description */}
                    <p className="text-sm font-mono mb-2 text-foreground break-words">
                      {event.description}
                    </p>

                    {/* Metadata */}
                    <div className="space-y-1 text-xs text-muted-foreground font-mono">
                      {event.user && event.user !== 'N/A' && event.user !== 'Unknown' && (
                        <p>User: {event.user}</p>
                      )}
                      {event.process_name && event.process_name !== 'N/A' && event.process_name !== 'Unknown' && (
                        <p>
                          Process: {event.process_name}
                          {event.process_id !== undefined && event.process_id !== null && event.process_id !== 0 && ` (PID: ${event.process_id})`}
                        </p>
                      )}
                      {event.parent_process && event.parent_process !== 'N/A' && event.parent_process !== 'Unknown' && (
                        <p>Parent: {event.parent_process}</p>
                      )}
                      {(event.source_ip || event.dest_ip) && (
                        <p>
                          Network:
                          {event.source_ip && event.source_ip !== 'N/A' && ` ${event.source_ip}`}
                          {event.source_ip && event.dest_ip && ' →'}
                          {event.dest_ip && event.dest_ip !== 'N/A' && ` ${event.dest_ip}`}
                        </p>
                      )}
                    </div>

                    {/* MITRE Techniques */}
                    {event.mitre_techniques.length > 0 && (
                      <div className="flex gap-1 mt-3 flex-wrap">
                        {event.mitre_techniques.map((tech, i) => (
                          <span
                            key={i}
                            className="text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded font-mono"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
