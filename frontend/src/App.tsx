import React, { useState } from 'react';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';
import { CodeEditor } from './components/editor/CodeEditor';
import { CompilerPanel } from './components/compiler/CompilerPanel';
import { MLRecommendationCard } from './components/ml/MLRecommendationCard';
import { BenchmarkRunner } from './components/benchmark/BenchmarkRunner';
import { AnalyticsDashboard } from './components/analytics/AnalyticsDashboard';
import { ReportExporter } from './components/reports/ReportExporter';
import { Code, BarChart3, Sliders, Cpu, Activity } from 'lucide-react';
import { BenchmarkSuiteResponse, OptimizationLevel } from './types';
import { useEditorStore } from './stores/useEditorStore';

export const App: React.FC = () => {
  const { activeFile, setOptLevel, recommendation } = useEditorStore();
  const [activeMainTab, setActiveMainTab] = useState<'editor' | 'analytics'>('editor');
  const [activeRightTab, setActiveRightTab] = useState<'compiler' | 'ml' | 'benchmark'>('compiler');
  const [latestSuite, setLatestSuite] = useState<BenchmarkSuiteResponse | null>(null);
  const [isReportOpen, setIsReportOpen] = useState<boolean>(false);

  const handleSuiteComplete = (suite: BenchmarkSuiteResponse) => {
    setLatestSuite(suite);
    setActiveMainTab('analytics');
  };

  const handleApplyRecommendedLevel = (level: OptimizationLevel) => {
    setOptLevel(level);
    setActiveRightTab('compiler');
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-zinc-950 text-zinc-100">
      {/* Top Navigation */}
      <Navbar />

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar />

        {/* Center Main Stage (Editor or Analytics) */}
        <div className="flex-1 flex flex-col min-w-0 bg-zinc-950 border-r border-zinc-800">
          {/* Main Stage Tabs */}
          <div className="h-10 bg-zinc-900 border-b border-zinc-800 flex items-center justify-between px-3">
            <div className="flex items-center gap-1">
              <button
                onClick={() => setActiveMainTab('editor')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md flex items-center gap-2 transition-colors ${
                  activeMainTab === 'editor'
                    ? 'bg-zinc-800 text-zinc-100'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
                }`}
              >
                <Code className="w-3.5 h-3.5 text-blue-400" />
                <span>Source Editor</span>
                {activeFile && (
                  <span className="text-[10px] px-1.5 py-0.2 bg-zinc-900 text-zinc-400 rounded font-mono">
                    {activeFile.filename}
                  </span>
                )}
              </button>

              <button
                onClick={() => setActiveMainTab('analytics')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md flex items-center gap-2 transition-colors ${
                  activeMainTab === 'analytics'
                    ? 'bg-zinc-800 text-zinc-100'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
                }`}
              >
                <BarChart3 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Performance Analytics</span>
                {latestSuite && (
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                )}
              </button>
            </div>

            {/* Quick Export Button when Suite exists */}
            {latestSuite && (
              <button
                onClick={() => setIsReportOpen(true)}
                className="text-[11px] font-medium text-indigo-400 hover:text-indigo-300 px-2 py-1 rounded bg-indigo-950/40 border border-indigo-800/50 transition-colors"
              >
                Export Report
              </button>
            )}
          </div>

          {/* Tab Viewport */}
          <div className="flex-1 overflow-hidden">
            {activeMainTab === 'editor' ? (
              <CodeEditor />
            ) : (
              <div className="h-full overflow-y-auto p-6">
                <AnalyticsDashboard
                  suite={latestSuite}
                  onExportClick={() => setIsReportOpen(true)}
                />
              </div>
            )}
          </div>
        </div>

        {/* Right Inspector Panel (Compiler, ML, Benchmarks) */}
        <div className="w-80 md:w-96 flex flex-col bg-zinc-950 shrink-0">
          {/* Right Panel Tabs */}
          <div className="h-10 bg-zinc-900 border-b border-zinc-800 flex items-center px-2 gap-1">
            <button
              onClick={() => setActiveRightTab('compiler')}
              className={`flex-1 py-1.5 text-[11px] font-medium rounded-md flex items-center justify-center gap-1.5 transition-colors ${
                activeRightTab === 'compiler'
                  ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
              }`}
            >
              <Sliders className="w-3 h-3 text-blue-400" />
              <span>Compiler</span>
            </button>

            <button
              onClick={() => setActiveRightTab('ml')}
              className={`flex-1 py-1.5 text-[11px] font-medium rounded-md flex items-center justify-center gap-1.5 transition-colors ${
                activeRightTab === 'ml'
                  ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
              }`}
            >
              <Cpu className="w-3 h-3 text-purple-400" />
              <span>AI Optimizer</span>
            </button>

            <button
              onClick={() => setActiveRightTab('benchmark')}
              className={`flex-1 py-1.5 text-[11px] font-medium rounded-md flex items-center justify-center gap-1.5 transition-colors ${
                activeRightTab === 'benchmark'
                  ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
              }`}
            >
              <Activity className="w-3 h-3 text-emerald-400" />
              <span>Benchmarking</span>
            </button>
          </div>

          {/* Right Panel Content */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {activeRightTab === 'compiler' && <CompilerPanel />}

            {activeRightTab === 'ml' && (
              <MLRecommendationCard
                onApplyLevel={handleApplyRecommendedLevel}
              />
            )}

            {activeRightTab === 'benchmark' && (
              <BenchmarkRunner onSuiteComplete={handleSuiteComplete} />
            )}
          </div>
        </div>
      </div>

      {/* Audit Report Modal */}
      <ReportExporter
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        suite={latestSuite}
        recommendation={recommendation}
        filename={activeFile?.filename || 'program.c'}
      />
    </div>
  );
};
