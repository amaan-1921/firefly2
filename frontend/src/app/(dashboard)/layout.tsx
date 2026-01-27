// src/app/(dashboard)/layout.tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LucideAlertTriangle, LucideBarChart3, LucideGlobe2, LucideSettings, LucideUsers, LucideHome, LucideSettings2 } from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from '@/components/ui/dropdown-menu';
import { Slider } from '@/components/ui/slider';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { signOut } from 'next-auth/react';
import { useAlertStore } from '@/store/useAlertStore';
import { ThemeToggle } from '@/components/common/ThemeToggle';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LucideHome },
  { href: '/monitoring', label: 'Alerts', icon: LucideAlertTriangle },
  { href: '/alerts', label: 'Monitoring Signals', icon: LucideGlobe2 },
  { href: '/impact', label: 'Impact', icon: LucideBarChart3 },
  { href: '/suppliers', label: 'Suppliers', icon: LucideUsers },
  { href: '/settings', label: 'Settings', icon: LucideSettings }
];

export default function DashboardLayout({
  children
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { monitoringConfig, setMonitoringConfig } = useAlertStore();

  return (
    <div className="h-screen flex bg-bg-white">
      {/* Fixed left sidebar */}
      <aside className="w-64 border-r border-slate-200 flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-slate-200">
          <Link href="/dashboard" className="text-lg font-semibold text-primary-red tracking-tight hover:text-brand-terracotta transition-colors">
            ADAPT
          </Link>
        </div>
        <nav className="flex-1 py-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-2 text-sm font-medium transition-colors ${
                  active
                    ? 'bg-primary-red/10 text-primary-red'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex flex-col">
        {/* Utility header */}
        <header className="h-16 border-b border-slate-200 flex items-center justify-between px-6 gap-4">
          <div className="flex-1 max-w-lg">
            <input
              type="search"
              placeholder="Search alerts, suppliers, POs..."
              className="w-full rounded-full border border-slate-200 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-red/40"
            />
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs uppercase tracking-wide text-slate-400">
              Safety Progression
            </span>
                        <ThemeToggle />
            <button
              type="button"
              className="flex items-center gap-2 rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-500"
            >
              <span className="inline-flex h-2 w-2 rounded-full bg-safe-green" />
              <span>System Ready</span>
            </button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm">
                  <LucideSettings2 className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-80">
                <DropdownMenuLabel>Monitoring Configuration</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <div className="p-2 space-y-4">
                  <div>
                    <label className="text-xs font-semibold text-slate-500 uppercase">Risk Category</label>
                    <ToggleGroup
                      type="single"
                      value={monitoringConfig.riskCategory}
                      onValueChange={(value) => value && setMonitoringConfig({ riskCategory: value })}
                      className="justify-start mt-1"
                    >
                      <ToggleGroupItem value="ALL" size="sm">All</ToggleGroupItem>
                      <ToggleGroupItem value="GEOPOLITICAL" size="sm">Geopolitical</ToggleGroupItem>
                      <ToggleGroupItem value="WEATHER" size="sm">Weather</ToggleGroupItem>
                      <ToggleGroupItem value="LOGISTICS" size="sm">Logistics</ToggleGroupItem>
                    </ToggleGroup>
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-500 uppercase">Impact Threshold</label>
                    <Slider
                      value={[monitoringConfig.impactThreshold]}
                      onValueChange={(value) => setMonitoringConfig({ impactThreshold: value[0] })}
                      max={1000000}
                      min={0}
                      step={50000}
                      className="mt-2"
                    />
                    <p className="text-xs text-slate-400 mt-1">
                      Showing alerts where estimated impact is &gt; ${monitoringConfig.impactThreshold.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-500 uppercase">Frequency</label>
                    <ToggleGroup
                      type="single"
                      value={monitoringConfig.frequency}
                      onValueChange={(value) => value && setMonitoringConfig({ frequency: value as 'REALTIME' | 'DAILY' })}
                      className="justify-start mt-1"
                    >
                      <ToggleGroupItem value="REALTIME" size="sm">Real-time</ToggleGroupItem>
                      <ToggleGroupItem value="DAILY" size="sm">Daily Digest</ToggleGroupItem>
                    </ToggleGroup>
                    <p className="text-[10px] text-slate-400 mt-1">
                      Real-time is recommended for high-stakes logistics.
                    </p>
                  </div>
                </div>
              </DropdownMenuContent>
            </DropdownMenu>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center gap-2">
                  <Avatar className="h-8 w-8 bg-primary-red">
                    <AvatarFallback>U</AvatarFallback>
                  </Avatar>
                  <span className="text-sm text-slate-700 hidden md:inline">
                    user1@company.com
                  </span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem asChild>
                  <Link href="/profile">Profile</Link>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => signOut()}>
                  Sign out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Routed content */}
        <main className="flex-1 overflow-y-auto bg-slate-50">
          {children}
        </main>
      </div>
    </div>
  );
}
