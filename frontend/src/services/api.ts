import axios from 'axios';
import {
  Project,
  SourceFile,
  SourceFileDetail,
  Compilation,
  BenchmarkRunResponse,
  BenchmarkSuiteResponse,
  FeatureVector,
  RecommendationResponse,
  ModelStatusResponse,
  SystemHealth,
  OptimizationLevel,
  Objective,
} from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Projects API
export const getProjects = async (): Promise<Project[]> => {
  const res = await api.get('/projects');
  return res.data.items;
};

export const createProject = async (name: string, description?: string, language: string = 'c'): Promise<Project> => {
  const res = await api.post('/projects', { name, description, language });
  return res.data;
};

export const deleteProject = async (projectId: string): Promise<void> => {
  await api.delete(`/projects/${projectId}`);
};

// Files API
export const getProjectFiles = async (projectId: string): Promise<SourceFile[]> => {
  const res = await api.get(`/projects/${projectId}/files`);
  return res.data;
};

export const getFileDetail = async (fileId: string): Promise<SourceFileDetail> => {
  const res = await api.get(`/files/${fileId}`);
  return res.data;
};

export const createSourceFile = async (
  projectId: string,
  filename: string,
  content: string
): Promise<SourceFile> => {
  const res = await api.post(`/projects/${projectId}/files`, { filename, content });
  return res.data;
};

export const updateSourceFile = async (
  fileId: string,
  content: string,
  filename?: string
): Promise<SourceFileDetail> => {
  const res = await api.put(`/files/${fileId}`, { content, filename });
  return res.data;
};

export const deleteSourceFile = async (fileId: string): Promise<void> => {
  await api.delete(`/files/${fileId}`);
};

// Compilation API
export const compileFile = async (
  fileId: string,
  optimizationLevel: OptimizationLevel = '-O0',
  compilerFlags: string[] = []
): Promise<Compilation> => {
  const res = await api.post(`/files/${fileId}/compile`, {
    optimization_level: optimizationLevel,
    compiler_flags: compilerFlags,
  });
  return res.data;
};

export const getFileCompilations = async (fileId: string): Promise<Compilation[]> => {
  const res = await api.get(`/files/${fileId}/compilations`);
  return res.data;
};

// Benchmarking API
export const benchmarkCompilation = async (
  compilationId: string,
  numRuns: number = 5,
  stdinPayload?: string
): Promise<BenchmarkRunResponse> => {
  const res = await api.post(`/compilations/${compilationId}/benchmark`, {
    num_runs: numRuns,
    stdin_payload: stdinPayload,
  });
  return res.data;
};

export const runBenchmarkSuite = async (
  fileId: string,
  runsPerLevel: number = 5,
  stdinPayload?: string
): Promise<BenchmarkSuiteResponse> => {
  const res = await api.post(`/files/${fileId}/benchmark-suite`, {
    runs_per_level: runsPerLevel,
    stdin_payload: stdinPayload,
  });
  return res.data;
};

export const getSuiteStatus = async (suiteId: string): Promise<BenchmarkSuiteResponse> => {
  const res = await api.get(`/benchmarks/suite/${suiteId}`);
  return res.data;
};

// ML Optimization API
export const extractFeatures = async (fileId: string): Promise<FeatureVector> => {
  const res = await api.get(`/optimization/features/${fileId}`);
  return res.data;
};

export const getRecommendation = async (
  fileId: string,
  objective: Objective = 'SPEED'
): Promise<RecommendationResponse> => {
  const res = await api.post(`/files/${fileId}/recommend`, { objective });
  return res.data;
};

export const getModelStatus = async (): Promise<ModelStatusResponse> => {
  const res = await api.get('/ml/model/status');
  return res.data;
};

export const retrainModel = async (): Promise<ModelStatusResponse> => {
  const res = await api.post('/ml/model/retrain');
  return res.data;
};

// System Health API
export const getSystemHealth = async (): Promise<SystemHealth> => {
  const res = await api.get('/health');
  return res.data;
};

export default api;

