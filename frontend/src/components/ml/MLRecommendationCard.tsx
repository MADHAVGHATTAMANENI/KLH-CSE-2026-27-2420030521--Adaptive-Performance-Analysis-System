import React, { useState } from 'react';
import {
  Sparkles,
  Cpu,
  Target,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Info,
  CheckCircle2,
  Sliders,
} from 'lucide-react';
import { RecommendationResponse, Objective, OptimizationLevel } from '../../types';
import { getRecommendation, retrainModel } from '../../services/api';
import { useEditorStore } from '../../stores/useEditorStore';

interface MLRecommendationCardProps {
  onApplyLevel?: (level: OptimizationLevel) => void;
}

export const MLRecommendationCard: React.FC<MLRecommendationCardProps> = ({ onApplyLevel }) => {
  const { activeFile } = useEditorStore();
  const [objective, setObjective] = useState<Objective>('SPEED');
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [retraining, setRetraining] = useState(false);
  const [showFeatures, setShowFeatures] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendation = async (targetObjective = objective) => {
    if (!activeFile) return;
    setLoading(true);
    setError(null);
    try {
      const rec = await getRecommendation(activeFile.id, targetObjective);
      setRecommendation(rec);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to infer recommendation from ML model.');
    } finally {
      setLoading(false);
    }
  };

  const handleRetrain = async () => {
    setRetraining(true);
    setError(null);
    try {
      await retrainModel();
      await fetchRecommendation(objective);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Retraining failed.');
    } finally {
      setRetraining(false);
    }
  };

  if (!activeFile) {
    return (
      <div className="p-4 text-center text-xs text-zinc-500 border border-zinc-800 rounded-lg bg-zinc-950/40">
        Select a source file to analyze optimization vectors.
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden shadow-lg">
      {/* Header */}
      <div className="px-4 py-3 bg-zinc-900/90 border-b border-zinc-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-md bg-purple-500/10 text-purple-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-zinc-200">Adaptive AI Optimizer</h3>
            <p className="text-[10px] text-zinc-400">Random Forest (100 Trees) • Static AST Analysis</p>
          </div>
        </div>
        <button
          onClick={handleRetrain}
          disabled={retraining}
          title="Retrain Random Forest on benchmark corpus"
          className="p-1 text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 rounded transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${retraining ? 'animate-spin text-purple-400' : ''}`} />
        </button>
      </div>

      <div className="p-4 space-y-4">
        {/* Objective Selector */}
        <div className="flex items-center justify-between gap-2">
          <label className="text-[11px] font-medium text-zinc-400 flex items-center gap-1.5">
            <Target className="w-3.5 h-3.5 text-zinc-500" />
            Target Metric:
          </label>
          <div className="flex bg-zinc-950 p-0.5 rounded-md border border-zinc-800 text-[11px]">
            {(['SPEED', 'SIZE', 'BALANCED'] as Objective[]).map((obj) => (
              <button
                key={obj}
                onClick={() => {
                  setObjective(obj);
                  if (recommendation) {
                    fetchRecommendation(obj);
                  }
                }}
                className={`px-2 py-1 rounded transition-colors font-mono ${
                  objective === obj
                    ? 'bg-purple-600/30 text-purple-300 font-medium'
                    : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {obj}
              </button>
            ))}
          </div>
        </div>

        {/* Action Button */}
        {!recommendation && (
          <button
            onClick={() => fetchRecommendation(objective)}
            disabled={loading}
            className="w-full py-2 px-3 rounded-md bg-purple-600 hover:bg-purple-500 text-white font-medium text-xs flex items-center justify-center gap-2 transition-all shadow-md shadow-purple-950/50 disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Analyzing 16D Feature Vector...
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                Predict Optimal Flag
              </>
            )}
          </button>
        )}

        {error && (
          <div className="p-2.5 rounded bg-red-950/40 border border-red-800/60 text-red-300 text-xs flex items-start gap-2">
            <Info className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Recommendation Result Presentation */}
        {recommendation && (
          <div className="space-y-3 pt-1">
            <div className="flex items-center justify-between p-3 rounded-md bg-zinc-950 border border-purple-900/40">
              <div className="space-y-1">
                <span className="text-[10px] uppercase font-mono tracking-wider text-purple-400">
                  Recommended Configuration
                </span>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold font-mono text-white">
                    {recommendation.recommended_level}
                  </span>
                  <span className="text-xs text-zinc-400">
                    {(recommendation.confidence_score * 100).toFixed(1)}% confidence
                  </span>
                </div>
              </div>

              {onApplyLevel && (
                <button
                  onClick={() => onApplyLevel(recommendation.recommended_level)}
                  className="px-2.5 py-1.5 text-xs font-medium rounded bg-purple-600/20 text-purple-300 hover:bg-purple-600/30 border border-purple-500/30 flex items-center gap-1.5 transition-colors"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Apply
                </button>
              )}
            </div>

            {/* Confidence Bar */}
            <div className="space-y-1">
              <div className="flex justify-between text-[10px] text-zinc-400">
                <span>Model Confidence</span>
                <span className="font-mono">{(recommendation.confidence_score * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden border border-zinc-800">
                <div
                  className="h-full bg-gradient-to-r from-purple-600 to-indigo-500 transition-all duration-500"
                  style={{ width: `${Math.min(100, recommendation.confidence_score * 100)}%` }}
                />
              </div>
            </div>

            {/* Explainability Reasoning */}
            <div className="p-2.5 rounded bg-zinc-950/60 border border-zinc-800/80 text-[11px] leading-relaxed text-zinc-300">
              <p className="font-sans">{recommendation.explanation}</p>
            </div>

            {/* Top Influencing Features */}
            {recommendation.top_influencing_features && recommendation.top_influencing_features.length > 0 && (
              <div className="space-y-1.5 pt-1">
                <span className="text-[10px] font-medium uppercase tracking-wider text-zinc-400 flex items-center gap-1">
                  <Cpu className="w-3 h-3 text-zinc-500" />
                  Top Decision Drivers
                </span>
                <div className="space-y-1">
                  {recommendation.top_influencing_features.slice(0, 3).map((feat, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between text-[11px] px-2 py-1 rounded bg-zinc-950/40 border border-zinc-800/60 font-mono"
                    >
                      <span className="text-zinc-300">{feat.feature.replace(/_/g, ' ')}</span>
                      <span className="text-purple-400 text-[10px]">
                        weight: {(feat.importance * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 16D Feature Vector Collapsible */}
            <div className="border-t border-zinc-800/80 pt-2">
              <button
                onClick={() => setShowFeatures(!showFeatures)}
                className="w-full flex items-center justify-between text-[10px] text-zinc-400 hover:text-zinc-200 py-1 transition-colors"
              >
                <span className="flex items-center gap-1 font-mono">
                  <Sliders className="w-3 h-3" />
                  {showFeatures ? 'Hide' : 'Inspect'} 16D Extracted AST Vectors
                </span>
                {showFeatures ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>

              {showFeatures && (
                <div className="mt-2 p-2 rounded bg-zinc-950 border border-zinc-800 grid grid-cols-2 gap-1.5 font-mono text-[10px] max-h-48 overflow-y-auto">
                  {Object.entries(recommendation.features_extracted).map(([key, val]) => (
                    <div key={key} className="flex justify-between p-1 bg-zinc-900/60 rounded">
                      <span className="text-zinc-400 truncate mr-2" title={key}>
                        {key}
                      </span>
                      <span className="text-purple-300 font-semibold">{val}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button
              onClick={() => fetchRecommendation(objective)}
              disabled={loading}
              className="w-full py-1.5 text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 rounded transition-colors flex items-center justify-center gap-1.5"
            >
              <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
              Re-analyze
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
