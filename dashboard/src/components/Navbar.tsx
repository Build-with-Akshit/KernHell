'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Flame, Play, Database, History, LayoutDashboard, Terminal, ShieldCheck } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Overview', href: '/', icon: LayoutDashboard },
    { name: 'Live Playground', href: '/playground', icon: Play, badge: 'AI Live' },
    { name: 'Semantic Memory', href: '/cache', icon: Database },
    { name: 'Run History', href: '/history', icon: History },
  ];

  return (
    <header className="sticky top-0 z-50 w-full glass-panel border-b border-surface-border/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-red to-brand-crimson p-0.5 shadow-glow-red group-hover:scale-105 transition-transform duration-200">
              <div className="w-full h-full bg-surface rounded-[10px] flex items-center justify-center">
                <Flame className="w-5 h-5 text-brand-red group-hover:animate-pulse" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-wider text-white group-hover:text-brand-red transition-colors font-mono">
                  KERN<span className="text-brand-red">HELL</span>
                </span>
                <span className="px-1.5 py-0.5 text-[10px] uppercase font-mono font-semibold tracking-wider bg-surface-border text-brand-cyan rounded border border-brand-cyan/20">
                  v0.1.0
                </span>
              </div>
              <p className="text-[11px] text-gray-400 font-sans hidden sm:block">
                The Heart of Your System Where Innovation Meets Precision
              </p>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-surface-light text-white border border-brand-red/40 shadow-sm'
                      : 'text-gray-400 hover:text-white hover:bg-surface/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-brand-red' : 'text-gray-400'}`} />
                  <span>{item.name}</span>
                  {item.badge && (
                    <span className="text-[10px] px-1.5 py-0.2 rounded font-mono font-semibold bg-brand-red/20 text-brand-red border border-brand-red/30">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Right Status Indicator & Actions */}
          <div className="flex items-center space-x-4">
            <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-surface-light/80 border border-surface-border text-xs">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-emerald opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-emerald"></span>
              </span>
              <span className="font-mono text-gray-300 font-medium">ENGINE ONLINE</span>
              <span className="text-[10px] text-brand-cyan font-mono pl-1 border-l border-surface-border">
                12ms latency
              </span>
            </div>

            <a
              href="https://github.com/riteshkumar072/KernHell"
              target="_blank"
              rel="noreferrer"
              className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-mono rounded-lg bg-surface hover:bg-surface-light border border-surface-border hover:border-gray-600 text-gray-300 hover:text-white transition-colors"
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
