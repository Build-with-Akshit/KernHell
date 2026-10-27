'use client';

import React, { useState } from 'react';
import { Copy, Check, FileCode, CheckCircle2, SplitSquareVertical } from 'lucide-react';

interface DiffViewerProps {
  diff?: string;
  title?: string;
  testFile?: string;
  oldSelector?: string;
  newSelector?: string;
}

export default function DiffViewer({
  diff,
  title = 'Surgical CST Code Patch',
  testFile,
  oldSelector,
  newSelector,
}: DiffViewerProps) {
  const [copied, setCopied] = useState(false);

  // If there's no diff and no selectors provided, show authentic clean empty state
  if (!diff && !oldSelector && !newSelector) {
    return (
      <div className="glass-panel rounded-2xl border border-surface-border p-8 text-center space-y-3 bg-[#0B0D14]/80">
        <div className="w-10 h-10 rounded-xl bg-surface-light border border-white/[0.08] flex items-center justify-center text-gray-500 mx-auto">
          <FileCode className="w-5 h-5" />
        </div>
        <div className="space-y-1">
          <p className="text-xs font-mono font-bold text-gray-300">No Active AST Patch</p>
          <p className="text-[11px] font-sans text-gray-500 max-w-sm mx-auto">
            Test selectors are intact. When KernHell repairs a broken locator during test execution, the surgical LibCST code diff will stream here.
          </p>
        </div>
      </div>
    );
  }

  const fileName = testFile ? testFile.split(/[/\\]/).pop() || 'test.py' : 'test.py';
  const effectiveDiff =
    diff ||
    `--- a/${fileName}
+++ b/${fileName}
@@ -1,3 +1,3 @@
-    page.click("${oldSelector || ''}")
+    page.click("${newSelector || ''}")`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(effectiveDiff);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lines = effectiveDiff.split('\n');

  return (
    <div className="glass-panel rounded-2xl border border-surface-border overflow-hidden">
      {/* Diff Header */}
      <div className="px-4 py-3 bg-surface-light/70 border-b border-surface-border flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <FileCode className="w-4 h-4 text-brand-red" />
          <span className="text-xs font-mono font-semibold text-gray-200">{title}</span>
          <span className="text-[11px] font-mono text-gray-500 hidden sm:inline">
            ({testFile})
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <span className="hidden sm:flex items-center space-x-1 text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-brand-emerald/10 text-brand-emerald border border-brand-emerald/20">
            <CheckCircle2 className="w-3 h-3" />
            <span>Comments & Formatting 100% Preserved</span>
          </span>

          <button
            onClick={copyToClipboard}
            className="flex items-center space-x-1 px-2.5 py-1 text-xs font-mono rounded bg-surface hover:bg-surface-border text-gray-300 hover:text-white transition-colors border border-surface-border"
            title="Copy diff to clipboard"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-brand-emerald" />
                <span className="text-brand-emerald">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Diff Code Body */}
      <div className="p-4 font-mono text-xs overflow-x-auto bg-[#07080c] leading-relaxed">
        {lines.map((line, idx) => {
          let lineClass = 'text-gray-400';
          let bgClass = '';

          if (line.startsWith('---') || line.startsWith('+++')) {
            lineClass = 'text-brand-cyan font-bold';
            bgClass = 'bg-brand-cyan/5';
          } else if (line.startsWith('@@')) {
            lineClass = 'text-brand-purple font-semibold';
            bgClass = 'bg-brand-purple/5';
          } else if (line.startsWith('-')) {
            lineClass = 'text-red-400 font-medium';
            bgClass = 'bg-red-950/40 border-l-2 border-red-500';
          } else if (line.startsWith('+')) {
            lineClass = 'text-emerald-400 font-medium';
            bgClass = 'bg-emerald-950/40 border-l-2 border-emerald-500';
          }

          return (
            <div
              key={idx}
              className={`px-3 py-0.5 whitespace-pre font-mono rounded-sm ${lineClass} ${bgClass}`}
            >
              <span className="inline-block w-8 text-right pr-4 select-none opacity-30 text-[10px]">
                {idx + 1}
              </span>
              <span>{line}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
