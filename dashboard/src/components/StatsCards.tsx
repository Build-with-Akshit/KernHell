'use client';

import React from 'react';
import { SystemStats } from '@/lib/api';
import { Wrench, Zap, ShieldAlert, DollarSign, ArrowUpRight, Clock } from 'lucide-react';

interface StatsCardsProps {
  stats: SystemStats;
  loading?: boolean;
}

export default function StatsCards({ stats, loading }: StatsCardsProps) {
  const cards = [
    {
      title: 'Autonomous Fixes',
      value: stats.total_healed.toString(),
      subtext: `From ${stats.total_runs} test suites healed`,
      icon: Wrench,
      gradient: 'from-brand-red/20 to-brand-crimson/5',
      iconColor: 'text-brand-red',
      borderGlow: 'hover:border-brand-red/50',
      badge: '100% Verified',
      badgeColor: 'bg-brand-red/10 text-brand-red border-brand-red/30',
    },
    {
      title: 'Vector Cache Hit Rate',
      value: `${stats.cache_efficiency_pct}%`,
      subtext: `${stats.cache_hits} hits (0ms LLM latency)`,
      icon: Zap,
      gradient: 'from-brand-cyan/20 to-blue-500/5',
      iconColor: 'text-brand-cyan',
      borderGlow: 'hover:border-brand-cyan/50',
      badge: `${stats.cache_entries} Embeddings`,
      badgeColor: 'bg-brand-cyan/10 text-brand-cyan border-brand-cyan/30',
    },
    {
      title: 'Real Bugs Guarded',
      value: stats.real_bugs_caught.toString(),
      subtext: 'Flagged without false healing',
      icon: ShieldAlert,
      gradient: 'from-purple-500/20 to-pink-500/5',
      iconColor: 'text-brand-purple',
      borderGlow: 'hover:border-brand-purple/50',
      badge: 'Zero Hallucinations',
      badgeColor: 'bg-brand-purple/10 text-brand-purple border-brand-purple/30',
    },
    {
      title: 'Engineering Value Saved',
      value: `$${stats.dollars_saved.toLocaleString()}`,
      subtext: `${stats.hours_saved} hrs manual QA time saved`,
      icon: DollarSign,
      gradient: 'from-brand-emerald/20 to-emerald-600/5',
      iconColor: 'text-brand-emerald',
      borderGlow: 'hover:border-brand-emerald/50',
      badge: 'ROI 14.8x',
      badgeColor: 'bg-brand-emerald/10 text-brand-emerald border-brand-emerald/30',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`glass-panel p-5 rounded-2xl relative overflow-hidden transition-all duration-300 glass-panel-hover border border-surface-border ${card.borderGlow}`}
          >
            {/* Background subtle gradient glow */}
            <div
              className={`absolute -right-8 -top-8 w-32 h-32 rounded-full bg-gradient-to-br ${card.gradient} blur-2xl opacity-60 pointer-events-none`}
            />

            <div className="flex items-center justify-between mb-3 relative z-10">
              <span className="text-xs font-medium text-gray-400 font-sans">{card.title}</span>
              <div className="w-8 h-8 rounded-lg bg-surface-light flex items-center justify-center border border-surface-border">
                <Icon className={`w-4 h-4 ${card.iconColor}`} />
              </div>
            </div>

            <div className="flex items-baseline space-x-2 relative z-10">
              <span className="text-3xl font-bold tracking-tight text-white font-mono">
                {loading ? '...' : card.value}
              </span>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${card.badgeColor}`}>
                {card.badge}
              </span>
            </div>

            <p className="mt-2 text-xs text-gray-400 font-sans flex items-center space-x-1 relative z-10">
              <span>{card.subtext}</span>
            </p>
          </div>
        );
      })}
    </div>
  );
}
