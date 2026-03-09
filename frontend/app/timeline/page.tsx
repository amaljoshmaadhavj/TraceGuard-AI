import { AppLayout } from '@/components/layout/app-layout'
import { PageHeader } from '@/components/common/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Clock, Upload, CheckCircle2, AlertCircle, Zap } from 'lucide-react'

const timelineEvents = [
  {
    id: 1,
    timestamp: '2024-01-15 14:32:45',
    type: 'upload',
    title: 'Evidence Uploaded',
    description: 'portrait_analysis.jpg uploaded for analysis',
    icon: Upload,
  },
  {
    id: 2,
    timestamp: '2024-01-15 14:33:12',
    type: 'analysis',
    title: 'Analysis Started',
    description: 'AI generation analysis initiated',
    icon: Zap,
  },
  {
    id: 3,
    timestamp: '2024-01-15 14:35:47',
    type: 'alert',
    title: 'Anomalies Detected',
    description: 'Suspicious patterns found in image metadata',
    icon: AlertCircle,
  },
  {
    id: 4,
    timestamp: '2024-01-15 14:37:22',
    type: 'complete',
    title: 'Analysis Complete',
    description: 'Confirmed AI-generated content with 94% confidence',
    icon: CheckCircle2,
  },
  {
    id: 5,
    timestamp: '2024-01-14 09:15:33',
    type: 'upload',
    title: 'Document Uploaded',
    description: 'document_scan.pdf submitted for verification',
    icon: Upload,
  },
  {
    id: 6,
    timestamp: '2024-01-14 09:16:01',
    type: 'analysis',
    title: 'Digital Forensics Scan',
    description: 'Scanning for manipulation and tampering',
    icon: Zap,
  },
  {
    id: 7,
    timestamp: '2024-01-14 09:20:15',
    type: 'complete',
    title: 'Manipulation Detected',
    description: 'Document has been edited and modified - 98% confidence',
    icon: CheckCircle2,
  },
]

const getEventColor = (type: string) => {
  switch (type) {
    case 'upload':
      return 'text-blue-500'
    case 'analysis':
      return 'text-purple-500'
    case 'alert':
      return 'text-red-500'
    case 'complete':
      return 'text-green-500'
    default:
      return 'text-gray-500'
  }
}

const getEventBgColor = (type: string) => {
  switch (type) {
    case 'upload':
      return 'bg-blue-100 dark:bg-blue-900/30'
    case 'analysis':
      return 'bg-purple-100 dark:bg-purple-900/30'
    case 'alert':
      return 'bg-red-100 dark:bg-red-900/30'
    case 'complete':
      return 'bg-green-100 dark:bg-green-900/30'
    default:
      return 'bg-gray-100 dark:bg-gray-900/30'
  }
}

export default function TimelinePage() {
  return (
    <AppLayout>
      <div className="px-4 lg:px-8 py-8 space-y-8">
        <PageHeader
          title="Activity Timeline"
          description="View all investigation activities and analysis events"
          icon={<Clock className="w-8 h-8" />}
        />

        <Card>
          <CardHeader>
            <CardTitle>Investigation Timeline</CardTitle>
            <CardDescription>Chronological view of all events</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-8 top-8 bottom-0 w-0.5 bg-border" />

              {/* Timeline events */}
              <div className="space-y-6">
                {timelineEvents.map((event, index) => {
                  const Icon = event.icon
                  return (
                    <div key={event.id} className="relative pl-20">
                      {/* Timeline dot */}
                      <div
                        className={`absolute -left-4 top-1 w-10 h-10 rounded-full border-4 border-background flex items-center justify-center ${getEventBgColor(
                          event.type
                        )}`}
                      >
                        <Icon className={`w-5 h-5 ${getEventColor(event.type)}`} />
                      </div>

                      {/* Event card */}
                      <div className="bg-card rounded-lg p-4 border border-border hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <h3 className="font-semibold text-sm">{event.title}</h3>
                            <p className="text-sm text-muted-foreground mt-1">
                              {event.description}
                            </p>
                          </div>
                          <time className="text-xs text-muted-foreground whitespace-nowrap ml-4">
                            {event.timestamp}
                          </time>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Timeline Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="text-sm text-muted-foreground">Total Events</div>
              <div className="text-3xl font-bold mt-2">47</div>
              <p className="text-xs text-muted-foreground mt-2">Last 30 days</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="text-sm text-muted-foreground">Uploads</div>
              <div className="text-3xl font-bold mt-2">12</div>
              <p className="text-xs text-muted-foreground mt-2">New evidence items</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="text-sm text-muted-foreground">Avg Analysis Time</div>
              <div className="text-3xl font-bold mt-2">3.2m</div>
              <p className="text-xs text-muted-foreground mt-2">Per file</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  )
}
