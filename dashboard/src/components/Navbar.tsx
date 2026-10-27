'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Flame, Play, Database, History, LayoutDashboard, Terminal } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Overview', href: '/', icon: LayoutDashboard },
    { name: 'Live Playground', href: '/playground', icon: Play, badge: 'AI Live' },
    { name: 'Semantic Memory', href: '/cache', icon: Database },
    { name: 'Run History', href: '/history', icon: History },
  ];

  return (
    <header className="sticky top-0 z-50 w-full bg-[#090A0F]/95 backdrop-blur-xl border-b border-white/[0.08] shadow-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Version */}
          <Link href="/" className="flex items-center space-x-3 group shrink-0">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-red via-brand-crimson to-brand-red p-0.5 shadow-glow-red group-hover:scale-105 transition-transform duration-200">
              <div className="w-full h-full bg-[#0B0D14] rounded-[10px] flex items-center justify-center">
                <Flame className="w-5 h-5 text-brand-red group-hover:animate-pulse" />
              </div>
            </div>
            <div className="flex flex-col">
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-wider text-white group-hover:text-brand-red transition-colors font-mono">
                  KERN<span className="text-brand-red">HELL</span>
                </span>
                <span className="px-1.5 py-0.5 text-[10px] uppercase font-mono font-semibold tracking-wider bg-surface-border/90 text-brand-cyan rounded border border-brand-cyan/30 shadow-sm">
                  v0.1.7
                </span>
              </div>
              <p className="text-[11px] text-gray-400 font-sans hidden xl:block leading-none mt-0.5">
                The Heart of Your System Where Innovation Meets Precision
              </p>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1.5 bg-[#0B0D14]/80 p-1 rounded-xl border border-white/[0.06]">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-mono font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-white/[0.09] text-white border border-brand-red/40 shadow-sm font-semibold'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-white/[0.04]'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-brand-red' : 'text-gray-400'}`} />
                  <span>{item.name}</span>
                  {item.badge && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded font-mono font-bold bg-brand-red/20 text-brand-red border border-brand-red/30 tracking-wider">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Right Status Indicator & Actions */}
          <div className="flex items-center space-x-3 shrink-0">
            <div className="hidden sm:flex items-center space-x-2.5 px-3 py-1.5 rounded-full bg-[#0B0D14] border border-white/[0.08] shadow-inner">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-emerald opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-emerald"></span>
              </span>
              <span className="font-mono text-xs text-gray-200 font-medium">ENGINE ONLINE</span>
              <span className="w-px h-3 bg-white/10" />
              <span className="text-[11px] text-brand-cyan font-mono font-semibold">
                12ms
              </span>
            </div>

            <a
              href="https://github.com/riteshkumar072/KernHell"
              target="_blank"
              rel="noreferrer"
              className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-mono rounded-lg bg-[#0B0D14] hover:bg-surface-light border border-white/[0.08] hover:border-gray-500 text-gray-300 hover:text-white transition-all shadow-sm"
            >
              <Terminal className="w-3.5 h-3.5 text-brand-cyan" />
              <span>CLI Docs</span>
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}
