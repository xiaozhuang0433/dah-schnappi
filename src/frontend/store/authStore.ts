/**
 * Authentication Store
 *
 * Manages authentication state using Zustand.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types';
import { authApi } from '@/services/api';
import { setChatStore, clearChatStore, createChatStore } from '@/db';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login({ username, password });

          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
          });

          // Initialize chat store for this user
          const chatStore = createChatStore(String(response.user.id));
          setChatStore(chatStore);
        } catch (error: unknown) {
          const message = error instanceof Error ? error.message : 'Login failed';
          set({
            error: message,
            isLoading: false,
            isAuthenticated: false,
            user: null,
          });
          throw error;
        }
      },

      register: async (username: string, email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.register({ username, email, password });

          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
          });

          // Initialize chat store for this user
          const chatStore = createChatStore(String(response.user.id));
          setChatStore(chatStore);
        } catch (error: unknown) {
          const message = error instanceof Error ? error.message : 'Registration failed';
          set({
            error: message,
            isLoading: false,
          });
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true, error: null });
        try {
          await authApi.logout();

          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });

          // Clear chat store
          clearChatStore();
        } catch (error: unknown) {
          const message = error instanceof Error ? error.message : 'Logout failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      checkAuth: async () => {
        set({ isLoading: true });

        try {
          if (authApi.isAuthenticated()) {
            const user = authApi.getStoredUser();
            if (user) {
              set({
                user,
                isAuthenticated: true,
                isLoading: false,
              });

              // Initialize chat store
              const chatStore = createChatStore(String(user.id));
              setChatStore(chatStore);
            } else {
              set({
                user: null,
                isAuthenticated: false,
                isLoading: false,
              });
            }
          } else {
            set({
              user: null,
              isAuthenticated: false,
              isLoading: false,
            });
          }
        } catch {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
