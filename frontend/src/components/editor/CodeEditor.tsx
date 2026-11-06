import React, { useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { Save, Check } from 'lucide-react';
import { useEditorStore } from '../../stores/useEditorStore';

export const CodeEditor: React.FC = () => {
  const { fileId, filename, content, isDirty, isSaving, updateContent, saveFile } = useEditorStore();

  const isCpp = filename.endsWith('.cpp') || filename.endsWith('.hpp');
  const language = isCpp ? 'cpp' : 'c';

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 's') {
        e.preventDefault();
        saveFile();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [saveFile]);

  if (!fileId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-canvas text-slate-500 font-mono text-xs">
        Select a source file or load a preset algorithm from the sidebar to begin.
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-3.5rem)] bg-canvas">
      {/* Editor Sub-Header */}
      <div className="h-10 border-b border-borderSubtle bg-surface/80 px-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="font-mono text-xs text-slate-200">{filename}</span>
          {isDirty && (
            <span className="w-2 h-2 rounded-full bg-amber-400" title="Unsaved changes" />
          )}
        </div>

        <button
          onClick={() => saveFile()}
          disabled={!isDirty || isSaving}
          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs font-mono transition ${
            isDirty
              ? 'bg-cyan-600 hover:bg-cyan-500 text-white'
              : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          {isSaving ? (
            <span className="animate-spin text-xs">...</span>
          ) : isDirty ? (
            <>
              <Save className="w-3.5 h-3.5" />
              <span>Save (Cmd+S)</span>
            </>
          ) : (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span>Saved</span>
            </>
          )}
        </button>
      </div>

      {/* Monaco Editor Container */}
      <div className="flex-1 overflow-hidden">
        <Editor
          height="100%"
          language={language}
          value={content}
          theme="vs-dark"
          onChange={(val) => updateContent(val || '')}
          options={{
            fontSize: 13,
            fontFamily: 'JetBrains Mono, Menlo, monospace',
            minimap: { enabled: true },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            bracketPairColorization: { enabled: true },
            lineNumbers: 'on',
            renderWhitespace: 'selection',
          }}
        />
      </div>
    </div>
  );
};
