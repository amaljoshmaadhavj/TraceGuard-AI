'use client'

import { Sidebar } from './sidebar'
import { MobileNav } from './mobile-nav'

export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar - Desktop only */}
      <Sidebar />

      {/* Mobile Nav */}
      <MobileNav />

      {/* Main Content */}
      <main className="flex-1 w-full lg:ml-64 pt-16 lg:pt-0">
        {children}
      </main>
    </div>
  )
}
