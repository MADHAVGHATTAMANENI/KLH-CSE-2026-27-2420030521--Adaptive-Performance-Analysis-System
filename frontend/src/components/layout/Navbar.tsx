import React, { useEffect, useState } from 'react';
import { Cpu, Terminal, ShieldCheck, Activity, FolderPlus } from 'lucide-react';
import { useProjectStore } from '../../stores/useProjectStore';
import { getSystemHealth } from '../../services/api';
import { SystemHealth } from '../../types';

export const Navbar: React.FC = () => {
  const { projects, activeProject, fetchProjects, selectProject, createProject } = useProjectStore();
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [showNewModal, setShowNewModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');

  useEffect(() => {
    fetchProjects().then(async () => {
      const state = useProjectStore.getState();
      if (state.projects.length === 0) {
        await createProject('CompilerX Sandbox', 'Default workspace for C/C++ benchmarks');
      }
    }).catch(() => {});

    getSystemHealth().then(setHealth).catch(() => {});
    const interval = setInterval(() => {
      getSystemHealth().then(setHealth).catch(() => {});
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    await createProject(newProjectName.trim());
    setNewProjectName('');
    setShowNewModal(false);
  };

  return (
    <header className="h-14 border-b border-borderSubtle bg-surface px-4 flex items-center justify-between z-20">
      {/* Brand & Project Selector */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Cpu className="w-4 h-4" />
          </div>
          <span className="font-bold text-slate-100 tracking-tight font-mono text-base">CompilerX</span>
          <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            v1.0.0
          </span>
        </div>

        <div className="h-4 w-px bg-slate-800" />

        {/* Project Dropdown */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400">Project:</span>
          <select
            value={activeProject?.id || ''}
            onChange={(e) => selectProject(e.target.value)}
            className="bg-elevated border border-borderFocus rounded px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.language.toUpperCase()})
              </option>
            ))}
          </select>

          <button
            onClick={() => setShowNewModal(true)}
            className="p-1 rounded text-slate-400 hover:text-cyan-400 hover:bg-slate-800 transition"
            title="Create New Project"
          >
            <FolderPlus className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Health & Status Indicators */}
      <div className="flex items-center space-x-4 text-xs font-mono">
        <div className="flex items-center space-x-1.5 text-slate-400">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>SecOps: Hardened</span>
        </div>

        <div className="flex items-center space-x-1.5 text-slate-400">
          <Terminal className="w-3.5 h-3.5 text-cyan-400" />
          <span>Clang 17 / LLVM</span>
        </div>

        <div className="flex items-center space-x-1.5 px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <Activity className="w-3 h-3 animate-pulse" />
          <span>{health?.status || 'HEALTHY'}</span>
        </div>
      </div>

      {/* New Project Modal */}
      {showNewModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-surface border border-slate-700 rounded-lg max-w-sm w-full p-5 shadow-2xl">
            <h3 className="text-sm font-semibold text-slate-100 mb-3">Create New Project</h3>
            <form onSubmit={handleCreate}>
              <input
                type="text"
                placeholder="e.g. Matrix Multiply Benchmark"
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value)}
                autoFocus
                className="w-full bg-elevated border border-borderFocus rounded px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500 mb-4"
              />
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowNewModal(false)}
                  className="px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-3 py-1.5 text-xs font-medium bg-cyan-600 hover:bg-cyan-500 text-white rounded transition"
                >
                  Create Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </header>
  );
};

