import React, { useState } from 'react';
import {
  Play,
  RotateCcw,
  Sliders,
  Terminal,
  Activity,
  AlertTriangle,
  Layers,
} from 'lucide-react';
import { BenchmarkSuiteResponse } from '../../types';
import { runBenchmarkSuite } from '../../services/api';
import { useEditorStore } from '../../stores/useEditorStore';

interface BenchmarkRunnerProps {
  onSuiteComplete?: (suite: BenchmarkSuiteResponse) => void;
}

export const BenchmarkRunner: React.FC<BenchmarkRunnerProps> = ({ onSuiteComplete }) => {
  const { activeFile } = useEditorStore();
  const [runsPerLevel, setRunsPerLevel] = useState<number>(5);
  const [stdinPayload, setStdinPayload] = useState<string>('');
  const [showStdin, setShowStdin] = useState<boolean>(false);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [currentLevel, setCurrentLevel] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRunSuite = async () => {
    if (!activeFile) return;
    setIsRunning(true);
    setError(null);
    setCurrentLevel('Compiling & Executing Matrix (-O0 ... -O3)');

    try {
      const suite = await runBenchmarkSuite(
        activeFile.id,
        runsPerLevel,
        stdinPayload.trim() ? stdinPayload : undefined
      );

      if (onSuiteComplete) {
        onSuiteComplete(suite);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Benchmark suite execution failed.');
    } finally {
      setIsRunning(false);
      setCurrentLevel(null);
    }
  };

  if (!activeFile) {
    return (
      <div className="p-4 text-center text-xs text-zinc-500 border border-zinc-800 rounded-lg bg-zinc-950/40">
        Select a file to run controlled benchmark suites.
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden shadow-lg">
      {/* Header */}
      <div className="px-4 py-3 bg-zinc-900/90 border-b border-zinc-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-md bg-emerald-500/10 text-emerald-400">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-zinc-200">Controlled Benchmarking Engine</h3>
            <p className="text-[10px] text-zinc-400">High-Precision Microsecond C Runner (CLOCK_MONOTONIC_RAW)</p>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Controls: Runs per Level */}
        <div className="flex items-center justify-between">
          <label className="text-[11px] font-medium text-zinc-400 flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5 text-zinc-500" />
            Runs Per Level:
          </label>
          <div className="flex bg-zinc-950 p-0.5 rounded-md border border-zinc-800 text-[11px]">
            {[3, 5, 10].map((num) => (
              <button
                key={num}
                onClick={() => setRunsPerLevel(num)}
                disabled={isRunning}
                className={`px-2.5 py-1 rounded transition-colors font-mono ${
                  runsPerLevel === num
                    ? 'bg-emerald-600/30 text-emerald-300 font-semibold'
                    : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {num}x
              </button>
            ))}
          </div>
        </div>

        {/* Stdin Toggle */}
        <div>
          <button
            onClick={() => setShowStdin(!showStdin)}
            className="text-[11px] text-zinc-400 hover:text-zinc-200 flex items-center gap-1.5 transition-colors"
          >
            <Terminal className="w-3.5 h-3.5 text-zinc-500" />
            <span>{showStdin ? 'Hide' : 'Provide'} Custom Stdin Input</span>
          </button>

          {showStdin && (
            <div className="mt-2">
              <textarea
                value={stdinPayload}
                onChange={(e) => setStdinPayload(e.target.value)}
                placeholder="Enter stdin input fed to the benchmark executable..."
                rows={3}
                disabled={isRunning}
                className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-xs font-mono text-zinc-200 focus:outline-none focus:border-zinc-700 resize-none"
              />
            </div>
          )}
        </div>

        {/* Error notification */}
        {error && (
          <div className="p-2.5 rounded bg-red-950/40 border border-red-800/60 text-red-300 text-xs flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Action Button */}
        <button
          onClick={handleRunSuite}
          disabled={isRunning}
          className="w-full py-2.5 px-3 rounded-md bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs flex items-center justify-center gap-2 transition-all shadow-md shadow-emerald-950/50 disabled:opacity-50"
        >
          {isRunning ? (
            <>
              <RotateCcw className="w-4 h-4 animate-spin text-white" />
              <span>{currentLevel || 'Executing Benchmarks...'}</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Run Full Suite (-O0 to -O3)</span>
            </>
          )}
        </button>

        {/* Info Note */}
        <div className="p-2.5 rounded bg-zinc-950/50 border border-zinc-800/60 text-[11px] text-zinc-400 flex items-start gap-2">
          <Layers className="w-3.5 h-3.5 text-zinc-500 shrink-0 mt-0.5" />
          <span>
            Compiles the file at <strong>-O0, -O1, -O2, -O3</strong>, captures exact binary byte sizes, runs {runsPerLevel} iterations per flag, filters outliers, and computes speedup vs -O0.
          </span>
        </div>
      </div>
    </div>
  );
};

