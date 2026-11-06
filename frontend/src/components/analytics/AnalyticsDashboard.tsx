import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import {
  TrendingUp,
  HardDrive,
  Cpu,
  Clock,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react';
import { BenchmarkSuiteResponse } from '../../types';

interface AnalyticsDashboardProps {
  suite: BenchmarkSuiteResponse | null;
  onExportClick?: () => void;
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  suite,
  onExportClick,
}) => {
  if (!suite || !suite.results || suite.results.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-8 text-center bg-zinc-950/40 border border-zinc-800 rounded-lg">
        <Cpu className="w-10 h-10 text-zinc-600 mb-3" />
        <h3 className="text-sm font-semibold text-zinc-300">No Benchmark Data Available</h3>
        <p className="text-xs text-zinc-500 max-w-sm mt-1">
          Execute a benchmark suite from the right panel to analyze multi-level execution timing, variance, speedup curves, and binary size profiles.
        </p>
      </div>
    );
  }

  const results = suite.results;
  const o0Result = results.find((r) => r.optimization_level === '-O0') || results[0];

  // Best speedup
  const bestSpeedupResult = [...results].sort(
    (a, b) => (b.speedup_vs_o0 || 1) - (a.speedup_vs_o0 || 1)
  )[0];

  // Smallest binary
  const smallestBinaryResult = [...results].sort(
    (a, b) => a.binary_size_bytes - b.binary_size_bytes
  )[0];

  // Detect regression: e.g. -O3 slower than -O2
  const o2Result = results.find((r) => r.optimization_level === '-O2');
  const o3Result = results.find((r) => r.optimization_level === '-O3');
  const hasRegression =
    o2Result && o3Result && o3Result.mean_time_ms > o2Result.mean_time_ms;

  const chartData = results.map((r) => ({
    level: r.optimization_level,
    runtime: Number(r.mean_time_ms.toFixed(3)),
    speedup: Number(r.speedup_vs_o0.toFixed(2)),
    binarySizeKB: Number((r.binary_size_bytes / 1024).toFixed(1)),
    stddev: Number(r.stddev_time_ms.toFixed(3)),
    hasHighVariance: r.has_high_variance,
  }));

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    return `${(bytes / 1024).toFixed(1)} KB`;
  };

  const getBarColor = (level: string) => {
    switch (level) {
      case '-O0':
        return '#71717a'; // zinc-500
      case '-O1':
        return '#3b82f6'; // blue-500
      case '-O2':
        return '#8b5cf6'; // violet-500
      case '-O3':
        return '#10b981'; // emerald-500
      default:
        return '#6366f1';
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Export Action */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
            Performance & Comparative Analytics
          </h2>
          <p className="text-xs text-zinc-400">
            Statistical execution analysis across Clang optimization levels
          </p>
        </div>

        {onExportClick && (
          <button
            onClick={onExportClick}
            className="px-3 py-1.5 text-xs font-medium rounded-md bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 flex items-center gap-1.5 transition-colors"
          >
            Export Audit Report
          </button>
        )}
      </div>

      {/* Regression Banner */}
      {hasRegression && (
        <div className="p-3 rounded-lg bg-amber-950/40 border border-amber-800/60 text-amber-300 text-xs flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <strong className="font-semibold">Performance Regression Detected at -O3:</strong>
            <p className="text-amber-200/80 mt-0.5">
              Runtime with -O3 ({o3Result.mean_time_ms.toFixed(2)} ms) is higher than -O2 ({o2Result.mean_time_ms.toFixed(2)} ms). This frequently stems from aggressive loop unrolling causing L1 instruction cache thrashing or register spilling.
            </p>
          </div>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Baseline Runtime */}
        <div className="p-3.5 rounded-lg bg-zinc-900 border border-zinc-800 space-y-1">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs">Baseline (-O0)</span>
            <Clock className="w-3.5 h-3.5" />
          </div>
          <div className="text-xl font-bold font-mono text-zinc-100">
            {o0Result.mean_time_ms.toFixed(2)} <span className="text-xs text-zinc-400">ms</span>
          </div>
          <div className="text-[10px] text-zinc-500">Unoptimized baseline</div>
        </div>

        {/* Peak Speedup */}
        <div className="p-3.5 rounded-lg bg-zinc-900 border border-zinc-800 space-y-1">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs">Max Speedup</span>
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="text-xl font-bold font-mono text-emerald-400">
            {bestSpeedupResult.speedup_vs_o0.toFixed(2)}x
          </div>
          <div className="text-[10px] text-zinc-400">
            Achieved at <span className="font-mono text-zinc-200">{bestSpeedupResult.optimization_level}</span>
          </div>
        </div>

        {/* Smallest Binary */}
        <div className="p-3.5 rounded-lg bg-zinc-900 border border-zinc-800 space-y-1">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs">Compact Binary</span>
            <HardDrive className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <div className="text-xl font-bold font-mono text-blue-400">
            {formatBytes(smallestBinaryResult.binary_size_bytes)}
          </div>
          <div className="text-[10px] text-zinc-400">
            at <span className="font-mono text-zinc-200">{smallestBinaryResult.optimization_level}</span>
          </div>
        </div>

        {/* Peak Memory */}
        <div className="p-3.5 rounded-lg bg-zinc-900 border border-zinc-800 space-y-1">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs">Peak RSS Memory</span>
            <Cpu className="w-3.5 h-3.5 text-purple-400" />
          </div>
          <div className="text-xl font-bold font-mono text-purple-400">
            {bestSpeedupResult.peak_memory_kb.toLocaleString()} <span className="text-xs text-zinc-400">KB</span>
          </div>
          <div className="text-[10px] text-zinc-500">Resident set size</div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Runtime Comparison Chart */}
        <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-zinc-200 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-zinc-400" />
              Mean Execution Time (ms) — Lower is Better
            </h3>
          </div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                <XAxis dataKey="level" stroke="#71717a" fontSize={11} tickLine={false} />
                <YAxis stroke="#71717a" fontSize={11} tickLine={false} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800 text-xs shadow-xl space-y-1">
                          <p className="font-mono font-semibold text-zinc-200">{data.level}</p>
                          <p className="text-zinc-400">
                            Mean Runtime: <span className="font-mono text-zinc-100">{data.runtime} ms</span>
                          </p>
                          <p className="text-zinc-400">
                            StdDev: <span className="font-mono text-zinc-100">±{data.stddev} ms</span>
                          </p>
                          <p className="text-emerald-400">
                            Speedup: <span className="font-mono font-semibold">{data.speedup}x</span>
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="runtime" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={getBarColor(entry.level)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Binary Size Chart */}
        <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-zinc-200 flex items-center gap-1.5">
              <HardDrive className="w-3.5 h-3.5 text-zinc-400" />
              Compiled Binary Footprint (KB)
            </h3>
          </div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                <XAxis dataKey="level" stroke="#71717a" fontSize={11} tickLine={false} />
                <YAxis stroke="#71717a" fontSize={11} tickLine={false} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800 text-xs shadow-xl space-y-1">
                          <p className="font-mono font-semibold text-zinc-200">{data.level}</p>
                          <p className="text-zinc-400">
                            Binary Size: <span className="font-mono text-zinc-100">{data.binarySizeKB} KB</span>
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="binarySizeKB" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Detailed Statistical Table */}
      <div className="rounded-lg bg-zinc-900 border border-zinc-800 overflow-hidden">
        <div className="px-4 py-3 border-b border-zinc-800 flex items-center justify-between">
          <h3 className="text-xs font-semibold text-zinc-200">Comparative Performance Matrix</h3>
          <span className="text-[10px] text-zinc-500 font-mono">
            {suite.results[0]?.variance_cv_percent !== undefined ? 'Multi-Run Aggregated' : ''}
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-zinc-800 bg-zinc-950/50 text-[11px] font-mono text-zinc-400 uppercase tracking-wider">
                <th className="py-2.5 px-3">Level</th>
                <th className="py-2.5 px-3">Mean (ms)</th>
                <th className="py-2.5 px-3">Median (ms)</th>
                <th className="py-2.5 px-3">StdDev</th>
                <th className="py-2.5 px-3">CV %</th>
                <th className="py-2.5 px-3">Speedup</th>
                <th className="py-2.5 px-3">Binary Size</th>
                <th className="py-2.5 px-3">Peak RSS</th>
                <th className="py-2.5 px-3 text-right">Reliability</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60 font-mono">
              {results.map((r) => (
                <tr key={r.optimization_level} className="hover:bg-zinc-800/30 transition-colors">
                  <td className="py-2.5 px-3 font-bold text-zinc-200 flex items-center gap-1.5">
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: getBarColor(r.optimization_level) }}
                    />
                    {r.optimization_level}
                  </td>
                  <td className="py-2.5 px-3 text-zinc-200">{r.mean_time_ms.toFixed(3)}</td>
                  <td className="py-2.5 px-3 text-zinc-400">{r.median_time_ms.toFixed(3)}</td>
                  <td className="py-2.5 px-3 text-zinc-500">±{r.stddev_time_ms.toFixed(3)}</td>
                  <td className="py-2.5 px-3">
                    <span
                      className={
                        r.variance_cv_percent > 10
                          ? 'text-amber-400 font-semibold'
                          : 'text-zinc-400'
                      }
                    >
                      {r.variance_cv_percent.toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-2.5 px-3">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                        r.speedup_vs_o0 > 1.05
                          ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/60'
                          : r.speedup_vs_o0 < 0.95
                          ? 'bg-red-950/60 text-red-400 border border-red-800/60'
                          : 'bg-zinc-800 text-zinc-400'
                      }`}
                    >
                      {r.speedup_vs_o0.toFixed(2)}x
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-zinc-300">{formatBytes(r.binary_size_bytes)}</td>
                  <td className="py-2.5 px-3 text-zinc-400">{r.peak_memory_kb.toLocaleString()} KB</td>
                  <td className="py-2.5 px-3 text-right">
                    {r.has_high_variance ? (
                      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-amber-950/50 text-amber-400 border border-amber-800/50 text-[10px]">
                        <AlertTriangle className="w-3 h-3" /> High Variance
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-emerald-400 text-[10px]">
                        <CheckCircle2 className="w-3 h-3" /> Consistent
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
