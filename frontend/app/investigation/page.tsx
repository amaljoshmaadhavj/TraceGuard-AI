'use client'

import { useState, useRef, useEffect } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { PageHeader } from '@/components/common/page-header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Microscope, Send, Loader, AlertCircle, CheckCircle2 } from 'lucide-react'
import Link from 'next/link'

interface Message {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
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

const mockInvestigations = [
  {
    id: 'INV-2024-001',
    title: 'Suspected AI-Generated Portrait',
    status: 'confirmed' as const,
    severity: 'high' as const,
    evidence: 'portrait_analysis.jpg',
    confidence: 94,
    createdAt: '2024-01-15',
    findings: [
      'Detected AI generation artifacts in background',
      'Inconsistent lighting patterns detected',
      'Facial proportions show generative model signatures',
    ],
  },
  {
    id: 'INV-2024-002',
    title: 'Manipulated Image Detection',
    status: 'confirmed' as const,
    severity: 'critical' as const,
    evidence: 'document_scan.pdf',
    confidence: 98,
    createdAt: '2024-01-14',
    findings: [
      'Digital manipulation detected in text regions',
      'Clone stamp tool evidence found',
      'Content insertion confirmed',
    ],
  },
  {
    id: 'INV-2024-003',
    title: 'Deepfake Video Detection',
    status: 'suspected' as const,
    severity: 'critical' as const,
    evidence: 'video_clip.mp4',
    confidence: 87,
    createdAt: '2024-01-13',
    findings: [
      'Facial reenactment patterns detected',
      'Eye movement inconsistencies identified',
      'Audio-visual sync discrepancies found',
    ],
  },
  {
    id: 'INV-2024-004',
    title: 'Text Authenticity Check',
    status: 'resolved' as const,
    severity: 'medium' as const,
    evidence: 'message_log.txt',
    confidence: 76,
    createdAt: '2024-01-12',
    findings: [
      'No AI generation markers found',
      'Writing style analysis complete',
      'Authenticity verified',
    ],
  },
]

const allEvidence = [
  { id: 'EV001', title: 'Image-2024-01-15.jpg', type: 'image' as const, status: 'confirmed' as const, confidence: 92, uploadDate: '2024-01-15' },
  { id: 'EV002', title: 'Document_scan.pdf', type: 'file' as const, status: 'confirmed' as const, confidence: 98, uploadDate: '2024-01-14' },
  { id: 'EV003', title: 'Screenshot_evidence.png', type: 'image' as const, status: 'suspected' as const, confidence: 78, uploadDate: '2024-01-14' },
  { id: 'EV004', title: 'Audio_recording.wav', type: 'file' as const, status: 'pending' as const, uploadDate: '2024-01-13' },
  { id: 'EV005', title: 'Presentation_slides.pptx', type: 'file' as const, status: 'analyzing' as const, uploadDate: '2024-01-13' },
  { id: 'EV006', title: 'Video_footage.mp4', type: 'file' as const, status: 'confirmed' as const, confidence: 87, uploadDate: '2024-01-12' },
]

export default function InvestigationPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [filesLoading, setFilesLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const queryInputRef = useRef<HTMLInputElement>(null)

  // Load uploaded files on mount
  useEffect(() => {
    loadUploadedFiles()
  }, [])

  // Auto-scroll to bottom
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
      setError('Please upload evidence files first before asking questions.')
      return
    }

    // Add user message
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
      // Send query to backend
      const response = await fetch('http://localhost:8001/api/query/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          top_k: 5,
        }),
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`)
      }

      const data = await response.json()

      // Add AI response
      const aiMessage: Message = {
        id: `msg-${Date.now()}-ai`,
        type: 'ai',
        content: data.response || 'No response generated',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMessage])
    } catch (err) {
      console.error('Query error:', err)
      const errorMessage: Message = {
        id: `msg-${Date.now()}-error`,
        type: 'ai',
        content: `Error: ${err instanceof Error ? err.message : 'Failed to get response from AI. Make sure the backend is running.'}`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppLayout>
      <div className="px-4 lg:px-8 py-8 space-y-8 h-[calc(100vh-120px)] flex flex-col">
        <PageHeader
          title="Investigations"
          description="Chat with AI about your uploaded forensic evidence"
          icon={<Microscope className="w-8 h-8" />}
          action={
            <Link href="/upload">
              <Button className="bg-primary hover:bg-primary/90">Upload Evidence</Button>
            </Link>
          }
        />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
          {/* Evidence Panel */}
          <Card className="lg:col-span-1 overflow-hidden flex flex-col">
            <CardHeader>
              <CardTitle className="text-base">Uploaded Evidence</CardTitle>
              <CardDescription>Files available for investigation</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto space-y-3">
              {filesLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader className="w-5 h-5 animate-spin text-muted-foreground" />
                </div>
              ) : uploadedFiles.length === 0 ? (
                <div className="text-center py-8">
                  <AlertCircle className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground mb-4">No evidence uploaded yet</p>
                  <Link href="/upload">
                    <Button size="sm" variant="outline" className="w-full">
                      Upload Evidence
                    </Button>
                  </Link>
                </div>
              ) : (
                uploadedFiles.map((file) => (
                  <div key={file.id} className="p-3 rounded-lg bg-muted/50 border border-border space-y-2">
                    <div className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{file.filename}</p>
                        <p className="text-xs text-muted-foreground">{file.category}</p>
                        {file.notes && (
                          <p className="text-xs text-muted-foreground italic mt-1">{file.notes}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2 text-xs">
                      <span className="px-2 py-1 rounded bg-primary/10 text-primary">{file.file_type}</span>
                      <span className="px-2 py-1 rounded bg-muted text-muted-foreground">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </span>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {/* Chat Panel */}
          <Card className="lg:col-span-2 overflow-hidden flex flex-col">
            <CardHeader>
              <CardTitle className="text-base">Investigation Chat</CardTitle>
              <CardDescription>Ask questions about your evidence</CardDescription>
            </CardHeader>

            {/* Messages */}
            <CardContent className="flex-1 overflow-y-auto space-y-4 mb-4">
              {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <Microscope className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-50" />
                    <p className="text-muted-foreground">
                      {uploadedFiles.length === 0
                        ? 'Upload evidence to start investigating'
                        : 'Ask a question about your evidence'}
                    </p>
                  </div>
                </div>
              ) : (
                messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex gap-3 ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        msg.type === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-foreground'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      <p className={`text-xs mt-1 ${msg.type === 'user' ? 'opacity-70' : 'text-muted-foreground'}`}>
                        {msg.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))
              )}

              {loading && (
                <div className="flex gap-3">
                  <div className="bg-muted px-4 py-2 rounded-lg">
                    <Loader className="w-4 h-4 animate-spin" />
                  </div>
                </div>
              )}

              {error && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/50 flex gap-2">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                  <p className="text-sm text-red-500">{error}</p>
                </div>
              )}

              <div ref={messagesEndRef} />
            </CardContent>

            {/* Query Input */}
            <div className="border-t p-4">
              <form onSubmit={handleSubmitQuery} className="flex gap-2">
                <Input
                  ref={queryInputRef}
                  placeholder="Ask a question about the evidence..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  disabled={loading || uploadedFiles.length === 0}
                  className="flex-1"
                />
                <Button
                  type="submit"
                  disabled={loading || !query.trim() || uploadedFiles.length === 0}
                  className="px-4"
                >
                  {loading ? (
                    <Loader className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </form>

              <p className="text-xs text-muted-foreground mt-2">
                Ask about suspicious patterns, MITRE ATT&CK techniques, credential access, and more.
              </p>
            </div>
          </Card>
        </div>
      </div>
    </AppLayout>
  )
}
