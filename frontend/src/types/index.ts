export type Language = 'c' | 'cpp';
export type OptimizationLevel = '-O0' | '-O1' | '-O2' | '-O3' | '-Os' | '-Oz';
export type Objective = 'SPEED' | 'SIZE' | 'BALANCED';
export type SuiteStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface Project {
  id: string;
  name: string;
  description: string | null;
  language: Language;
  file_count: number;
  created_at: string;
  updated_at: string;
}

export interface SourceFile {
  id: string;
  project_id: string;
  filename: string;
  content_hash: string;
  size_bytes: number;
  created_at: string;
  updated_at: string;
}

export interface SourceFileDetail extends SourceFile {
  content: string;
}

export interface Compilation {
  id: string;
  source_file_id: string;
  optimization_level: OptimizationLevel;
  compiler_flags: string[];
  success: boolean;
  stdout: string;
  stderr: string;
  exit_code: number;
  compilation_time_ms: number;
  binary_size_bytes: number | null;
  created_at: string;
}

export interface BenchmarkRunItem {
  run_index: number;
  wall_time_ms: number;
  user_cpu_time_ms: number;
  sys_cpu_time_ms: number;
  peak_memory_kb: number;
  exit_code: number;
}

export interface BenchmarkStatistics {
  mean_wall_time_ms: number;
  median_wall_time_ms: number;
  stddev_ms: number;
  min_ms: number;
  max_ms: number;
  variance_cv_percent: number;
  has_high_variance: boolean;
}

export interface BenchmarkRunResponse {
  compilation_id: string;
  runs: BenchmarkRunItem[];
  statistics: BenchmarkStatistics;
}

export interface SuiteResultItem {
  optimization_level: OptimizationLevel;
  mean_time_ms: number;
  median_time_ms: number;
  stddev_time_ms: number;
  min_time_ms: number;
  max_time_ms: number;
  variance_cv_percent: number;
  speedup_vs_o0: number;
  peak_memory_kb: number;
  binary_size_bytes: number;
  has_high_variance: boolean;
}

export interface BenchmarkSuiteResponse {
  suite_id: string;
  source_file_id: string;
  status: SuiteStatus;
  started_at: string | null;
  completed_at: string | null;
  results: SuiteResultItem[];
}

export interface FeatureVector {
  lines_of_code: number;
  function_count: number;
  cyclomatic_complexity: number;
  loop_count: number;
  max_loop_nesting_depth: number;
  integer_arithmetic_ops: number;
  float_arithmetic_ops: number;
  pointer_dereferences: number;
  array_subscript_ops: number;
  branch_count: number;
  recursive_call_count: number;
  bitwise_ops: number;
  memory_allocation_ops: number;
  math_library_calls: number;
  global_variable_count: number;
  arithmetic_to_branch_ratio: number;
}

export interface InfluencingFeature {
  feature: string;
  importance: number;
}

export interface RecommendationResponse {
  id: string;
  source_file_id: string;
  recommended_level: OptimizationLevel;
  confidence_score: number;
  objective: Objective;
  explanation: string;
  features_extracted: FeatureVector;
  top_influencing_features: InfluencingFeature[];
  created_at: string;
}

export interface ModelStatusResponse {
  model_version: string;
  training_samples: number;
  test_samples: number;
  accuracy: number;
  f1_macro: number;
  confusion_matrix: number[][];
  labels: string[];
  feature_importances: Record<string, number>;
  training_duration_ms: number;
}

export interface SystemHealth {
  status: string;
  app_name: string;
  version: string;
  environment: string;
  timestamp: string;
  database: { status: string; engine: string };
  compiler: { status: string; path: string; version: string };
  docker: { status: string; socket: string };
}
