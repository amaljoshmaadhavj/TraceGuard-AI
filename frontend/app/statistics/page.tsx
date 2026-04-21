'use client'

import { AppLayout } from '@/components/layout/app-layout'
import { PageHeader } from '@/components/common/page-header'
import { StatCard } from '@/components/common/stat-card'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, TrendingUp, Users, Zap, Shield } from 'lucide-react'
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
  AreaChart,
  Area,
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
    name: name.toUpperCase(),
    value: value
  })) : []

  const COLORS = ['oklch(0.78 0.22 150)', 'oklch(0.65 0.2 30)', 'oklch(0.55 0.15 250)', 'oklch(0.85 0.1 100)'];

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-primary font-mono animate-pulse">INIT_ANALYTICS_STREAM...</div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="px-4 lg:px-8 py-8 space-y-8">
        <PageHeader
          title="Statistics & Analytics"
          description="Live neural telemetry and forensic metric distribution"
          icon={<BarChart3 className="w-8 h-8" />}
        />

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Events"
            value={stats?.total_events.toString() || "0"}
            icon={<Zap className="w-5 h-5" />}
            change={{ value: 23, label: 'detection_node', trend: 'up' }}
          />
          <StatCard
            title="Evidence Files"
            value={stats?.total_files.toString() || "0"}
            icon={<TrendingUp className="w-5 h-5" />}
            change={{ value: 8, label: 'ingestion_rate', trend: 'up' }}
          />
          <StatCard
            title="Att&ck Vectors"
            value={stats?.total_techniques.toString() || "0"}
            icon={<Users className="w-5 h-5" />}
            change={{ value: 2.3, label: 'pattern_match', trend: 'up' }}
          />
          <StatCard
            title="System Uptime"
            value="99.9%"
            icon={<BarChart3 className="w-5 h-5" />}
            change={{ value: 0.1, label: 'stability', trend: 'up' }}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Category Distribution */}
          <Card className="card-premium border-primary/20">
            <CardHeader className="bg-primary/5 border-b border-primary/10">
              <CardTitle className="text-xs font-black uppercase tracking-widest text-primary">Evidence Categories</CardTitle>
              <CardDescription className="text-[10px] font-mono">Distribution of detected events by forensic type</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.32 0.05 155)" vertical={false} />
                  <XAxis dataKey="name" stroke="oklch(0.65 0.08 160)" fontSize={10} tick={{fill: 'oklch(0.65 0.08 160)'}} />
                  <YAxis stroke="oklch(0.65 0.08 160)" fontSize={10} tick={{fill: 'oklch(0.65 0.08 160)'}} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'oklch(0.12 0.015 160)', border: '1px solid oklch(0.78 0.22 150)' }}
                    itemStyle={{ color: 'oklch(0.78 0.22 150)', fontFamily: 'monospace' }}
                  />
                  <Bar dataKey="value" fill="oklch(0.78 0.22 150)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Severity Pie */}
          <Card className="card-premium border-primary/20">
            <CardHeader className="bg-primary/5 border-b border-primary/10">
              <CardTitle className="text-xs font-black uppercase tracking-widest text-primary">Severity Matrix</CardTitle>
              <CardDescription className="text-[10px] font-mono">Threat level distribution across dataset</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'oklch(0.12 0.015 160)', border: '1px solid oklch(0.78 0.22 150)' }}
                  />
                  <Legend verticalAlign="bottom" height={36}/>
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* MITRE Techniques */}
        <Card className="card-premium border-primary/20">
          <CardHeader className="bg-primary/5 border-b border-primary/10">
            <CardTitle className="text-xs font-black uppercase tracking-widest text-primary flex items-center gap-2">
              <Shield className="w-4 h-4" />
              Detected MITRE ATT&CK Techniques
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {stats?.techniques_list.map((tech, idx) => (
                <div key={idx} className="flex items-center gap-3 p-3 rounded border border-primary/10 bg-primary/5 hover:border-primary/30 transition-colors">
                  <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                  <span className="text-xs font-mono text-primary/80">{tech}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
