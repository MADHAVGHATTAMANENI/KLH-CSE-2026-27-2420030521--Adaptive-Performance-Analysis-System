import { create } from 'zustand';
import { Project, SourceFile } from '../types';
import * as api from '../services/api';

interface ProjectState {
  projects: Project[];
  activeProject: Project | null;
  files: SourceFile[];
  activeFileId: string | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchProjects: () => Promise<void>;
  selectProject: (projectId: string) => Promise<void>;
  createProject: (name: string, description?: string) => Promise<Project>;
  deleteProject: (projectId: string) => Promise<void>;
  fetchFiles: (projectId: string) => Promise<void>;
  setActiveFileId: (fileId: string | null) => void;
  createFile: (filename: string, content: string) => Promise<SourceFile>;
  deleteFile: (fileId: string) => Promise<void>;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  projects: [],
  activeProject: null,
  files: [],
  activeFileId: null,
  isLoading: false,
  error: null,

  fetchProjects: async () => {
    set({ isLoading: true, error: null });
    try {
      const projects = await api.getProjects();
      set({ projects, isLoading: false });
      if (projects.length > 0 && !get().activeProject) {
        await get().selectProject(projects[0].id);
      }
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch projects', isLoading: false });
    }
  },

  selectProject: async (projectId: string) => {
    const project = get().projects.find((p) => p.id === projectId) || null;
    set({ activeProject: project, activeFileId: null, files: [] });
    if (project) {
      await get().fetchFiles(project.id);
    }
  },

  createProject: async (name: string, description?: string) => {
    set({ isLoading: true });
    try {
      const newProject = await api.createProject(name, description);
      set((state) => ({
        projects: [newProject, ...state.projects],
        activeProject: newProject,
        isLoading: false,
      }));
      await get().fetchFiles(newProject.id);
      return newProject;
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
      throw err;
    }
  },

  deleteProject: async (projectId: string) => {
    await api.deleteProject(projectId);
    set((state) => {
      const updated = state.projects.filter((p) => p.id !== projectId);
      return {
        projects: updated,
        activeProject: updated.length > 0 ? updated[0] : null,
      };
    });
    if (get().activeProject) {
      await get().fetchFiles(get().activeProject!.id);
    }
  },

  fetchFiles: async (projectId: string) => {
    try {
      const files = await api.getProjectFiles(projectId);
      set({ files });
      if (files.length > 0 && !get().activeFileId) {
        set({ activeFileId: files[0].id });
      }
    } catch (err: any) {
      set({ error: err.message });
    }
  },

  setActiveFileId: (fileId: string | null) => {
    set({ activeFileId: fileId });
  },

  createFile: async (filename: string, content: string) => {
    const activeProject = get().activeProject;
    if (!activeProject) throw new Error('No active project');
    const newFile = await api.createSourceFile(activeProject.id, filename, content);
    set((state) => ({
      files: [newFile, ...state.files],
      activeFileId: newFile.id,
    }));
    return newFile;
  },

  deleteFile: async (fileId: string) => {
    await api.deleteSourceFile(fileId);
    set((state) => {
      const updated = state.files.filter((f) => f.id !== fileId);
      return {
        files: updated,
        activeFileId: updated.length > 0 ? updated[0].id : null,
      };
    });
  },
}));
