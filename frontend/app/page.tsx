import Link from 'next/link'
import { AppLayout } from '@/components/layout/app-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ShieldAlert, Zap, TrendingUp, Lock } from 'lucide-react'

const features = [
  {
    icon: ShieldAlert,
    title: 'AI Detection',
    description: 'Advanced algorithms detect AI-generated content and manipulations with high accuracy.',
  },
  {
    icon: Zap,
    title: 'Real-Time Analysis',
    description: 'Lightning-fast forensic analysis of digital evidence and suspicious files.',
  },
  {
    icon: TrendingUp,
    title: 'Detailed Reports',
    description: 'Comprehensive forensic reports with actionable insights and evidence trails.',
  },
  {
    icon: Lock,
    title: 'Secure & Compliant',
    description: 'Enterprise-grade security with full audit trails and compliance support.',
  },
]

export default function Home() {
  return (
    <AppLayout>
      <div className="px-4 lg:px-8 py-8">
        {/* Hero Section */}
        <section className="mb-16">
          <div className="text-center space-y-6 mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20">
              <div className="w-2 h-2 rounded-full bg-primary" />
              <span className="text-sm font-medium text-primary">
                Advanced Forensics Platform
              </span>
            </div>
            <h1 className="text-5xl lg:text-6xl font-bold tracking-tight text-balance">
              Digital Forensics Meets
              <span className="text-primary"> AI Intelligence</span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto text-balance">
              TraceGuard AI delivers cutting-edge forensic investigation tools powered by artificial intelligence. Detect AI-generated content, analyze digital evidence, and build unshakeable cases.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              <Link href="/upload">
                <Button size="lg" className="bg-primary hover:bg-primary/90">
                  Start Investigation
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button size="lg" variant="outline">
                  View Dashboard
                </Button>
              </Link>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-16">
            <Card className="bg-gradient-to-br from-primary/5 to-transparent border-primary/20">
              <CardContent className="p-6">
                <div className="text-3xl font-bold">15,234</div>
                <p className="text-sm text-muted-foreground mt-2">Cases Analyzed</p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-accent/5 to-transparent border-accent/20">
              <CardContent className="p-6">
                <div className="text-3xl font-bold">99.8%</div>
                <p className="text-sm text-muted-foreground mt-2">Detection Accuracy</p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-green-500/5 to-transparent border-green-500/20">
              <CardContent className="p-6">
                <div className="text-3xl font-bold">&lt;2s</div>
                <p className="text-sm text-muted-foreground mt-2">Average Analysis Time</p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Features Section */}
        <section className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Why TraceGuard AI?</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Industry-leading forensic tools designed for investigators, law enforcement, and security professionals.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <Card key={index} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="mb-4">
                      <Icon className="w-8 h-8 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16">
          <Card className="bg-gradient-to-r from-primary/20 via-transparent to-accent/20 border-primary/30">
            <CardContent className="p-12 text-center space-y-6">
              <h2 className="text-3xl font-bold">Ready to investigate?</h2>
              <p className="text-muted-foreground max-w-xl mx-auto">
                Upload your first piece of evidence and let TraceGuard AI analyze it instantly.
              </p>
              <Link href="/upload">
                <Button size="lg" className="bg-primary hover:bg-primary/90">
                  Upload Evidence
                </Button>
              </Link>
            </CardContent>
          </Card>
        </section>
      </div>
    </AppLayout>
  )
}
