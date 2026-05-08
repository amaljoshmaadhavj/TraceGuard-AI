import Link from 'next/link'
import { AppLayout } from '@/components/layout/app-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ShieldAlert, Zap, BarChart3, Lock, CheckCircle2, Search } from 'lucide-react'

const features = [
  {
    icon: Search,
    title: 'Advanced AI Detection',
    description: 'Pinpoint AI-generated content and manipulations with research-grade forensic algorithms.',
  },
  {
    icon: Zap,
    title: 'High-Speed Analysis',
    description: 'Rapid forensic processing of digital evidence, minimizing investigation lead times.',
  },
  {
    icon: BarChart3,
    title: 'Comprehensive Reporting',
    description: 'Generate detailed, court-ready forensic reports with full chain-of-custody documentation.',
  },
  {
    icon: Lock,
    title: 'Enterprise Security',
    description: 'Bank-grade security protocols ensuring your investigation data remains confidential and secure.',
  },
]

export default function Home() {
  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-24">
        {/* Hero Section */}
        <section className="text-center space-y-8 mb-24">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-secondary text-secondary-foreground border border-border">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            <span className="text-xs font-medium tracking-wide uppercase">
              Next-Generation Digital Forensics
            </span>
          </div>
          
          <h1 className="text-5xl lg:text-7xl font-bold tracking-tight text-gradient max-w-4xl mx-auto leading-[1.1]">
            Trust through clarity. <br />
            Digital Forensics for the AI Age.
          </h1>
          
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            TraceGuard AI provides industry-leading forensic tools to detect, analyze, and verify digital content. Built for law enforcement, legal professionals, and security experts.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
            <Link href="/upload">
              <Button size="lg" className="h-14 px-8 text-base font-semibold shadow-lg shadow-primary/10 transition-transform active:scale-95">
                Start New Investigation
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button size="lg" variant="outline" className="h-14 px-8 text-base font-semibold border-border bg-background/50 backdrop-blur hover:bg-secondary">
                Explore Dashboard
              </Button>
            </Link>
          </div>
        </section>

        {/* Stats Section */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-32">
          {[
            { label: 'Cases Analyzed', value: '15,234' },
            { label: 'Detection Accuracy', value: '99.8%' },
            { label: 'Average Response', value: '< 2.0s' },
          ].map((stat, i) => (
            <div key={i} className="p-8 rounded-2xl border border-border bg-card/50 backdrop-blur-sm text-center">
              <div className="text-4xl font-bold tracking-tight mb-2">{stat.value}</div>
              <div className="text-sm font-medium text-muted-foreground uppercase tracking-widest">{stat.label}</div>
            </div>
          ))}
        </section>

        {/* Features Section */}
        <section className="space-y-16 mb-32">
          <div className="text-center space-y-4">
            <h2 className="text-3xl font-bold tracking-tight">System Capabilities</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Professional-grade forensic modules designed for high-stakes digital investigations.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <Card key={index} className="card-professional group">
                  <CardHeader>
                    <div className="w-12 h-12 rounded-xl bg-secondary flex items-center justify-center mb-4 group-hover:bg-primary group-hover:text-primary-foreground transition-colors duration-300">
                      <Icon className="w-6 h-6" />
                    </div>
                    <CardTitle className="text-xl font-bold tracking-tight">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground leading-relaxed">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </section>

        {/* CTA Section */}
        <section>
          <div className="relative rounded-3xl overflow-hidden bg-primary text-primary-foreground p-12 lg:p-20 text-center">
            <div className="absolute top-0 right-0 -mt-20 -mr-20 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-0 -mb-20 -ml-20 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
            
            <div className="relative z-10 space-y-8">
              <h2 className="text-3xl lg:text-5xl font-bold tracking-tight">Ready to begin your investigation?</h2>
              <p className="text-primary-foreground/80 max-w-2xl mx-auto text-lg leading-relaxed">
                Securely upload your evidence artifacts and let our forensic engine provide the clarity you need.
              </p>
              <Link href="/upload">
                <Button size="lg" variant="secondary" className="h-16 px-12 text-lg font-bold shadow-xl hover:bg-white hover:text-black transition-all">
                  Get Started Now
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </div>
    </AppLayout>
  )
}
