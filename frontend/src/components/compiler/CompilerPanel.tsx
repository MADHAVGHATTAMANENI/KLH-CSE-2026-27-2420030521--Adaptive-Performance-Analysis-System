import React, { useState } from 'react';
import { Play, Terminal, CheckCircle2, XCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { useEditorStore } from '../../stores/useEditorStore';
import { OptimizationLevel } from '../../types';

const OPT_LEVELS: OptimizationLevel[] = ['-O0', '-O1', '-O2', '-O3', '-Os'];
const COMMON_FLAGS = ['-Wall', '-Wextra', '-pedantic', '-ffast-math', '-funroll-loops'];

export const CompilerPanel: React.FC = () => {
  const {
    fileId,
    selectedOptLevel,
    auxiliaryFlags,
    compilation,
    isCompiling,
    setOptLevel,
    toggleFlag,
    compile,
  } = useEditorStore();

  const [showTerminal, setShowTerminal] = useState(true);

  if (!fileId) return null;

  return (
    <div className="border-b border-borderSubtle bg-surface p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">
          Clang Compiler Engine
        </span>
        <button
          onClick={() => compile()}
          disabled={isCompiling}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-mono font-medium transition disabled:opacity-50"
        >
          {isCompiling ? (
            <span className="animate-spin text-xs">...</span>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Compile</span>
            </>
          )}
        </button>
      </div>

      {/* Optimization Level Selector */}
      <div className="space-y-1.5">
        <label className="text-[11px] font-mono text-slate-400">Optimization Level</label>
        <div className="grid grid-cols-5 gap-1.5">
          {OPT_LEVELS.map((level) => (
            <button
              key={level}
              onClick={() => setOptLevel(level)}
              className={`py-1 rounded text-xs font-mono font-semibold transition ${
                selectedOptLevel === level
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50'
                  : 'bg-elevated text-slate-400 hover:text-slate-200 border border-borderSubtle'
              }`}
            >
              {level}
            </button>
          ))}
        </div>
      </div>

      {/* Auxiliary Flags Whitelist */}
      <div className="space-y-1.5">
        <label className="text-[11px] font-mono text-slate-400">Compiler Flags (Whitelisted)</label>
        <div className="flex flex-wrap gap-1.5">
          {COMMON_FLAGS.map((flag) => {
            const active = auxiliaryFlags.includes(flag);
            return (
              <button
                key={flag}
                onClick={() => toggleFlag(flag)}
                className={`px-2 py-0.5 rounded text-[11px] font-mono transition ${
                  active
                    ? 'bg-cyan-950 text-cyan-300 border border-cyan-700/60'
                    : 'bg-elevated text-slate-400 hover:text-slate-200 border border-borderSubtle'
                }`}
              >
                {flag}
              </button>
            );
          })}
        </div>
      </div>

      {/* Compilation Result Metrics */}
      {compilation && (
        <div className="space-y-2 pt-2 border-t border-borderSubtle">
          <div className="flex items-center justify-between text-xs font-mono">
            <div className="flex items-center space-x-1.5">
              {compilation.success ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : (
                <XCircle className="w-4 h-4 text-rose-400" />
              )}
              <span className={compilation.success ? 'text-emerald-400' : 'text-rose-400'}>
                {compilation.success ? 'Build Succeeded' : 'Build Failed'}
              </span>
            </div>
            <span className="text-slate-400">{compilation.compilation_time_ms} ms</span>
          </div>

          {compilation.binary_size_bytes !== null && (
            <div className="flex justify-between text-[11px] font-mono text-slate-400 bg-elevated/60 px-2 py-1 rounded">
              <span>Binary Size:</span>
              <span className="text-slate-200">{compilation.binary_size_bytes.toLocaleString()} bytes</span>
            </div>
          )}

          {/* Diagnostic Terminal Toggle */}
          <div className="pt-1">
            <button
              onClick={() => setShowTerminal(!showTerminal)}
              className="w-full flex items-center justify-between text-[11px] font-mono text-slate-400 hover:text-slate-200 py-1"
            >
              <div className="flex items-center space-x-1.5">
                <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                <span>Diagnostics & Output</span>
              </div>
              {showTerminal ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>

            {showTerminal && (
              <pre className="mt-1 p-2 bg-slate-950 rounded border border-borderSubtle text-[11px] font-mono text-slate-300 overflow-x-auto max-h-40 leading-relaxed">
                {compilation.stderr || compilation.stdout || 'Compilation finished with 0 warnings.'}
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
