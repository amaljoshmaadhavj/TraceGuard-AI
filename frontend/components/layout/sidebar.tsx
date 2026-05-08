'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ShieldAlert, BarChart3, Upload, Microscope, Clock, Settings, Home, Activity } from 'lucide-react'
import { cn } from '@/lib/utils'

const navigationItems = [
  { href: '/', label: 'Overview', icon: Home },
  { href: '/dashboard', label: 'Monitor', icon: Activity },
  { href: '/upload', label: 'Evidence Ingestion', icon: Upload },
  { href: '/investigation', label: 'Analysis Lab', icon: Microscope },
  { href: '/timeline', label: 'Evidence Timeline', icon: Clock },
  { href: '/statistics', label: 'Forensic Metrics', icon: BarChart3 },
  { href: '/settings', label: 'System Settings', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="hidden lg:flex flex-col w-64 bg-sidebar border-r border-sidebar-border h-screen fixed left-0 top-0 z-40 transition-colors duration-200">
      {/* Logo */}
      <div className="p-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center text-primary-foreground shadow-sm">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div className="overflow-hidden">
            <h1 className="font-bold text-lg tracking-tight text-sidebar-foreground leading-none">TraceGuard</h1>
            <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-widest mt-1">AI Forensics</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-1 mt-2">
        {navigationItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group text-sm font-medium',
                isActive
                  ? 'bg-secondary text-primary'
                  : 'text-muted-foreground hover:bg-secondary/50 hover:text-sidebar-foreground'
              )}
            >
              <Icon className={cn("w-4.5 h-4.5 transition-colors", isActive ? "text-primary" : "text-muted-foreground group-hover:text-sidebar-foreground")} />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="p-4 rounded-xl bg-secondary/30 border border-sidebar-border/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">System Status</span>
            <span className="flex h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
          </div>
          <p className="text-xs font-bold text-sidebar-foreground">v2.4.0 Stable</p>
          <p className="text-[10px] text-muted-foreground mt-0.5">Verified Deployment</p>
        </div>
      </div>
    </aside>
  )
}
