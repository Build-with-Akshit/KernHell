import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'KernHell | Autonomous Self-Healing Testing Engine',
  description:
    'The Heart of Your System Where Innovation Meets Precision. Autonomous self-healing testing engine for Playwright test suites.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-gray-100 min-h-screen flex flex-col font-sans selection:bg-brand-red selection:text-white">
        {/* Ambient background glow effects */}
        <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
          <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-gradient-to-b from-brand-red/10 via-brand-purple/5 to-transparent blur-[120px]" />
          <div className="absolute top-1/3 -left-40 w-[400px] h-[400px] bg-brand-cyan/5 blur-[120px] rounded-full" />
        </div>

        {/* Navigation */}
        <Navbar />

        {/* Content body */}
        <main className="flex-1 relative z-10 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        {/* Footer */}
        <footer className="relative z-10 border-t border-surface-border/70 py-6 text-center text-xs text-gray-500 font-mono">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <span>
              KernHell Engine © 2026 • Autonomous Self-Healing Infrastructure
            </span>
            <span className="text-gray-400">
              The Heart of Your System Where Innovation Meets Precision
            </span>
          </div>
        </footer>
      </body>
    </html>
  );
}
