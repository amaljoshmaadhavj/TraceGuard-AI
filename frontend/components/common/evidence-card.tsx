import { Card, CardContent } from '@/components/ui/card'
import { StatusBadge } from './status-badge'
import { FileIcon, Image, AlertCircle, FileText } from 'lucide-react'
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
        return <Image className="w-6 h-6" />
      case 'text':
        return <FileText className="w-6 h-6" />
      default:
        return <FileIcon className="w-6 h-6" />
    }
  }

  return (
    <Card
      className={cn(
        'card-professional group cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      <CardContent className="p-5">
        <div className="space-y-4">
          <div className="flex items-start justify-between gap-4">
            <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center text-muted-foreground group-hover:bg-primary group-hover:text-primary-foreground transition-colors duration-300">
              {getIcon()}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-bold text-sm truncate leading-tight">{title}</h3>
              <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-widest mt-1">Ref: {id.slice(0, 8)}</p>
            </div>
          </div>

          <div className="flex items-center justify-between gap-2 pt-2 border-t border-border/50">
            <StatusBadge status={status} />
            {confidence !== undefined && (
              <div className="flex flex-col items-end">
                <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Match</span>
                <span className="text-xs font-black">{confidence}%</span>
              </div>
            )}
          </div>

          <div className="flex items-center justify-between text-[10px] font-medium text-muted-foreground uppercase tracking-wide">
            <span>Entry Date</span>
            <span>{uploadDate}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
