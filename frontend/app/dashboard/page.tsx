'use client'

import { AppLayout } from '@/components/layout/app-layout'
import { PageHeader } from '@/components/common/page-header'
import { StatCard } from '@/components/common/stat-card'
import { EvidenceCard } from '@/components/common/evidence-card'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ShieldAlert, TrendingUp, AlertTriangle, CheckCircle2, Clock, BarChart3 } from 'lucide-react'
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
        
        // Map backend files to frontend EvidenceItem format
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
      <div className="px-4 lg:px-8 py-8 space-y-8">
        <PageHeader
          title="Dashboard"
          description="Real-time overview of forensic investigations and neural analysis"
          icon={<ShieldAlert className="w-8 h-8" />}
        />

        {/* Key Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Node Hits"
            value={stats?.total_events.toString() || "0"}
            icon={<ShieldAlert className="w-5 h-5" />}
            change={{ value: 12, label: 'buffer_growth', trend: 'up' }}
            className="card-premium border-primary/20"
          />
          <StatCard
            title="Evidence Files"
            value={stats?.total_files.toString() || "0"}
            icon={<CheckCircle2 className="w-5 h-5 text-glow" />}
            change={{ value: stats?.total_files || 0, label: 'total_archived', trend: 'up' }}
            className="card-premium border-primary/40"
          />
          <StatCard
            title="MITRE Techniques"
            value={stats?.total_techniques.toString() || "0"}
            icon={<Clock className="w-5 h-5" />}
            change={{ value: 2, label: 'new_detected', trend: 'up' }}
            className="card-premium border-primary/20"
          />
          <StatCard
            title="LLM Confidence"
            value="94.2%"
            icon={<TrendingUp className="w-5 h-5" />}
            change={{ value: 2.3, label: 'sync_rate', trend: 'up' }}
            className="card-premium border-primary/20"
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Cases Over Time */}
          <Card className="lg:col-span-2 card-premium border-primary/20">
            <CardHeader className="bg-primary/5 border-b border-primary/10">
              <CardTitle className="text-xs font-black uppercase tracking-widest text-primary flex items-center gap-2">
                 <BarChart3 className="w-4 h-4" />
                 Temporal Analysis (Category Distribution)
              </CardTitle>
              <CardDescription className="text-[10px] font-mono uppercase">Event distribution across categories</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={chartData.length > 0 ? chartData : [{date: 'N/A', cases: 0}]}>
                  <defs>
                    <linearGradient id="colorCases" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="oklch(0.78 0.22 150)" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="oklch(0.78 0.22 150)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.32 0.05 155)" vertical={false} />
                  <XAxis 
                    dataKey="date" 
                    stroke="oklch(0.65 0.08 160)" 
                    fontSize={10} 
                    tickLine={false} 
                    axisLine={false}
                    className="font-mono uppercase"
                  />
                  <YAxis 
                    stroke="oklch(0.65 0.08 160)" 
                    fontSize={10} 
                    tickLine={false} 
                    axisLine={false}
                    className="font-mono"
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'oklch(0.12 0.015 160)', border: '1px solid oklch(0.78 0.22 150)', borderRadius: '8px' }}
                    itemStyle={{ color: 'oklch(0.78 0.22 150)', fontFamily: 'monospace', fontSize: '12px' }}
                    labelStyle={{ color: 'oklch(0.98 0.01 160)', marginBottom: '4px', fontWeight: 'bold' }}
                  />
                  <Area type="monotone" dataKey="cases" stroke="oklch(0.78 0.22 150)" strokeWidth={3} fillOpacity={1} fill="url(#colorCases)" />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Detection Rate */}
          <Card className="card-premium border-primary/20">
            <CardHeader className="bg-primary/5 border-b border-primary/10">
              <CardTitle className="text-xs font-black uppercase tracking-widest text-primary">Severity Distribution</CardTitle>
              <CardDescription className="text-[10px] font-mono uppercase">Detected threat levels</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-4">
                {stats ? Object.entries(stats.severity_distribution).map(([level, count]) => {
                  const percentage = (count / stats.total_events) * 100;
                  const colorClass = level === 'critical' ? 'bg-red-500' : level === 'high' ? 'bg-orange-500' : 'bg-primary';
                  return (
                    <div key={level} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-mono uppercase text-primary/80">{level}</span>
                        <span className="text-xs font-bold text-primary">{count}</span>
                      </div>
                      <div className="w-full bg-primary/10 rounded-full h-1.5">
                        <div className={`${colorClass} h-1.5 rounded-full`} style={{width: `${percentage}%`}}></div>
                      </div>
                    </div>
                  )
                }) : (
                  <div className="text-center py-8 text-primary/40 font-mono text-[10px] animate-pulse">
                    LOADING_SEVERITY_METRICS...
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Evidence */}
        <Card className="card-premium border-primary/20">
          <CardHeader className="bg-primary/5 border-b border-primary/10">
            <CardTitle className="text-xs font-black uppercase tracking-widest text-primary">Live Evidence Ingestion</CardTitle>
            <CardDescription className="text-[10px] font-mono uppercase">Recent forensic artifacts analyzed by traceguard ai</CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {loading ? (
                Array(4).fill(0).map((_, i) => (
                  <div key={i} className="h-32 rounded-lg bg-primary/5 animate-pulse border border-primary/10" />
                ))
              ) : evidence.length > 0 ? (
                evidence.map((item) => (
                  <EvidenceCard key={item.id} {...item} />
                ))
              ) : (
                <div className="col-span-full py-12 text-center text-primary/40 font-mono text-sm">
                   NO_ACTIVE_INGESTIONS_FOUND
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Risk Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-orange-500/30 bg-orange-500/5 backdrop-blur-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-black uppercase tracking-widest text-orange-500 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                Detections Found
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-black text-orange-500/80">{stats?.total_events || 0}</div>
              <p className="text-[10px] font-mono text-orange-500/60 mt-1 uppercase">Items requiring verification</p>
            </CardContent>
          </Card>
          <Card className="border-red-500/30 bg-red-500/5 backdrop-blur-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-black uppercase tracking-widest text-red-500 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                Critical Hazards
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-black text-red-500/80">{stats?.severity_distribution.critical || 0}</div>
              <p className="text-[10px] font-mono text-red-500/60 mt-1 uppercase">Immediate mitigation required</p>
            </CardContent>
          </Card>
          <Card className="border-emerald-500/30 bg-emerald-500/5 backdrop-blur-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-black uppercase tracking-widest text-emerald-500 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                Integrity Checks
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-black text-emerald-500/80">{stats?.total_files || 0}</div>
              <p className="text-[10px] font-mono text-emerald-500/60 mt-1 uppercase">Processed evidence streams</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  )
}

