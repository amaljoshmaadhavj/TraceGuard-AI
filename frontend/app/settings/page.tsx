'use client'

import { useState } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { PageHeader } from '@/components/common/page-header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Settings, Bell, Lock, Palette, Database, Shield, User, Smartphone, Cloud } from 'lucide-react'

export default function SettingsPage() {
  const [notifications, setNotifications] = useState({
    analysisComplete: true,
    detectionsFound: true,
    systemUpdates: false,
    weeklyReport: true,
  })

  const [theme, setTheme] = useState('dark')
  const [confidenceThreshold, setConfidenceThreshold] = useState('85')
  const [analysisType, setAnalysisType] = useState('comprehensive')

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto px-4 lg:px-8 py-8 space-y-8">
        <PageHeader
          title="Settings & Configuration"
          description="Manage your account preferences, security protocols, and forensic engine parameters"
          icon={<Settings className="w-8 h-8 text-primary" />}
        />

        <Tabs defaultValue="general" className="space-y-8">
          <TabsList className="inline-flex h-12 items-center justify-start rounded-xl bg-secondary/30 p-1 text-muted-foreground w-full sm:w-auto">
            <TabsTrigger value="general" className="px-6 rounded-lg data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm transition-all text-xs font-bold uppercase tracking-widest gap-2">
              <User className="w-3.5 h-3.5" />
              Profile
            </TabsTrigger>
            <TabsTrigger value="notifications" className="px-6 rounded-lg data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm transition-all text-xs font-bold uppercase tracking-widest gap-2">
              <Bell className="w-3.5 h-3.5" />
              Alerts
            </TabsTrigger>
            <TabsTrigger value="analysis" className="px-6 rounded-lg data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm transition-all text-xs font-bold uppercase tracking-widest gap-2">
              <Database className="w-3.5 h-3.5" />
              Engine
            </TabsTrigger>
            <TabsTrigger value="privacy" className="px-6 rounded-lg data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm transition-all text-xs font-bold uppercase tracking-widest gap-2">
              <Lock className="w-3.5 h-3.5" />
              Security
            </TabsTrigger>
          </TabsList>

          {/* Profile Settings */}
          <TabsContent value="general" className="space-y-6 focus-visible:outline-none">
            <Card className="card-professional overflow-hidden">
              <CardHeader className="bg-secondary/30 border-b border-border/50">
                <CardTitle className="text-sm font-bold tracking-tight">Profile Information</CardTitle>
                <CardDescription className="text-xs">Update your investigator credentials</CardDescription>
              </CardHeader>
              <CardContent className="p-8 space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-3">
                    <Label htmlFor="username" className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Investigator ID</Label>
                    <Input id="username" placeholder="amaljosh" className="h-11 rounded-xl" />
                  </div>
                  <div className="space-y-3">
                    <Label htmlFor="email" className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Official Email</Label>
                    <Input id="email" type="email" placeholder="investigator@traceguard.ai" className="h-11 rounded-xl" />
                  </div>
                  <div className="space-y-3 md:col-span-2">
                    <Label htmlFor="organization" className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Bureau / Organization</Label>
                    <Input id="organization" placeholder="Cyber Forensics Division" className="h-11 rounded-xl" />
                  </div>
                </div>
                <div className="pt-4 border-t border-border/50">
                  <Button className="font-bold px-8 h-11 shadow-lg shadow-primary/10">Save Profile</Button>
                </div>
              </CardContent>
            </Card>

            <Card className="card-professional overflow-hidden">
              <CardHeader className="bg-secondary/30 border-b border-border/50">
                <CardTitle className="text-sm font-bold tracking-tight">System Appearance</CardTitle>
                <CardDescription className="text-xs">Customize the visual interface of the lab</CardDescription>
              </CardHeader>
              <CardContent className="p-8">
                <div className="max-w-md space-y-6">
                  <div className="space-y-3">
                    <Label htmlFor="theme" className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Interface Mode</Label>
                    <Select value={theme} onValueChange={setTheme}>
                      <SelectTrigger id="theme" className="h-11 rounded-xl">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="light">Light Professional</SelectItem>
                        <SelectItem value="dark">Dark Institutional</SelectItem>
                        <SelectItem value="auto">System Adaptive</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button variant="outline" className="font-bold px-6 h-11 border-border/50">Update Preference</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Alerts */}
          <TabsContent value="notifications" className="space-y-6 focus-visible:outline-none">
            <Card className="card-professional overflow-hidden">
              <CardHeader className="bg-secondary/30 border-b border-border/50">
                <CardTitle className="text-sm font-bold tracking-tight">Intelligence Alerts</CardTitle>
                <CardDescription className="text-xs">Configure how you receive critical forensic updates</CardDescription>
              </CardHeader>
              <CardContent className="p-8 space-y-8">
                {[
                  { id: 'analysisComplete', title: 'Analysis Finalized', desc: 'Alert when evidence stream analysis is complete' },
                  { id: 'detectionsFound', title: 'Threat Detected', desc: 'Immediate notification upon pattern match or anomaly detection' },
                  { id: 'systemUpdates', title: 'Bureau Updates', desc: 'Internal system and engine updates' },
                  { id: 'weeklyReport', title: 'Operational Briefing', desc: 'Weekly summary of all investigations and findings' },
                ].map((item) => (
                  <div key={item.id} className="flex items-center justify-between group">
                    <div className="space-y-1">
                      <h3 className="text-sm font-bold leading-none group-hover:text-primary transition-colors">{item.title}</h3>
                      <p className="text-xs text-muted-foreground font-medium">{item.desc}</p>
                    </div>
                    <Switch
                      checked={(notifications as any)[item.id]}
                      onCheckedChange={(checked) =>
                        setNotifications({ ...notifications, [item.id]: checked })
                      }
                      className="data-[state=checked]:bg-primary"
                    />
                  </div>
                ))}
                <div className="pt-4 border-t border-border/50">
                  <Button className="font-bold px-8 h-11 shadow-lg shadow-primary/10">Update Alert Protocols</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Engine Settings */}
          <TabsContent value="analysis" className="space-y-6 focus-visible:outline-none">
            <Card className="card-professional overflow-hidden">
              <CardHeader className="bg-secondary/30 border-b border-border/50">
                <CardTitle className="text-sm font-bold tracking-tight">Forensic Engine Configuration</CardTitle>
                <CardDescription className="text-xs">Fine-tune the AI analysis parameters and thresholds</CardDescription>
              </CardHeader>
              <CardContent className="p-8 space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-3">
                    <Label htmlFor="threshold" className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Confidence Threshold (%)</Label>
                    <Input
                      id="threshold"
                      type="number"
                      min="0"
                      max="100"
                      value={confidenceThreshold}
                      onChange={(e) => setConfidenceThreshold(e.target.value)}
                      className="h-11 rounded-xl"
                    />
                    <p className="text-[10px] text-muted-foreground font-medium italic">
                      Results below this value will require manual verification.
                    </p>
                  </div>
                  <div className="space-y-3">
                    <Label htmlFor="analysis-type" className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Analysis Priority</Label>
                    <Select value={analysisType} onValueChange={setAnalysisType}>
                      <SelectTrigger id="analysis-type" className="h-11 rounded-xl">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="comprehensive">Comprehensive (Standard)</SelectItem>
                        <SelectItem value="fast">High-Velocity (Reduced Depth)</SelectItem>
                        <SelectItem value="detailed">Deep Forensic (Maximum Depth)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-6 pt-6 border-t border-border/50">
                  <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Advanced Protocols</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    {[
                      { label: 'Neural Log Correlation', checked: true },
                      { label: 'Adversarial Pattern Matching', checked: true },
                      { label: 'Experimental Heuristics', checked: false },
                      { label: 'Deep Packet Inspection', checked: true },
                    ].map((feature, i) => (
                      <label key={i} className="flex items-center gap-3 cursor-pointer group">
                        <div className="relative flex items-center">
                          <input type="checkbox" defaultChecked={feature.checked} className="peer h-5 w-5 cursor-pointer appearance-none rounded-md border border-border bg-background transition-all checked:bg-primary checked:border-primary" />
                          <svg className="absolute w-3.5 h-3.5 text-primary-foreground opacity-0 peer-checked:opacity-100 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                        </div>
                        <span className="text-xs font-bold text-muted-foreground group-hover:text-foreground transition-colors uppercase tracking-wider">{feature.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                <div className="pt-4">
                  <Button className="font-bold px-8 h-11 shadow-lg shadow-primary/10">Initialize Engine Parameters</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security */}
          <TabsContent value="privacy" className="space-y-6 focus-visible:outline-none">
            <Card className="card-professional overflow-hidden">
              <CardHeader className="bg-secondary/30 border-b border-border/50">
                <CardTitle className="text-sm font-bold tracking-tight">Authentication & Security</CardTitle>
                <CardDescription className="text-xs">Secure your investigator access and data</CardDescription>
              </CardHeader>
              <CardContent className="p-8 space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-6 rounded-2xl bg-secondary/20 border border-border/50 space-y-4">
                    <div className="flex items-center gap-3 mb-2">
                      <Lock className="w-4 h-4 text-primary" />
                      <h3 className="text-xs font-bold uppercase tracking-widest">Passcode Protocol</h3>
                    </div>
                    <p className="text-xs text-muted-foreground font-medium">Last updated: 45 days ago. Recommended update in 15 days.</p>
                    <Button variant="outline" className="w-full font-bold h-10 border-border/50 text-xs uppercase tracking-widest">Reset Passcode</Button>
                  </div>
                  <div className="p-6 rounded-2xl bg-secondary/20 border border-border/50 space-y-4">
                    <div className="flex items-center gap-3 mb-2">
                      <Shield className="w-4 h-4 text-primary" />
                      <h3 className="text-xs font-bold uppercase tracking-widest">Multi-Factor Sync</h3>
                    </div>
                    <p className="text-xs text-muted-foreground font-medium">Add hardware or biometric security layers to your terminal.</p>
                    <Button variant="outline" className="w-full font-bold h-10 border-border/50 text-xs uppercase tracking-widest">Configure MFA</Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="card-professional border-rose-200/50 dark:border-rose-900/30 overflow-hidden">
              <CardHeader className="bg-rose-50/50 dark:bg-rose-950/10 border-b border-rose-100 dark:border-rose-900/20">
                <CardTitle className="text-xs font-black uppercase tracking-widest text-rose-600 dark:text-rose-400">Restricted Protocols</CardTitle>
                <CardDescription className="text-[10px] font-bold text-rose-500/70">High-risk administrative actions</CardDescription>
              </CardHeader>
              <CardContent className="p-8 space-y-4">
                <div className="flex flex-col sm:flex-row gap-4">
                  <Button variant="outline" className="flex-1 font-bold h-11 border-rose-200 text-rose-600 hover:bg-rose-50 hover:text-rose-700 dark:border-rose-900/30 dark:text-rose-400 dark:hover:bg-rose-950/20 text-[10px] uppercase tracking-widest">
                    Purge All Evidence Data
                  </Button>
                  <Button variant="outline" className="flex-1 font-bold h-11 border-rose-200 text-rose-600 hover:bg-rose-50 hover:text-rose-700 dark:border-rose-900/30 dark:text-rose-400 dark:hover:bg-rose-950/20 text-[10px] uppercase tracking-widest">
                    Decommission Investigator ID
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  )
}
