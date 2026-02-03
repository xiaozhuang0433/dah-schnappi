/**
 * API Service
 *
 * Handles all HTTP requests to the backend API.
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import type {
  User,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  UserConfig,
  GitLabConfigUpdate,
  GitHubConfigUpdate,
  SendMessageRequest,
  ChatResponse,
  GenerateWorklogRequest,
  GenerateWorklogResponse,
} from '@/types';

/**
 * API base URL
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

/**
 * Create axios instance with default config
 */
function createAxiosInstance(): AxiosInstance {
  const instance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000, // 60 seconds
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor: Add auth token
  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = localStorage.getItem('access_token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor: Handle errors
  instance.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (error.response?.status === 401) {
        // Unauthorized: Clear token and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return instance;
}

const api = createAxiosInstance();

/**
 * Authentication API
 */
export const authApi = {
  /**
   * Login
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login', data);
    // Store token and user
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  /**
   * Register
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/register', data);
    return response.data;
  },

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Logout
   */
  async logout(): Promise<void> {
    await api.post('/auth/logout');
    // Clear local storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Get stored user
   */
  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
};

/**
 * Configuration API
 */
export const configApi = {
  /**
   * Get user configuration
   */
  async getConfig(): Promise<UserConfig> {
    const response = await api.get<UserConfig>('/config');
    return response.data;
  },

  /**
   * Update configuration
   */
  async updateConfig(data: Partial<UserConfig>): Promise<{ status: string; message: string }> {
    const response = await api.put('/config', data);
    return response.data;
  },

  /**
   * Update GitLab configuration
   */
  async updateGitLabConfig(data: GitLabConfigUpdate): Promise<{ status: string; message: string }> {
    const response = await api.patch('/config/gitlab', data);
    return response.data;
  },

  /**
   * Update GitHub configuration
   */
  async updateGitHubConfig(data: GitHubConfigUpdate): Promise<{ status: string; message: string }> {
    const response = await api.patch('/config/github', data);
    return response.data;
  },

  /**
   * Delete configuration
   */
  async deleteConfig(): Promise<{ status: string; message: string }> {
    const response = await api.delete('/config');
    return response.data;
  },
};

/**
 * Chat API
 */
export const chatApi = {
  /**
   * Send chat message
   */
  async sendMessage(data: SendMessageRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/chat/message', data);
    return response.data;
  },

  /**
   * Generate work log directly
   */
  async generateWorklog(data: GenerateWorklogRequest): Promise<GenerateWorklogResponse> {
    const response = await api.post<GenerateWorklogResponse>('/chat/generate-worklog', data);
    return response.data;
  },

  /**
   * List available tools
   */
  async listTools(): Promise<{ tools: unknown[]; count: number }> {
    const response = await api.get('/chat/tools');
    return response.data;
  },

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; service: string; timestamp: string }> {
    const response = await api.get('/chat/health');
    return response.data;
  },
};

/**
 * System API
 */
export const systemApi = {
  /**
   * Health check
   */
  async healthCheck(): Promise<{
    status: string;
    version: string;
    timestamp: string;
    services: {
      database: string;
      cache: string;
      llm: string;
    };
  }> {
    const response = await api.get('/health');
    return response.data;
  },

  /**
   * Get version
   */
  async getVersion(): Promise<{ name: string; version: string; description: string }> {
    const response = await api.get('/version');
    return response.data;
  },
};

/**
 * Export all APIs
 */
export default api;
