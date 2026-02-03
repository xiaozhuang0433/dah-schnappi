/**
 * Chat Store
 *
 * Manages chat state using Zustand with IndexedDB persistence.
 */

import { create } from 'zustand';
import type { ChatMessage, Attachment } from '@/types';
import { chatApi } from '@/services/api';
import { getChatStore } from '@/db';

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  isSending: boolean;
  error: string | null;
  attachments: Attachment[];

  // Actions
  loadMessages: () => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  generateWorklog: (timeRange?: string) => Promise<void>;
  clearMessages: () => Promise<void>;
  addMessage: (message: ChatMessage) => void;
  clearError: () => void;
  clearAttachments: () => void;
}

export const useChatStore = create<ChatState>()((set, get) => ({
  messages: [],
  isLoading: false,
  isSending: false,
  error: null,
  attachments: [],

  loadMessages: async () => {
    set({ isLoading: true, error: null });

    try {
      const chatStore = getChatStore();
      if (!chatStore) {
        set({ isLoading: false });
        return;
      }

      const messages = await chatStore.getAllMessages();

      set({
        messages,
        isLoading: false,
      });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to load messages';
      set({
        error: message,
        isLoading: false,
      });
    }
  },

  sendMessage: async (content: string) => {
    set({ isSending: true, error: null, attachments: [] });

    try {
      const chatStore = getChatStore();
      if (!chatStore) {
        throw new Error('Not logged in');
      }

      // Add user message to store
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      };

      await chatStore.addMessage('user', content);

      set((state) => ({
        messages: [...state.messages, userMessage],
      }));

      // Send to API
      const response = await chatApi.sendMessage({ message: content });

      // Add assistant message to store
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.content,
        metadata: response.metadata,
        created_at: new Date().toISOString(),
      };

      await chatStore.addMessage('assistant', response.content, response.metadata);

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        isSending: false,
        attachments: response.attachments || [],
      }));
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to send message';
      set({
        error: message,
        isSending: false,
      });
      throw error;
    }
  },

  generateWorklog: async (timeRange?: string) => {
    set({ isSending: true, error: null, attachments: [] });

    try {
      const chatStore = getChatStore();
      if (!chatStore) {
        throw new Error('Not logged in');
      }

      // Add user message
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: timeRange ? `生成${timeRange}的工作日志` : '生成工作日志',
        created_at: new Date().toISOString(),
      };

      await chatStore.addMessage('user', userMessage.content);

      set((state) => ({
        messages: [...state.messages, userMessage],
      }));

      // Call API
      const response = await chatApi.generateWorklog({
        time_range: timeRange,
      });

      // Add assistant message
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.content,
        metadata: response.metadata,
        created_at: new Date().toISOString(),
      };

      await chatStore.addMessage('assistant', response.content, response.metadata);

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        isSending: false,
        attachments: response.attachments || [],
      }));
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to generate worklog';
      set({
        error: message,
        isSending: false,
      });
      throw error;
    }
  },

  clearMessages: async () => {
    try {
      const chatStore = getChatStore();
      if (!chatStore) {
        return;
      }

      await chatStore.clearAllMessages();

      set({
        messages: [],
        attachments: [],
      });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to clear messages';
      set({ error: message });
      throw error;
    }
  },

  addMessage: (message: ChatMessage) => {
    set((state) => ({
      messages: [...state.messages, message],
    }));
  },

  clearError: () => {
    set({ error: null });
  },

  clearAttachments: () => {
    set({ attachments: [] });
  },
}));
