/**
 * Configuration Store
 *
 * Manages user configuration state using Zustand.
 */

import { create } from 'zustand';
import type { UserConfig, GitLabConfigUpdate, GitHubConfigUpdate } from '@/types';
import { configApi } from '@/services/api';

interface ConfigState {
  config: UserConfig | null;
  isLoading: boolean;
  error: string | null;
  isConfigured: boolean;

  // Actions
  fetchConfig: () => Promise<void>;
  updateGitLabConfig: (data: GitLabConfigUpdate) => Promise<void>;
  updateGitHubConfig: (data: GitHubConfigUpdate) => Promise<void>;
  deleteConfig: () => Promise<void>;
  clearError: () => void;
}

export const useConfigStore = create<ConfigState>()((set, get) => ({
  config: null,
  isLoading: false,
  error: null,
  isConfigured: false,

  fetchConfig: async () => {
    set({ isLoading: true, error: null });
    try {
      const config = await configApi.getConfig();

      set({
        config,
        isLoading: false,
        isConfigured: true,
      });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to fetch configuration';
      set({
        error: message,
        isLoading: false,
        isConfigured: false,
      });
    }
  },

  updateGitLabConfig: async (data: GitLabConfigUpdate) => {
    set({ isLoading: true, error: null });
    try {
      await configApi.updateGitLabConfig(data);

      // Refresh config
      await get().fetchConfig();
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to update GitLab configuration';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  updateGitHubConfig: async (data: GitHubConfigUpdate) => {
    set({ isLoading: true, error: null });
    try {
      await configApi.updateGitHubConfig(data);

      // Refresh config
      await get().fetchConfig();
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to update GitHub configuration';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  deleteConfig: async () => {
    set({ isLoading: true, error: null });
    try {
      await configApi.deleteConfig();

      set({
        config: null,
        isLoading: false,
        isConfigured: false,
      });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to delete configuration';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));
