import { AppLayout } from '@/components/layout/app-layout'
import { PageHeader } from '@/components/common/page-header'
import { StatCard } from '@/components/common/stat-card'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, TrendingUp, Users, Zap } from 'lucide-react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
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

const analyticsData = [
  { month: 'Jan', cases: 45, detections: 12, falsePositives: 2 },
  { month: 'Feb', cases: 52, detections: 18, falsePositives: 1 },
  { month: 'Mar', cases: 48, detections: 15, falsePositives: 2 },
  { month: 'Apr', cases: 61, detections: 22, falsePositives: 3 },
  { month: 'May', cases: 55, detections: 19, falsePositives: 1 },
  { month: 'Jun', cases: 67, detections: 24, falsePositives: 2 },
]

const detectionTypeData = [
  { name: 'AI-Generated', value: 38, color: '#3B82F6' },
  { name: 'Manipulated', value: 32, color: '#F97316' },
  { name: 'Deepfake', value: 18, color: '#EC4899' },
  { name: 'Authentic', value: 12, color: '#22C55E' },
]

const accuracyByType = [
  { type: 'Images', accuracy: 96 },
  { type: 'Videos', accuracy: 91 },
  { type: 'Audio', accuracy: 88 },
  { type: 'Documents', accuracy: 94 },
  { type: 'Text', accuracy: 89 },
]

export default function StatisticsPage() {
  return (
    <AppLayout>
      <div className="px-4 lg:px-8 py-8 space-y-8">
        <PageHeader
          title="Statistics & Analytics"
          description="Comprehensive analysis of your forensic investigations and detection metrics"
          icon={<BarChart3 className="w-8 h-8" />}
        />

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Investigations"
            value="328"
            icon={<Zap className="w-5 h-5" />}
            change={{ value: 23, label: 'this month', trend: 'up' }}
          />
          <StatCard
            title="AI Detections"
            value="127"
            icon={<TrendingUp className="w-5 h-5" />}
            change={{ value: 8, label: 'this week', trend: 'up' }}
          />
          <StatCard
            title="Detection Rate"
            value="94.2%"
            icon={<Users className="w-5 h-5" />}
            change={{ value: 2.3, label: 'improvement', trend: 'up' }}
          />
          <StatCard
            title="False Positives"
            value="2.1%"
            icon={<BarChart3 className="w-5 h-5" />}
            change={{ value: 0.8, label: 'reduction', trend: 'down' }}
          />
        </div>

        {/* Trends */}
        <Card>
          <CardHeader>
            <CardTitle>Investigation Trends</CardTitle>
            <CardDescription>Monthly investigation and detection statistics</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={analyticsData}>
                <defs>
                  <linearGradient id="colorCases" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--color-primary)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="var(--color-primary)" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorDetections" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--color-accent)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="var(--color-accent)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="month" stroke="var(--color-muted-foreground)" />
                <YAxis stroke="var(--color-muted-foreground)" />
                <Tooltip
                  contentStyle={{ backgroundColor: 'var(--color-card)', border: '1px solid var(--color-border)' }}
                  labelStyle={{ color: 'var(--color-foreground)' }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="cases"
                  stroke="var(--color-primary)"
                  fillOpacity={1}
                  fill="url(#colorCases)"
                  name="Total Cases"
                />
                <Area
                  type="monotone"
                  dataKey="detections"
                  stroke="var(--color-accent)"
                  fillOpacity={1}
                  fill="url(#colorDetections)"
                  name="Detections"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Detection Types */}
          <Card>
            <CardHeader>
              <CardTitle>Detection Types Distribution</CardTitle>
              <CardDescription>Breakdown by detection category</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={detectionTypeData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {detectionTypeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Accuracy by Type */}
          <Card>
            <CardHeader>
              <CardTitle>Detection Accuracy by Type</CardTitle>
              <CardDescription>Average confidence score per file type</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={accuracyByType} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis type="number" stroke="var(--color-muted-foreground)" />
                  <YAxis dataKey="type" type="category" stroke="var(--color-muted-foreground)" width={100} />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'var(--color-card)', border: '1px solid var(--color-border)' }}
                    labelStyle={{ color: 'var(--color-foreground)' }}
                  />
                  <Bar dataKey="accuracy" fill="var(--color-primary)" radius={[0, 8, 8, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Analysis Speed */}
        <Card>
          <CardHeader>
            <CardTitle>Analysis Speed Metrics</CardTitle>
            <CardDescription>Average processing time per file type</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {[
                { label: 'Small Images', time: '2.1s' },
                { label: 'Large Images', time: '4.3s' },
                { label: 'Short Videos', time: '18.5s' },
                { label: 'Documents', time: '3.2s' },
                { label: 'Audio Files', time: '12.8s' },
              ].map((item, idx) => (
                <div key={idx} className="text-center p-4 rounded-lg bg-muted/50 border border-border">
                  <p className="text-sm text-muted-foreground">{item.label}</p>
                  <p className="text-lg font-bold mt-2">{item.time}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
