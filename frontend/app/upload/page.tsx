'use client'

import { useState, useRef } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { PageHeader } from '@/components/common/page-header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Upload, CheckCircle2, AlertCircle, FileIcon } from 'lucide-react'
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
  const [analysisType, setAnalysisType] = useState('general')
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
    return <FileIcon className="w-5 h-5 text-blue-500" />
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
      const uploadedFiles = []
      
      // Upload each file to the backend
      for (const uploadedFile of files) {
        const formData = new FormData()
        formData.append('file', uploadedFile.file)
        formData.append('analysis_type', analysisType)
        formData.append('notes', notes)

        const response = await fetch('http://localhost:8001/api/files/upload', {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          throw new Error(`Failed to upload ${uploadedFile.name}: ${response.statusText}`)
        }

        const data = await response.json()
        uploadedFiles.push(data)
      }

      // Success!
      setUploadSuccess(true)
      setFiles([])
      setNotes('')
      setAnalysisType('general')
      
      // Auto-clear success message after 5 seconds
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
      <div className="px-4 lg:px-8 py-8 space-y-8">
        <PageHeader
          title="Upload Evidence"
          description="Upload digital evidence for AI analysis and forensic investigation"
          icon={<Upload className="w-8 h-8" />}
        />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Upload Area */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Upload Files</CardTitle>
              <CardDescription>Drag and drop or click to select files</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Drag and Drop Area */}
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="font-semibold mb-2">Drag files here or click to browse</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Supports EVTX (Windows Event Logs) and PCAP (Network Captures)
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
                  className="cursor-pointer"
                  onClick={handleSelectFilesClick}
                >
                  Select Files
                </Button>
              </div>

              {/* Uploaded Files List */}
              {files.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-medium text-sm">Uploaded Files ({files.length})</h4>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {files.map((file) => (
                      <div
                        key={file.id}
                        className="flex items-center justify-between p-3 rounded-lg bg-muted/50 border border-border"
                      >
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          {getFileIcon(file.type)}
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium truncate">{file.name}</p>
                            <p className="text-xs text-muted-foreground">{file.size}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                          {file.status === 'completed' && (
                            <CheckCircle2 className="w-5 h-5 text-green-500" />
                          )}
                          {file.status === 'uploading' && (
                            <div className="w-5 h-5 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Options Panel */}
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Analysis Options</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="analysis-type">Analysis Type</Label>
                  <Select value={analysisType} onValueChange={setAnalysisType}>
                    <SelectTrigger id="analysis-type">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="general">General Analysis</SelectItem>
                      <SelectItem value="image">Image Analysis</SelectItem>
                      <SelectItem value="video">Video Analysis</SelectItem>
                      <SelectItem value="audio">Audio Analysis</SelectItem>
                      <SelectItem value="deepfake">Deepfake Detection</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="notes">Notes</Label>
                  <Textarea
                    id="notes"
                    placeholder="Add any relevant context or notes about this evidence..."
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    className="resize-none h-24"
                  />
                </div>

                {/* Error Message */}
                {uploadError && (
                  <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/50 flex gap-2">
                    <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-500">{uploadError}</p>
                  </div>
                )}

                {/* Success Message */}
                {uploadSuccess && (
                  <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/50 flex gap-2">
                    <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-green-500">Files uploaded successfully! Start your investigation.</p>
                  </div>
                )}

                <Button
                  className="w-full bg-primary hover:bg-primary/90"
                  disabled={files.length === 0 || uploading}
                  onClick={handleStartAnalysis}
                >
                  {uploading ? 'Uploading...' : 'Start Analysis'}
                </Button>

                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => {
                    setFiles([])
                    setNotes('')
                    setAnalysisType('general')
                  }}
                >
                  Clear All
                </Button>
              </CardContent>
            </Card>

            {/* Quick Tips */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Tips</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex gap-2">
                    <span className="text-primary">•</span>
                    <span>Upload Windows Event Logs (.evtx) for system activity analysis</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary">•</span>
                    <span>Upload PCAP files (.pcap) for network traffic analysis</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary">•</span>
                    <span>Add context notes for faster investigation and analysis</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary">•</span>
                    <span>Results include MITRE ATT&CK technique mapping</span>
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
