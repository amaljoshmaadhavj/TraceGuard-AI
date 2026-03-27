'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ShieldAlert, BarChart3, Upload, Microscope, Clock, Settings, Home } from 'lucide-react'
import { cn } from '@/lib/utils'

const navigationItems = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/dashboard', label: 'Dashboard', icon: ShieldAlert },
  { href: '/upload', label: 'Upload Evidence', icon: Upload },
  { href: '/investigation', label: 'Investigation', icon: Microscope },
  { href: '/timeline', label: 'Timeline', icon: Clock },
  { href: '/statistics', label: 'Statistics', icon: BarChart3 },
  { href: '/settings', label: 'Settings', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="hidden lg:flex flex-col w-64 bg-background border-r border-primary/20 h-screen fixed left-0 top-0 z-40">
      {/* Logo */}
      <div className="p-8 border-b border-primary/20 bg-primary/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center shadow-[0_0_15px_rgba(0,255,65,0.4)]">
            <ShieldAlert className="w-6 h-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="font-black text-xs tracking-[0.3em] uppercase text-primary">TraceGuard</h1>
            <p className="text-[9px] font-mono font-bold text-primary/60 uppercase">Forensics_OS</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-3 mt-4">
        {navigationItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 group font-mono uppercase text-[11px] tracking-tight',
                isActive
                  ? 'bg-primary/20 text-primary border border-primary/30 shadow-[0_0_10px_rgba(0,255,65,0.1)]'
                  : 'text-muted-foreground hover:bg-primary/5 hover:text-primary'
              )}
            >
              <Icon className={cn("w-4 h-4 transition-transform group-hover:scale-110", isActive && "text-primary")} />
              <span className="font-bold">{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-6 border-t border-primary/20 bg-primary/5">
        <div className="px-5 py-4 rounded-xl bg-background border border-primary/20">
          <p className="text-[9px] font-mono font-black text-primary/40 mb-1 uppercase tracking-widest">System_Ver</p>
          <p className="text-xs font-black text-primary font-mono">1.9.0_BUILD_SEC</p>
        </div>
      </div>
    </aside>
  )
}
