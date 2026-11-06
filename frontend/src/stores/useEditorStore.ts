import { create } from 'zustand';
import {
  Compilation,
  BenchmarkSuiteResponse,
  RecommendationResponse,
  OptimizationLevel,
} from '../types';
import * as api from '../services/api';

interface EditorState {
  fileId: string | null;
  filename: string;
  content: string;
  activeFile: { id: string; filename: string; content: string } | null;
  isDirty: boolean;
  isSaving: boolean;
  selectedOptLevel: OptimizationLevel;
  auxiliaryFlags: string[];
  stdinPayload: string;

  // Active Results
  compilation: Compilation | null;
  suiteResult: BenchmarkSuiteResponse | null;
  recommendation: RecommendationResponse | null;
  isCompiling: boolean;
  isBenchmarking: boolean;
  isRecommending: boolean;

  // Actions
  loadFile: (fileId: string) => Promise<void>;
  updateContent: (content: string) => void;
  saveFile: () => Promise<void>;
  setOptLevel: (level: OptimizationLevel) => void;
  toggleFlag: (flag: string) => void;
  setStdinPayload: (payload: string) => void;
  compile: () => Promise<Compilation>;
  runSuite: (runsPerLevel?: number) => Promise<BenchmarkSuiteResponse>;
  fetchRecommendation: () => Promise<RecommendationResponse>;
}

export const useEditorStore = create<EditorState>((set, get) => ({
  fileId: null,
  filename: '',
  content: '',
  activeFile: null,
  isDirty: false,
  isSaving: false,
  selectedOptLevel: '-O0',
  auxiliaryFlags: ['-Wall'],
  stdinPayload: '',

  compilation: null,
  suiteResult: null,
  recommendation: null,
  isCompiling: false,
  isBenchmarking: false,
  isRecommending: false,

  loadFile: async (fileId: string) => {
    try {
      const fileDetail = await api.getFileDetail(fileId);
      set({
        fileId: fileDetail.id,
        filename: fileDetail.filename,
        content: fileDetail.content,
        activeFile: {
          id: fileDetail.id,
          filename: fileDetail.filename,
          content: fileDetail.content,
        },
        isDirty: false,
        compilation: null,
        suiteResult: null,
        recommendation: null,
      });
      // Fetch recommendation in background
      get().fetchRecommendation().catch(() => {});
    } catch (err) {
      console.error('Failed to load file', err);
    }
  },

  updateContent: (content: string) => {
    set((state) => ({
      content,
      isDirty: true,
      activeFile: state.activeFile ? { ...state.activeFile, content } : null,
    }));
  },

  saveFile: async () => {
    const { fileId, content } = get();
    if (!fileId) return;
    set({ isSaving: true });
    try {
      await api.updateSourceFile(fileId, content);
      set({ isDirty: false, isSaving: false });
    } catch (err) {
      set({ isSaving: false });
      console.error('Failed to save file', err);
    }
  },

  setOptLevel: (selectedOptLevel: OptimizationLevel) => {
    set({ selectedOptLevel });
  },

  toggleFlag: (flag: string) => {
    set((state) => {
      const exists = state.auxiliaryFlags.includes(flag);
      const auxiliaryFlags = exists
        ? state.auxiliaryFlags.filter((f) => f !== flag)
        : [...state.auxiliaryFlags, flag];
      return { auxiliaryFlags };
    });
  },

  setStdinPayload: (stdinPayload: string) => {
    set({ stdinPayload });
  },

  compile: async () => {
    const { fileId, selectedOptLevel, auxiliaryFlags, isDirty } = get();
    if (!fileId) throw new Error('No active file');
    if (isDirty) {
      await get().saveFile();
    }
    set({ isCompiling: true });
    try {
      const compilation = await api.compileFile(fileId, selectedOptLevel, auxiliaryFlags);
      set({ compilation, isCompiling: false });
      return compilation;
    } catch (err) {
      set({ isCompiling: false });
      throw err;
    }
  },

  runSuite: async (runsPerLevel: number = 5) => {
    const { fileId, stdinPayload, isDirty } = get();
    if (!fileId) throw new Error('No active file');
    if (isDirty) {
      await get().saveFile();
    }
    set({ isBenchmarking: true });
    try {
      const suite = await api.runBenchmarkSuite(fileId, runsPerLevel, stdinPayload);
      set({ suiteResult: suite, isBenchmarking: false });
      return suite;
    } catch (err) {
      set({ isBenchmarking: false });
      throw err;
    }
  },

  fetchRecommendation: async () => {
    const { fileId } = get();
    if (!fileId) throw new Error('No active file');
    set({ isRecommending: true });
    try {
      const recommendation = await api.getRecommendation(fileId, 'SPEED');
      set({ recommendation, isRecommending: false });
      return recommendation;
    } catch (err) {
      set({ isRecommending: false });
      throw err;
    }
  },
}));
