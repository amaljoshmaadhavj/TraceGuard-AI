'use client'

import { AppLayout } from '@/components/layout/app-layout'
import { PageHeader } from '@/components/common/page-header'
import { StatCard } from '@/components/common/stat-card'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, TrendingUp, Users, Zap, Shield, PieChart as PieIcon, Activity } from 'lucide-react'
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { useEffect, useState } from 'react'

interface StatsData {
  total_events: number
  total_files: number
  total_techniques: number
  events_by_category: Record<string, number>
  severity_distribution: Record<string, number>
  techniques_list: string[]
}

export default function StatisticsPage() {
  const [stats, setStats] = useState<StatsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchStats() {
      try {
        const response = await fetch('http://localhost:8001/api/stats/')
        const data = await response.json()
        setStats(data)
      } catch (error) {
        console.error('Failed to fetch statistics:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [])

  const categoryData = stats ? Object.entries(stats.events_by_category).map(([name, value]) => ({
    name: name.replace(/_/g, ' ').toUpperCase(),
    value: value
  })) : []

  const severityData = stats ? Object.entries(stats.severity_distribution).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value: value
  })) : []

  const COLORS = ['#1e293b', '#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

  if (loading) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
          <Activity className="w-10 h-10 text-primary animate-spin" />
          <div className="text-muted-foreground font-medium animate-pulse text-sm">Synchronizing forensic data...</div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8 space-y-8">
        <PageHeader
          title="Statistics & Analytics"
          description="Detailed forensic metric distribution and threat intelligence analysis"
          icon={<BarChart3 className="w-8 h-8 text-primary" />}
        />

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Events"
            value={stats?.total_events.toString() || "0"}
            icon={<Zap className="w-5 h-5 text-muted-foreground" />}
            change={{ value: 23, label: 'vs baseline', trend: 'up' }}
            className="card-professional"
          />
          <StatCard
            title="Evidence Files"
            value={stats?.total_files.toString() || "0"}
            icon={<TrendingUp className="w-5 h-5 text-muted-foreground" />}
            change={{ value: 8, label: 'new artifacts', trend: 'up' }}
            className="card-professional"
          />
          <StatCard
            title="Attack Vectors"
            value={stats?.total_techniques.toString() || "0"}
            icon={<Users className="w-5 h-5 text-muted-foreground" />}
            change={{ value: 2.3, label: 'pattern matches', trend: 'up' }}
            className="card-professional"
          />
          <StatCard
            title="System Stability"
            value="99.9%"
            icon={<Shield className="w-5 h-5 text-muted-foreground" />}
            change={{ value: 0.1, label: 'uptime', trend: 'up' }}
            className="card-professional"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Category Distribution */}
          <Card className="card-professional overflow-hidden">
            <CardHeader className="bg-secondary/30 border-b border-border/50">
              <CardTitle className="text-sm font-bold tracking-tight">Evidence Categories</CardTitle>
              <CardDescription className="text-xs">Distribution of detected events by forensic type</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis 
                    dataKey="name" 
                    stroke="var(--muted-foreground)" 
                    fontSize={10} 
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis 
                    stroke="var(--muted-foreground)" 
                    fontSize={10} 
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'var(--card)', 
                      border: '1px solid var(--border)',
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                    }}
                    cursor={{fill: 'var(--secondary)', opacity: 0.5}}
                  />
                  <Bar dataKey="value" fill="var(--primary)" radius={[4, 4, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Severity Pie */}
          <Card className="card-professional overflow-hidden">
            <CardHeader className="bg-secondary/30 border-b border-border/50">
              <CardTitle className="text-sm font-bold tracking-tight">Severity Profile</CardTitle>
              <CardDescription className="text-xs">Threat level distribution across current investigation</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={90}
                    paddingAngle={8}
                    dataKey="value"
                    stroke="none"
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'var(--card)', 
                      border: '1px solid var(--border)',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend 
                    verticalAlign="bottom" 
                    height={36} 
                    iconType="circle"
                    formatter={(value) => <span className="text-xs font-medium text-muted-foreground">{value}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* MITRE Techniques */}
        <Card className="card-professional overflow-hidden">
          <CardHeader className="bg-secondary/30 border-b border-border/50">
            <CardTitle className="text-sm font-bold tracking-tight flex items-center gap-2">
              <Shield className="w-4 h-4 text-primary" />
              Detected MITRE ATT&CK Techniques
            </CardTitle>
            <CardDescription className="text-xs">Identified adversarial patterns and vectors</CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {stats?.techniques_list.map((tech, idx) => (
                <div key={idx} className="flex items-center gap-3 p-4 rounded-xl border border-border bg-secondary/20 hover:bg-secondary/40 transition-colors group">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary group-hover:scale-125 transition-transform" />
                  <span className="text-xs font-semibold text-foreground/80">{tech}</span>
                </div>
              ))}
              {(!stats || stats.techniques_list.length === 0) && (
                <div className="col-span-full py-8 text-center text-muted-foreground text-sm italic">
                  No specific techniques identified in current stream.
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
