import React, { useState } from 'react';
import {
  FileText,
  Download,
  Copy,
  Check,
  X,
  Code2,
} from 'lucide-react';
import { BenchmarkSuiteResponse, RecommendationResponse } from '../../types';

interface ReportExporterProps {
  isOpen: boolean;
  onClose: () => void;
  suite: BenchmarkSuiteResponse | null;
  recommendation: RecommendationResponse | null;
  filename: string;
}

export const ReportExporter: React.FC<ReportExporterProps> = ({
  isOpen,
  onClose,
  suite,
  recommendation,
  filename,
}) => {
  const [activeTab, setActiveTab] = useState<'markdown' | 'json'>('markdown');
  const [copied, setCopied] = useState(false);

  if (!isOpen || !suite) return null;

  const results = suite.results;
  const bestSpeedup = [...results].sort(
    (a, b) => (b.speedup_vs_o0 || 1) - (a.speedup_vs_o0 || 1)
  )[0];

  const generateMarkdownReport = (): string => {
    const timestamp = new Date().toISOString();
    return `# CompilerX Performance Audit & Optimization Report
**Target File:** \`${filename}\`  
**Generated At:** \`${timestamp}\`  
**Suite ID:** \`${suite.suite_id}\`  

---

## 1. Executive Summary
- **Baseline (-O0) Runtime:** \`${results.find((r) => r.optimization_level === '-O0')?.mean_time_ms.toFixed(3)} ms\`
- **Optimal Optimization Level:** \`${bestSpeedup.optimization_level}\`
- **Peak Observed Speedup:** \`${bestSpeedup.speedup_vs_o0.toFixed(2)}x\` faster than baseline
- **Peak RSS Memory Footprint:** \`${bestSpeedup.peak_memory_kb.toLocaleString()} KB\`
- **AI Recommendation:** \`${recommendation?.recommended_level || 'N/A'}\` (Confidence: ${
      recommendation ? (recommendation.confidence_score * 100).toFixed(1) + '%' : 'N/A'
    })

---

## 2. Benchmark Measurement Matrix
Execution times captured via high-resolution native C harness using \`clock_gettime(CLOCK_MONOTONIC_RAW)\`.

| Level | Mean Time (ms) | Median Time (ms) | StdDev (ms) | Variance CV% | Speedup vs -O0 | Binary Size | Reliability |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
${results
  .map(
    (r) =>
      `| \`${r.optimization_level}\` | ${r.mean_time_ms.toFixed(3)} | ${r.median_time_ms.toFixed(
        3
      )} | ±${r.stddev_time_ms.toFixed(3)} | ${r.variance_cv_percent.toFixed(
        1
      )}% | **${r.speedup_vs_o0.toFixed(2)}x** | ${(r.binary_size_bytes / 1024).toFixed(
        1
      )} KB | ${r.has_high_variance ? '⚠️ High Variance' : '✅ Consistent'} |`
  )
  .join('\n')}

---

## 3. Machine Learning Adaptive Optimization Analysis
${
  recommendation
    ? `
- **Model Architecture:** Random Forest Classifier (100 Estimators)
- **Objective:** \`${recommendation.objective}\`
- **Predicted Flag:** \`${recommendation.recommended_level}\`
- **Confidence:** \`${(recommendation.confidence_score * 100).toFixed(1)}%\`
- **Decision Rationale:**
  > ${recommendation.explanation}

### Top AST Feature Drivers
${recommendation.top_influencing_features
  ?.map((f) => `- **${f.feature.replace(/_/g, ' ')}**: Feature weight ${(f.importance * 100).toFixed(1)}%`)
  .join('\n')}
`
    : '*No machine learning inference was generated for this session.*'
}

---

## 4. Engineering Verification & Audit Integrity
- **Sandboxing:** Isolated subprocess execution under controlled cgroups and memory quotas.
- **Outlier Rejection:** Statistical outlier rejection and sample standard deviation verification.
- **Reproducibility:** Run verified with CompilerX automated benchmark harness.
`;
  };

  const generateJsonReport = (): string => {
    return JSON.stringify(
      {
        report_meta: {
          system: 'CompilerX AI Platform',
          version: '1.0.0',
          filename,
          timestamp: new Date().toISOString(),
        },
        benchmark_suite: suite,
        ml_recommendation: recommendation,
      },
      null,
      2
    );
  };

  const content = activeTab === 'markdown' ? generateMarkdownReport() : generateJsonReport();

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = activeTab === 'markdown' ? 'md' : 'json';
    const mime = activeTab === 'markdown' ? 'text/markdown' : 'application/json';
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `compilerx-report-${filename.replace(/[^a-zA-Z0-9_-]/g, '_')}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl w-full max-w-3xl overflow-hidden shadow-2xl flex flex-col max-h-[85vh]">
        {/* Modal Header */}
        <div className="px-5 py-4 border-b border-zinc-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-zinc-100">Performance Audit Report</h2>
              <p className="text-xs text-zinc-400">Export verified benchmark and ML recommendation data</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 rounded-lg transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Format Selector Bar */}
        <div className="px-5 py-2.5 bg-zinc-950/60 border-b border-zinc-800 flex items-center justify-between">
          <div className="flex bg-zinc-900 p-0.5 rounded-lg border border-zinc-800 text-xs">
            <button
              onClick={() => setActiveTab('markdown')}
              className={`px-3 py-1 rounded-md transition-colors flex items-center gap-1.5 ${
                activeTab === 'markdown'
                  ? 'bg-zinc-800 text-zinc-100 font-medium'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              Markdown (.md)
            </button>
            <button
              onClick={() => setActiveTab('json')}
              className={`px-3 py-1 rounded-md transition-colors flex items-center gap-1.5 ${
                activeTab === 'json'
                  ? 'bg-zinc-800 text-zinc-100 font-medium'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <Code2 className="w-3.5 h-3.5" />
              Raw JSON
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium flex items-center gap-1.5 transition-colors border border-zinc-700"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? 'Copied' : 'Copy'}
            </button>
            <button
              onClick={handleDownload}
              className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium flex items-center gap-1.5 transition-colors shadow-md shadow-indigo-950/50"
            >
              <Download className="w-3.5 h-3.5" />
              Download Report
            </button>
          </div>
        </div>

        {/* Report Content Preview */}
        <div className="flex-1 overflow-auto p-5 bg-zinc-950 font-mono text-xs text-zinc-300 leading-relaxed whitespace-pre-wrap select-text">
          {content}
        </div>
      </div>
    </div>
  );
};
