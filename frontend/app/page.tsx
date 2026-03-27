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
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/20 border border-primary/40 text-glow">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span className="text-sm font-bold tracking-widest uppercase text-primary">
                Advanced Forensics Platform
              </span>
            </div>
            <h1 className="text-5xl lg:text-7xl font-bold tracking-tighter text-balance uppercase">
              Digital Forensics Meets
              <span className="text-primary text-glow block lg:inline"> AI Intelligence</span>
            </h1>
            <p className="text-xl text-muted-foreground/80 max-w-2xl mx-auto text-balance font-mono leading-relaxed">
              [SYSTEM_MESSAGE]: TraceGuard AI delivers cutting-edge forensic investigation tools powered by artificial intelligence. Detect AI-generated content, analyze digital evidence, and build unshakeable cases.
            </p>
            <div className="flex flex-col sm:flex-row gap-6 justify-center pt-8">
              <Link href="/upload">
                <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/80 px-8 py-6 text-lg font-bold uppercase tracking-tighter shadow-[0_0_20px_rgba(0,255,65,0.4)]">
                  Start Investigation
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button size="lg" variant="outline" className="border-primary/50 text-primary hover:bg-primary/10 px-8 py-6 text-lg font-bold uppercase tracking-tighter">
                  View Dashboard
                </Button>
              </Link>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20">
            <Card className="card-premium border-primary/30">
              <CardContent className="p-8">
                <div className="text-4xl font-bold text-primary text-glow uppercase">15,234</div>
                <p className="text-xs font-bold text-muted-foreground mt-2 uppercase tracking-widest">Cases Analyzed</p>
              </CardContent>
            </Card>
            <Card className="card-premium border-accent/30">
              <CardContent className="p-8">
                <div className="text-4xl font-bold text-accent text-glow uppercase">99.8%</div>
                <p className="text-xs font-bold text-muted-foreground mt-2 uppercase tracking-widest">Detection Accuracy</p>
              </CardContent>
            </Card>
            <Card className="card-premium border-primary/30">
              <CardContent className="p-8">
                <div className="text-4xl font-bold text-primary text-glow uppercase">&lt;2s</div>
                <p className="text-xs font-bold text-muted-foreground mt-2 uppercase tracking-widest">Avg Analysis Time</p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Features Section */}
        <section className="mb-24 py-12">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 uppercase tracking-tighter">System Capabilities</h2>
            <div className="h-1 w-24 bg-primary mx-auto mb-6" />
            <p className="text-muted-foreground/70 max-w-xl mx-auto font-mono">
              [DEVICES_ONLINE]: Industry-leading forensic tools designed for deep-layer investigation and law enforcement.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <Card key={index} className="card-premium group">
                  <CardHeader className="pb-2">
                    <div className="mb-4">
                      <Icon className="w-10 h-10 text-primary group-hover:scale-110 transition-transform duration-300" />
                    </div>
                    <CardTitle className="text-xl font-bold uppercase tracking-tight">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground leading-relaxed font-mono">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20">
          <Card className="card-premium border-primary/50 relative overflow-hidden">
            <div className="absolute inset-0 bg-primary/5 pointer-events-none" />
            <CardContent className="p-16 text-center space-y-8 relative z-10">
              <h2 className="text-4xl font-bold uppercase tracking-tighter">Initialize Investigation?</h2>
              <p className="text-muted-foreground/80 max-w-2xl mx-auto font-mono text-lg">
                SECURE_PROTOCOL: Upload your first piece of evidence and let the system analyze it. TraceGuard AI is ready for active surveillance.
              </p>
              <Link href="/upload">
                <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/80 px-10 py-8 text-xl font-black uppercase tracking-widest shadow-[0_0_30px_rgba(0,255,65,0.6)]">
                  [ START_UPLOAD ]
                </Button>
              </Link>
            </CardContent>
          </Card>
        </section>
      </div>
    </AppLayout>
  )
}
