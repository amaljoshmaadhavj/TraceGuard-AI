'use client'

import { AppLayout } from '@/components/layout/app-layout'
import { PageHeader } from '@/components/common/page-header'
import { StatCard } from '@/components/common/stat-card'
import { EvidenceCard } from '@/components/common/evidence-card'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ShieldAlert, TrendingUp, AlertTriangle, CheckCircle2, Clock, BarChart3, Activity } from 'lucide-react'
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { useEffect, useState } from 'react'

interface DashboardStats {
  total_events: number
  total_files: number
  total_techniques: number
  events_by_category: Record<string, number>
  severity_distribution: Record<string, number>
}

interface EvidenceItem {
  id: string
  title: string
  type: 'image' | 'file'
  status: 'pending' | 'analyzing' | 'suspected' | 'confirmed'
  confidence?: number
  uploadDate: string
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [evidence, setEvidence] = useState<EvidenceItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsRes, filesRes] = await Promise.all([
          fetch('http://localhost:8001/api/stats/'),
          fetch('http://localhost:8001/api/files/')
        ])
        
        const statsData = await statsRes.json()
        const filesData = await filesRes.json()
        
        setStats(statsData)
        
        if (filesData && filesData.files) {
          const mappedFiles: EvidenceItem[] = filesData.files.slice(0, 4).map((f: any) => ({
            id: f.id,
            title: f.filename,
            type: f.filename.endsWith('.evtx') ? 'file' : 'image',
            status: f.status === 'completed' ? 'confirmed' : 'analyzing',
            confidence: f.status === 'completed' ? 94 : undefined,
            uploadDate: new Date(f.upload_time).toLocaleDateString()
          }))
          setEvidence(mappedFiles)
        }
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const chartData = stats ? Object.entries(stats.events_by_category).map(([name, value]) => ({
    date: name.split('_').pop() || name,
    cases: value
  })) : []

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <PageHeader
          title="Investigation Overview"
          description="Real-time monitoring of active forensic streams and system metrics"
          icon={<Activity className="w-8 h-8 text-primary" />}
        />

        {/* Key Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Events"
            value={stats?.total_events.toString() || "0"}
            icon={<ShieldAlert className="w-5 h-5 text-muted-foreground" />}
            change={{ value: 12, label: 'vs last week', trend: 'up' }}
            className="card-professional"
          />
          <StatCard
            title="Evidence Files"
            value={stats?.total_files.toString() || "0"}
            icon={<CheckCircle2 className="w-5 h-5 text-muted-foreground" />}
            change={{ value: stats?.total_files || 0, label: 'total files', trend: 'up' }}
            className="card-professional"
          />
          <StatCard
            title="Techniques Identified"
            value={stats?.total_techniques.toString() || "0"}
            icon={<Clock className="w-5 h-5 text-muted-foreground" />}
            change={{ value: 2, label: 'new patterns', trend: 'up' }}
            className="card-professional"
          />
          <StatCard
            title="System Confidence"
            value="94.2%"
            icon={<TrendingUp className="w-5 h-5 text-muted-foreground" />}
            change={{ value: 2.3, label: 'sync accuracy', trend: 'up' }}
            className="card-professional"
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Cases Over Time */}
          <Card className="lg:col-span-2 card-professional overflow-hidden">
            <CardHeader className="bg-secondary/30 border-b border-border/50">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-sm font-bold tracking-tight flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-primary" />
                    Event Distribution
                  </CardTitle>
                  <CardDescription className="text-xs">Category-based analysis over time</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-6">
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={chartData.length > 0 ? chartData : [{date: 'N/A', cases: 0}]}>
                  <defs>
                    <linearGradient id="colorCases" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis 
                    dataKey="date" 
                    stroke="var(--muted-foreground)" 
                    fontSize={11} 
                    tickLine={false} 
                    axisLine={false}
                    tickMargin={12}
                  />
                  <YAxis 
                    stroke="var(--muted-foreground)" 
                    fontSize={11} 
                    tickLine={false} 
                    axisLine={false}
                    tickMargin={12}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'var(--card)', 
                      border: '1px solid var(--border)', 
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                    }}
                    itemStyle={{ color: 'var(--primary)', fontSize: '12px', fontWeight: 'bold' }}
                    labelStyle={{ color: 'var(--muted-foreground)', marginBottom: '4px', fontSize: '10px', textTransform: 'uppercase' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="cases" 
                    stroke="var(--primary)" 
                    strokeWidth={2} 
                    fillOpacity={1} 
                    fill="url(#colorCases)" 
                    activeDot={{ r: 6, strokeWidth: 0 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Detection Rate */}
          <Card className="card-professional">
            <CardHeader className="bg-secondary/30 border-b border-border/50">
              <CardTitle className="text-sm font-bold tracking-tight">Severity Profile</CardTitle>
              <CardDescription className="text-xs">Identified risk levels</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-6">
                {stats ? Object.entries(stats.severity_distribution).map(([level, count]) => {
                  const percentage = (count / stats.total_events) * 100;
                  const colorClass = level === 'critical' ? 'bg-red-500' : level === 'high' ? 'bg-orange-500' : 'bg-primary';
                  return (
                    <div key={level} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{level}</span>
                        <span className="text-xs font-bold">{count}</span>
                      </div>
                      <div className="w-full bg-secondary rounded-full h-1.5 overflow-hidden">
                        <div className={`${colorClass} h-1.5 rounded-full transition-all duration-500`} style={{width: `${percentage}%`}}></div>
                      </div>
                    </div>
                  )
                }) : (
                  <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground gap-3">
                    <Activity className="w-8 h-8 animate-pulse text-muted-foreground/30" />
                    <span className="text-xs font-medium italic">Calculating metrics...</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Evidence */}
        <Card className="card-professional overflow-hidden">
          <CardHeader className="bg-secondary/30 border-b border-border/50 flex flex-row items-center justify-between space-y-0">
            <div>
              <CardTitle className="text-sm font-bold tracking-tight">Recent Evidence Ingestion</CardTitle>
              <CardDescription className="text-xs">Latest forensic artifacts processed by the engine</CardDescription>
            </div>
            <Button variant="ghost" size="sm" className="text-xs font-semibold">View all</Button>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {loading ? (
                Array(4).fill(0).map((_, i) => (
                  <div key={i} className="h-40 rounded-xl bg-secondary/50 animate-pulse border border-border/50" />
                ))
              ) : evidence.length > 0 ? (
                evidence.map((item) => (
                  <EvidenceCard key={item.id} {...item} />
                ))
              ) : (
                <div className="col-span-full py-16 text-center">
                  <Activity className="w-12 h-12 text-muted-foreground/20 mx-auto mb-4" />
                  <p className="text-sm font-medium text-muted-foreground">No active ingestions found in current stream</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Risk Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-orange-200 bg-orange-50 dark:border-orange-900/30 dark:bg-orange-900/10">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-orange-600 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                Detections Found
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-orange-700 dark:text-orange-400">{stats?.total_events || 0}</div>
              <p className="text-xs text-orange-600/70 mt-1">Requiring manual verification</p>
            </CardContent>
          </Card>
          
          <Card className="border-red-200 bg-red-50 dark:border-red-900/30 dark:bg-red-900/10">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-red-600 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                Critical Hazards
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-red-700 dark:text-red-400">{stats?.severity_distribution.critical || 0}</div>
              <p className="text-xs text-red-600/70 mt-1">Immediate action required</p>
            </CardContent>
          </Card>

          <Card className="border-emerald-200 bg-emerald-50 dark:border-emerald-900/30 dark:bg-emerald-900/10">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-emerald-600 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                Integrity Checks
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-emerald-700 dark:text-emerald-400">{stats?.total_files || 0}</div>
              <p className="text-xs text-emerald-600/70 mt-1">Successfully processed streams</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  )
}
