'use client'

import { useState, useRef, useEffect } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { PageHeader } from '@/components/common/page-header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Microscope, Send, Loader, AlertCircle, CheckCircle2, FileText, Activity, MessageSquare } from 'lucide-react'
import { TimelineView } from '@/components/timeline-view'
import Link from 'next/link'

interface Message {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
  isTimeline?: boolean
  timelineData?: {
    events: any[]
    summary: string
    dateRange: { start: string; end: string }
    confidence: number
    query: string
  }
}

interface UploadedFile {
  id: string
  filename: string
  category: string
  file_type: string
  size: number
  upload_date: string
  status: string
  analysis_type?: string
  notes?: string
}

export default function InvestigationPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [filesLoading, setFilesLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const queryInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    loadUploadedFiles()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadUploadedFiles = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/files/')
      if (!response.ok) throw new Error('Failed to load files')
      const data = await response.json()
      setUploadedFiles(data.files || [])
      setError(null)
    } catch (err) {
      console.error('Error loading files:', err)
      setError('Could not load uploaded files')
      setUploadedFiles([])
    } finally {
      setFilesLoading(false)
    }
  }

  const handleSubmitQuery = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || loading) return

    if (uploadedFiles.length === 0) {
      setError('Please upload evidence artifacts first.')
      return
    }

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      type: 'user',
      content: query,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setQuery('')
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8001/api/query/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query, top_k: 5 }),
      })

      if (!response.ok) throw new Error(`Server error: ${response.statusText}`)

      const data = await response.json()

      if (data.is_timeline && data.events) {
        const timelineMessage: Message = {
          id: `msg-${Date.now()}-timeline`,
          type: 'ai',
          content: 'Timeline Analysis',
          timestamp: new Date(),
          isTimeline: true,
          timelineData: {
            events: data.events,
            summary: data.summary || '',
            dateRange: data.date_range || { start: '', end: '' },
            confidence: data.confidence || 0,
            query: data.query
          }
        }
        setMessages((prev) => [...prev, timelineMessage])
      } else {
        const aiMessage: Message = {
          id: `msg-${Date.now()}-ai`,
          type: 'ai',
          content: data.response || 'Analysis complete. No specific patterns identified in current slice.',
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, aiMessage])
      }
    } catch (err) {
      console.error('Query error:', err)
      const errorMessage: Message = {
        id: `msg-${Date.now()}-error`,
        type: 'ai',
        content: `Error: ${err instanceof Error ? err.message : 'System communication failed.'}`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8 h-[calc(100vh-2rem)] flex flex-col space-y-8">
        <PageHeader
          title="Analysis Lab"
          description="Interactive investigation of forensic artifacts using AI-powered pattern recognition"
          icon={<Microscope className="w-8 h-8 text-primary" />}
          action={
            <Link href="/upload">
              <Button className="font-bold h-11 px-6 shadow-lg shadow-primary/10">Upload New Evidence</Button>
            </Link>
          }
        />

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 flex-1 min-h-0">
          {/* Artifacts Panel */}
          <Card className="lg:col-span-1 flex flex-col card-professional overflow-hidden">
            <CardHeader className="bg-secondary/30 border-b border-border/50">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Ingested Artifacts</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-3">
              {filesLoading ? (
                <div className="flex flex-col items-center justify-center py-12 gap-3">
                  <Activity className="w-6 h-6 animate-spin text-muted-foreground/30" />
                  <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/40">Syncing...</span>
                </div>
              ) : uploadedFiles.length === 0 ? (
                <div className="text-center py-12 border-2 border-dashed border-border rounded-xl bg-secondary/10">
                  <FileText className="w-8 h-8 text-muted-foreground/30 mx-auto mb-3" />
                  <p className="text-xs font-bold text-muted-foreground/60 uppercase tracking-wider mb-4">No data ingested</p>
                  <Link href="/upload">
                    <Button size="sm" variant="outline" className="text-[10px] font-bold uppercase tracking-widest">
                      Ingest Data
                    </Button>
                  </Link>
                </div>
              ) : (
                uploadedFiles.map((file) => (
                  <div key={file.id} className="p-4 rounded-xl bg-card border border-border group hover:border-primary/50 transition-colors">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center text-muted-foreground group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                        <FileText className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-bold truncate leading-tight">{file.filename}</p>
                        <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-widest mt-1">{file.category}</p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {/* Analysis Hub */}
          <Card className="lg:col-span-3 flex flex-col card-professional overflow-hidden">
            <CardHeader className="bg-secondary/30 border-b border-border/50">
              <div className="flex items-center gap-3">
                <MessageSquare className="w-4 h-4 text-primary" />
                <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Interactive Investigation Hub</CardTitle>
              </div>
            </CardHeader>

            <CardContent className="flex-1 overflow-y-auto p-6 space-y-6">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center max-w-sm mx-auto space-y-6 opacity-40">
                  <div className="w-20 h-20 rounded-full bg-secondary flex items-center justify-center">
                    <Microscope className="w-10 h-10 text-muted-foreground" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold uppercase tracking-widest mb-2">Awaiting Inquiry</h3>
                    <p className="text-xs font-medium leading-relaxed">
                      {uploadedFiles.length === 0
                        ? 'Please ingest evidence artifacts to begin analysis.'
                        : 'Pose a question about your forensic dataset to initialize analysis.'}
                    </p>
                  </div>
                </div>
              ) : (
                messages.map((msg) => (
                  <div key={msg.id} className={`flex gap-4 ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    {msg.type === 'user' ? (
                      <div className="max-w-[80%] px-5 py-3 rounded-2xl bg-primary text-primary-foreground shadow-sm">
                        <p className="text-sm font-medium leading-relaxed">{msg.content}</p>
                        <p className="text-[10px] mt-2 font-bold uppercase tracking-widest opacity-60">{msg.timestamp.toLocaleTimeString()}</p>
                      </div>
                    ) : msg.isTimeline && msg.timelineData ? (
                      <div className="w-full">
                        <TimelineView
                          events={msg.timelineData.events}
                          summary={msg.timelineData.summary}
                          dateRange={msg.timelineData.dateRange}
                          confidence={msg.timelineData.confidence}
                          query={msg.timelineData.query}
                        />
                      </div>
                    ) : (
                      <div className="max-w-[85%] px-6 py-4 rounded-2xl bg-secondary/50 border border-border shadow-sm">
                        <p className="text-sm font-medium leading-relaxed text-foreground/90 whitespace-pre-wrap">{msg.content}</p>
                        <p className="text-[10px] mt-3 font-bold uppercase tracking-widest text-muted-foreground">{msg.timestamp.toLocaleTimeString()}</p>
                      </div>
                    )}
                  </div>
                ))
              )}

              {loading && (
                <div className="flex justify-start">
                  <div className="bg-secondary/50 border border-border px-6 py-4 rounded-2xl flex items-center gap-3">
                    <Loader className="w-4 h-4 animate-spin text-primary" />
                    <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Analyzing Pattern...</span>
                  </div>
                </div>
              )}

              {error && (
                <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 dark:bg-rose-950/20 dark:border-rose-900/30 flex gap-3 mx-auto max-w-md">
                  <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
                  <p className="text-xs font-bold text-rose-700 dark:text-rose-400 uppercase tracking-wider">{error}</p>
                </div>
              )}

              <div ref={messagesEndRef} />
            </CardContent>

            <div className="p-6 bg-secondary/10 border-t border-border/50">
              <form onSubmit={handleSubmitQuery} className="flex gap-3 relative">
                <Input
                  ref={queryInputRef}
                  placeholder="Pose a forensic inquiry..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  disabled={loading || uploadedFiles.length === 0}
                  className="flex-1 h-12 px-5 bg-card border-border shadow-sm focus-visible:ring-primary/20 rounded-xl font-medium"
                />
                <Button
                  type="submit"
                  disabled={loading || !query.trim() || uploadedFiles.length === 0}
                  className="h-12 w-12 rounded-xl p-0 flex items-center justify-center transition-all active:scale-95"
                >
                  {loading ? (
                    <Loader className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </Button>
              </form>
              <div className="flex items-center gap-4 mt-3 px-1 overflow-x-auto no-scrollbar">
                {['Suspicious patterns', 'Credential access', 'MITRE ATT&CK'].map((tip) => (
                  <button
                    key={tip}
                    type="button"
                    onClick={() => setQuery(tip)}
                    disabled={loading || uploadedFiles.length === 0}
                    className="whitespace-nowrap text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60 hover:text-primary transition-colors"
                  >
                    {tip}
                  </button>
                ))}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </AppLayout>
  )
}
