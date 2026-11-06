import React, { useState } from 'react';
import { FileCode, Plus, Trash2, Sparkles } from 'lucide-react';
import { useProjectStore } from '../../stores/useProjectStore';
import { useEditorStore } from '../../stores/useEditorStore';

const SAMPLE_TEMPLATES: Record<string, string> = {
  'matrix_mult.c': `// Matrix Multiplication Benchmark (Heavy Nested Loops)
#include <stdio.h>
#define N 256

double A[N][N], B[N][N], C[N][N];

int main() {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            A[i][j] = i * 0.5 + j;
            B[i][j] = j * 0.2 - i;
            C[i][j] = 0.0;
        }
    }

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            for (int k = 0; k < N; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }

    printf("Matrix mult complete: C[N-1][N-1] = %f\\n", C[N-1][N-1]);
    return 0;
}
`,
  'quicksort.c': `// QuickSort Recursive Benchmark (Control Flow & Branching)
#include <stdio.h>

void swap(int* a, int* b) {
    int t = *a;
    *a = *b;
    *b = t;
}

int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = (low - 1);
    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return (i + 1);
}

void quicksort(int arr[], int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quicksort(arr, low, pi - 1);
        quicksort(arr, pi + 1, high);
    }
}

int main() {
    int arr[10000];
    for (int i = 0; i < 10000; i++) arr[i] = 10000 - i;
    quicksort(arr, 0, 9999);
    printf("QuickSort complete: arr[0] = %d\\n", arr[0]);
    return 0;
}
`,
  'prime_sieve.c': `// Sieve of Eratosthenes (Array Access & Bitwise Checking)
#include <stdio.h>
#include <stdbool.h>
#define MAX 200000

bool is_prime[MAX + 1];

int main() {
    for (int i = 0; i <= MAX; i++) is_prime[i] = true;
    for (int p = 2; p * p <= MAX; p++) {
        if (is_prime[p]) {
            for (int i = p * p; i <= MAX; i += p) {
                is_prime[i] = false;
            }
        }
    }
    int count = 0;
    for (int p = 2; p <= MAX; p++) {
        if (is_prime[p]) count++;
    }
    printf("Total primes up to %d: %d\\n", MAX, count);
    return 0;
}
`,
};

export const Sidebar: React.FC = () => {
  const { files, activeFileId, setActiveFileId, createFile, deleteFile } = useProjectStore();
  const { loadFile } = useEditorStore();
  const [newFileName, setNewFileName] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const handleSelectFile = (fileId: string) => {
    setActiveFileId(fileId);
    loadFile(fileId);
  };

  const handleCreateFile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFileName.trim()) return;
    const name = newFileName.endsWith('.c') || newFileName.endsWith('.cpp')
      ? newFileName
      : `${newFileName}.c`;
    
    const file = await createFile(name, '// CompilerX Source File\n#include <stdio.h>\n\nint main() {\n    printf("Hello from CompilerX!\\n");\n    return 0;\n}\n');
    setNewFileName('');
    setIsCreating(false);
    handleSelectFile(file.id);
  };

  const handleLoadTemplate = async (templateName: string) => {
    const code = SAMPLE_TEMPLATES[templateName];
    const file = await createFile(templateName, code);
    handleSelectFile(file.id);
  };

  return (
    <aside className="w-64 border-r border-borderSubtle bg-surface flex flex-col h-[calc(100vh-3.5rem)] select-none">
      {/* Files Header */}
      <div className="p-3 border-b border-borderSubtle flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">
          Project Files
        </span>
        <button
          onClick={() => setIsCreating(true)}
          className="p-1 rounded text-slate-400 hover:text-cyan-400 hover:bg-slate-800 transition"
          title="Add File"
        >
          <Plus className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Inline Create Input */}
      {isCreating && (
        <form onSubmit={handleCreateFile} className="p-2 border-b border-borderSubtle">
          <input
            type="text"
            placeholder="filename.c"
            value={newFileName}
            onChange={(e) => setNewFileName(e.target.value)}
            autoFocus
            className="w-full bg-elevated border border-cyan-500 rounded px-2 py-1 text-xs text-slate-100 focus:outline-none"
          />
        </form>
      )}

      {/* File List */}
      <div className="flex-1 overflow-y-auto py-2">
        {files.length === 0 ? (
          <div className="px-4 py-8 text-center text-xs text-slate-500 font-mono">
            No source files. Create one or load a preset below.
          </div>
        ) : (
          files.map((file) => (
            <div
              key={file.id}
              onClick={() => handleSelectFile(file.id)}
              className={`group px-3 py-2 text-xs flex items-center justify-between cursor-pointer transition ${
                activeFileId === file.id
                  ? 'bg-cyan-500/10 text-cyan-400 border-l-2 border-cyan-400'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <div className="flex items-center space-x-2 truncate">
                <FileCode className="w-3.5 h-3.5 shrink-0" />
                <span className="truncate font-mono">{file.filename}</span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteFile(file.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 text-slate-500 hover:text-rose-400 rounded transition"
                title="Delete file"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Preset Algorithms / Templates */}
      <div className="p-3 border-t border-borderSubtle bg-slate-950/40">
        <div className="flex items-center space-x-1.5 text-xs text-slate-400 font-mono mb-2">
          <Sparkles className="w-3 h-3 text-cyan-400" />
          <span>Load Benchmarks</span>
        </div>
        <div className="space-y-1">
          {Object.keys(SAMPLE_TEMPLATES).map((template) => (
            <button
              key={template}
              onClick={() => handleLoadTemplate(template)}
              className="w-full text-left text-xs font-mono text-slate-400 hover:text-cyan-300 hover:bg-slate-800/60 px-2 py-1 rounded transition truncate"
            >
              + {template}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
};
