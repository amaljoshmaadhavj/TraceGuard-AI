import { Card, CardContent } from '@/components/ui/card'
import { StatusBadge } from './status-badge'
import { FileIcon, Image, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface EvidenceCardProps {
  id: string
  title: string
  type: 'image' | 'file' | 'text'
  status: 'pending' | 'analyzing' | 'suspected' | 'confirmed' | 'resolved' | 'unknown'
  confidence?: number
  uploadDate: string
  className?: string
  onClick?: () => void
}

export function EvidenceCard({
  id,
  title,
  type,
  status,
  confidence,
  uploadDate,
  className,
  onClick,
}: EvidenceCardProps) {
  const getIcon = () => {
    switch (type) {
      case 'image':
        return <Image className="w-8 h-8 text-primary" />
      case 'text':
        return <AlertCircle className="w-8 h-8 text-primary" />
      default:
        return <FileIcon className="w-8 h-8 text-primary" />
    }
  }

  return (
    <Card
      className={cn(
        'cursor-pointer hover:shadow-lg transition-shadow',
        className
      )}
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="space-y-3">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1">
              <h3 className="font-semibold text-sm truncate">{title}</h3>
              <p className="text-xs text-muted-foreground mt-1">ID: {id.slice(0, 8)}...</p>
            </div>
            {getIcon()}
          </div>

          <div className="flex items-center justify-between gap-2">
            <StatusBadge status={status} />
            {confidence !== undefined && (
              <div className="text-xs font-medium">
                {confidence}% confident
              </div>
            )}
          </div>

          <p className="text-xs text-muted-foreground">
            Uploaded: {uploadDate}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
