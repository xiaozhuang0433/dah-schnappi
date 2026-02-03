/**
 * TypeScript Type Definitions
 */

// ==================== User & Auth ====================

export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ==================== Configuration ====================

export interface UserConfig {
  id: number;
  user_id: number;
  gitlab_url?: string;
  gitlab_token?: string;
  github_username?: string;
  github_token?: string;
  default_platform: 'gitlab' | 'github';
  include_branches: boolean;
  created_at: string;
  updated_at: string;
}

export interface GitLabConfigUpdate {
  gitlab_url: string;
  gitlab_token: string;
}

export interface GitHubConfigUpdate {
  github_username: string;
  github_token: string;
}

// ==================== Chat ====================

export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  metadata?: {
    model?: string;
    usage?: {
      input_tokens: number;
      output_tokens: number;
      total_tokens: number;
    };
    processing_time?: number;
    tool_calls?: ToolCall[];
    error?: string;
  };
  created_at: string;
}

export interface ToolCall {
  name: string;
  arguments: Record<string, unknown>;
  result?: unknown;
  error?: string;
}

export interface Attachment {
  type: 'markdown' | 'text' | 'json' | 'pdf';
  filename: string;
  content: string; // Base64 encoded
  size?: number;
}

export interface ChatResponse {
  content: string;
  role: MessageRole;
  metadata?: ChatMessage['metadata'];
  attachments?: Attachment[];
}

export interface SendMessageRequest {
  message: string;
  conversation_id?: string;
}

// ==================== Database (IndexedDB) ====================

export interface DBMessage {
  id?: number;
  user_id: string;
  role: MessageRole;
  content: string;
  metadata?: ChatMessage['metadata'];
  created_at: Date;
}

export interface DBSession {
  userId: string;
  messages: DBMessage[];
  lastActive: Date;
}

// ==================== API Response ====================

export interface ApiResponse<T = unknown> {
  data?: T;
  error?: string;
  message?: string;
  status: string;
}

// ==================== Work Log ====================

export interface GenerateWorklogRequest {
  since_date?: string;
  until_date?: string;
  branch?: string;
  project_id?: string;
  include_stats?: boolean;
  time_range?: string;
}

export interface WorkLogMetadata {
  total_commits: number;
  start_date: string;
  end_date: string;
  projects: string[];
}

export interface GenerateWorklogResponse {
  content: string;
  metadata?: WorkLogMetadata;
  attachments?: Attachment[];
}
