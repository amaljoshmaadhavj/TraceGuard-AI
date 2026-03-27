import { AppLayout } from '@/components/layout/app-layout'
import { PageHeader } from '@/components/common/page-header'
import { StatCard } from '@/components/common/stat-card'
import { EvidenceCard } from '@/components/common/evidence-card'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ShieldAlert, TrendingUp, AlertTriangle, CheckCircle2, Clock, BarChart3 } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts'

const mockCasesData = [
  { date: 'Mon', cases: 4 },
  { date: 'Tue', cases: 6 },
  { date: 'Wed', cases: 5 },
  { date: 'Thu', cases: 8 },
  { date: 'Fri', cases: 7 },
  { date: 'Sat', cases: 3 },
  { date: 'Sun', cases: 5 },
]

const mockRecentEvidences = [
  { id: 'EV001', title: 'Image-2024-01-15.jpg', type: 'image' as const, status: 'confirmed' as const, confidence: 92, uploadDate: '2024-01-15' },
  { id: 'EV002', title: 'Document_scan.pdf', type: 'file' as const, status: 'analyzing' as const, uploadDate: '2024-01-14' },
  { id: 'EV003', title: 'Screenshot_evidence.png', type: 'image' as const, status: 'suspected' as const, confidence: 78, uploadDate: '2024-01-14' },
  { id: 'EV004', title: 'Audio_recording.wav', type: 'file' as const, status: 'pending' as const, uploadDate: '2024-01-13' },
]

export default function DashboardPage() {
  return (
    <AppLayout>
      <div className="px-4 lg:px-8 py-8 space-y-8">
        <PageHeader
          title="Dashboard"
          description="Overview of your investigations and analysis results"
          icon={<ShieldAlert className="w-8 h-8" />}
        />

        {/* Key Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Node Hits"
            value="127"
            icon={<ShieldAlert className="w-5 h-5" />}
            change={{ value: 12, label: 'buffer_growth', trend: 'up' }}
            className="card-premium border-primary/20"
          />
          <StatCard
            title="Extraction Success"
            value="34"
            icon={<CheckCircle2 className="w-5 h-5 text-glow" />}
            change={{ value: 8, label: 'this_cycle', trend: 'up' }}
            className="card-premium border-primary/40"
          />
          <StatCard
            title="Pending Queues"
            value="12"
            icon={<Clock className="w-5 h-5" />}
            change={{ value: 3, label: 'in_transit', trend: 'up' }}
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
                 Temporal Analysis (7D)
              </CardTitle>
              <CardDescription className="text-[10px] font-mono uppercase">Daily extraction activity logs</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={mockCasesData}>
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
          <Card>
            <CardHeader>
              <CardTitle>Detection Rate</CardTitle>
              <CardDescription>By analysis type</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Images</span>
                    <span className="text-sm font-bold">96%</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div className="bg-primary h-2 rounded-full" style={{width: '96%'}}></div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Videos</span>
                    <span className="text-sm font-bold">91%</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div className="bg-accent h-2 rounded-full" style={{width: '91%'}}></div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Text</span>
                    <span className="text-sm font-bold">89%</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{width: '89%'}}></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Evidence */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Evidence Items</CardTitle>
            <CardDescription>Latest uploaded items for analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {mockRecentEvidences.map((evidence) => (
                <EvidenceCard key={evidence.id} {...evidence} />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Risk Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-orange-500/30 bg-orange-500/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-orange-500" />
                Suspicious Items
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">18</div>
              <p className="text-sm text-muted-foreground mt-2">Require further investigation</p>
            </CardContent>
          </Card>
          <Card className="border-red-500/30 bg-red-500/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-red-500" />
                High Priority
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">5</div>
              <p className="text-sm text-muted-foreground mt-2">Immediate action needed</p>
            </CardContent>
          </Card>
          <Card className="border-green-500/30 bg-green-500/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                Verified Safe
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">104</div>
              <p className="text-sm text-muted-foreground mt-2">Passed all checks</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  )
}
