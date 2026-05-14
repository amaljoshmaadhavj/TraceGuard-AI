'use client'

import { useState, useRef } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { PageHeader } from '@/components/common/page-header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Upload, CheckCircle2, AlertCircle, FileIcon, FileText, Info } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'

interface UploadedFile {
  id: string
  name: string
  size: string
  type: string
  status: 'completed' | 'uploading' | 'pending'
  file: File
}

export default function UploadPage() {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [dragActive, setDragActive] = useState(false)
  const [category, setCategory] = useState('execution')
  const [notes, setNotes] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const droppedFiles = Array.from(e.dataTransfer.files)
    addFiles(droppedFiles)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files)
      addFiles(selectedFiles)
    }
  }

  const addFiles = (newFiles: File[]) => {
    const newUploadedFiles = newFiles.map((file) => ({
      id: `file-${Date.now()}-${Math.random()}`,
      name: file.name,
      size: `${(file.size / 1024 / 1024).toFixed(2)} MB`,
      type: getFileType(file.name),
      status: 'completed' as const,
      file: file,
    }))
    setFiles((prev) => [...prev, ...newUploadedFiles])
    setUploadError(null)
    setUploadSuccess(false)
  }

  const getFileType = (filename: string): string => {
    if (filename.endsWith('.evtx')) return 'Windows Event Log'
    if (filename.endsWith('.pcap')) return 'Network Capture'
    return 'Forensic Evidence'
  }

  const handleSelectFilesClick = () => {
    fileInputRef.current?.click()
  }

  const getFileIcon = (type: string) => {
    return <FileText className="w-5 h-5 text-primary" />
  }

  const handleStartAnalysis = async () => {
    if (files.length === 0) {
      setUploadError('Please select files to upload')
      return
    }

    setUploading(true)
    setUploadError(null)
    setUploadSuccess(false)

    try {
      for (const uploadedFile of files) {
        const formData = new FormData()
        formData.append('file', uploadedFile.file)
        formData.append('category', category)
        formData.append('notes', notes)

        const response = await fetch('http://localhost:8001/api/files/upload', {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          throw new Error(`Failed to upload ${uploadedFile.name}: ${response.statusText}`)
        }
      }

      setUploadSuccess(true)
      setFiles([])
      setNotes('')
      
      setTimeout(() => {
        setUploadSuccess(false)
      }, 5000)

    } catch (error) {
      console.error('Upload error:', error)
      setUploadError(
        error instanceof Error 
          ? error.message 
          : 'Failed to upload files. Please try again.'
      )
    } finally {
      setUploading(false)
    }
  }

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8 space-y-8">
        <PageHeader
          title="Evidence Ingestion"
          description="Upload digital artifacts for forensic analysis and pattern recognition"
          icon={<Upload className="w-8 h-8 text-primary" />}
        />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Area */}
          <Card className="lg:col-span-2 card-professional overflow-hidden">
            <CardHeader className="bg-secondary/30 border-b border-border/50">
              <CardTitle className="text-sm font-bold tracking-tight">File Ingestion</CardTitle>
              <CardDescription className="text-xs">Drag artifacts or click to browse</CardDescription>
            </CardHeader>
            <CardContent className="p-8 space-y-6">
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-200 ${
                  dragActive
                    ? 'border-primary bg-primary/5 scale-[1.01]'
                    : 'border-border bg-secondary/20 hover:border-primary/50'
                }`}
              >
                <div className="w-16 h-16 rounded-full bg-background border border-border flex items-center justify-center mx-auto mb-6 shadow-sm">
                  <Upload className="w-8 h-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-bold mb-2">Drop forensic artifacts here</h3>
                <p className="text-sm text-muted-foreground mb-8 max-w-xs mx-auto">
                  Supports system event logs, network captures, and digital evidence files.
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  onChange={handleChange}
                  className="hidden"
                  id="file-input"
                  accept=".evtx,.pcap"
                />
                <Button
                  variant="outline"
                  size="lg"
                  className="px-8 font-semibold"
                  onClick={handleSelectFilesClick}
                >
                  Select Artifacts
                </Button>
              </div>

              {/* Uploaded Files List */}
              {files.length > 0 && (
                <div className="space-y-4 pt-4 border-t border-border">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Queued Artifacts ({files.length})</h4>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-64 overflow-y-auto pr-2">
                    {files.map((file) => (
                      <div
                        key={file.id}
                        className="flex items-center gap-3 p-4 rounded-xl bg-card border border-border shadow-sm group hover:border-primary/50 transition-colors"
                      >
                        <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center text-muted-foreground group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                          <FileText className="w-5 h-5" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-bold truncate leading-tight">{file.name}</p>
                          <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-widest mt-1">{file.size}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Options Panel */}
          <div className="space-y-6">
            <Card className="card-professional overflow-hidden">
              <CardHeader className="bg-secondary/30 border-b border-border/50">
                <CardTitle className="text-sm font-bold tracking-tight">Analysis Configuration</CardTitle>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="category" className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Forensic Category</Label>
                  <Select value={category} onValueChange={setCategory}>
                    <SelectTrigger id="category" className="h-11">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="execution">Execution Analysis</SelectItem>
                      <SelectItem value="credential_access">Credential Access</SelectItem>
                      <SelectItem value="lateral_movement">Lateral Movement</SelectItem>
                      <SelectItem value="network_logs">Network Forensic Logs</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {files.length > 0 && (
                  <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 dark:bg-blue-950/20 dark:border-blue-900/30 flex gap-2">
                    <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs font-bold text-blue-700 dark:text-blue-400">Category applies to all files</p>
                      <p className="text-xs text-blue-600 dark:text-blue-300 mt-1">All {files.length} file(s) will be uploaded to <span className="font-bold capitalize">{category.replace('_', ' ')}</span>.</p>
                      <p className="text-xs text-blue-600 dark:text-blue-300 mt-1">To upload files to different categories, upload in separate batches.</p>
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="notes" className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Investigation Notes</Label>
                  <Textarea
                    id="notes"
                    placeholder="Provide context for the forensic engine..."
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    className="resize-none h-32 text-sm"
                  />
                </div>

                {uploadError && (
                  <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 dark:bg-rose-950/20 dark:border-rose-900/30 flex gap-3">
                    <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
                    <p className="text-xs font-medium text-rose-700 dark:text-rose-400">{uploadError}</p>
                  </div>
                )}

                {uploadSuccess && (
                  <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 dark:bg-emerald-950/20 dark:border-emerald-900/30 flex gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
                    <p className="text-xs font-medium text-emerald-700 dark:text-emerald-400">Artifacts successfully ingested. Analyzing streams now.</p>
                  </div>
                )}

                <Button
                  className="w-full h-12 font-bold shadow-lg shadow-primary/10"
                  disabled={files.length === 0 || uploading}
                  onClick={handleStartAnalysis}
                >
                  {uploading ? (
                    <span className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded-full border-2 border-primary-foreground/30 border-t-primary-foreground animate-spin" />
                      Ingesting...
                    </span>
                  ) : 'Initialize Analysis'}
                </Button>

                <Button
                  variant="ghost"
                  className="w-full text-xs font-bold text-muted-foreground hover:text-foreground"
                  onClick={() => {
                    setFiles([])
                    setNotes('')
                  }}
                >
                  Clear Queue
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-secondary/20 border-border/50">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                  <Info className="w-3.5 h-3.5" />
                  Guidelines
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 text-[11px] font-medium text-muted-foreground leading-relaxed">
                  <li className="flex gap-2">
                    <span className="text-primary">•</span>
                    <span>Upload .evtx files for system execution artifacts.</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary">•</span>
                    <span>Use .pcap for deep-packet network forensics.</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary">•</span>
                    <span>Detailed notes improve pattern recognition accuracy.</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
