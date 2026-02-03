/**
 * Chat Message Store
 *
 * Provides CRUD operations for chat messages with user isolation.
 */

import { db } from './index';
import type { DBMessage, ChatMessage } from '@/types';

/**
 * ChatStore class for managing chat messages
 */
export class ChatStore {
  private userId: string;

  constructor(userId: string) {
    if (!userId) {
      throw new Error('userId is required for ChatStore');
    }
    this.userId = userId;
  }

  /**
   * Get all messages for the current user
   */
  async getAllMessages(): Promise<ChatMessage[]> {
    const messages = await db.messages
      .where('user_id')
      .equals(this.userId)
      .sortBy('created_at');

    return messages.map(this.dbMessageToChatMessage);
  }

  /**
   * Add a new message
   */
  async addMessage(
    role: ChatMessage['role'],
    content: string,
    metadata?: ChatMessage['metadata']
  ): Promise<number> {
    const dbMessage: DBMessage = {
      user_id: this.userId,
      role,
      content,
      metadata,
      created_at: new Date(),
    };

    const id = await db.messages.add(dbMessage);

    // Auto-trim old messages (keep last 1000)
    await db.trimOldMessages(this.userId, 1000);

    return id;
  }

  /**
   * Get messages with pagination
   */
  async getMessages(limit: number, offset: number = 0): Promise<ChatMessage[]> {
    const messages = await db.messages
      .where('user_id')
      .equals(this.userId)
      .reverse() // newest first
      .offset(offset)
      .limit(limit)
      .toArray();

    // Reverse to get chronological order
    return messages
      .reverse()
      .map(this.dbMessageToChatMessage);
  }

  /**
   * Get messages since a specific date
   */
  async getMessagesSince(since: Date): Promise<ChatMessage[]> {
    const messages = await db.messages
      .where('user_id')
      .equals(this.userId)
      .and(msg => msg.created_at >= since)
      .sortBy('created_at');

    return messages.map(this.dbMessageToChatMessage);
  }

  /**
   * Delete a specific message
   */
  async deleteMessage(messageId: number): Promise<boolean> {
    const message = await db.messages.get(messageId);

    if (!message || message.user_id !== this.userId) {
      return false; // Not found or doesn't belong to user
    }

    await db.messages.delete(messageId);
    return true;
  }

  /**
   * Delete all messages for the current user
   */
  async clearAllMessages(): Promise<number> {
    return await db.clearUserData(this.userId);
  }

  /**
   * Get message count
   */
  async getCount(): Promise<number> {
    return await db.getMessageCount(this.userId);
  }

  /**
   * Search messages by content
   */
  async searchMessages(query: string): Promise<ChatMessage[]> {
    const lowerQuery = query.toLowerCase();
    const allMessages = await this.getAllMessages();

    return allMessages.filter(msg =>
      msg.content.toLowerCase().includes(lowerQuery)
    );
  }

  /**
   * Update message metadata
   */
  async updateMessageMetadata(
    messageId: number,
    metadata: ChatMessage['metadata']
  ): Promise<boolean> {
    const message = await db.messages.get(messageId);

    if (!message || message.user_id !== this.userId) {
      return false;
    }

    await db.messages.update(messageId, { metadata });
    return true;
  }

  /**
   * Get last N messages (for context)
   */
  async getLastMessages(count: number = 10): Promise<ChatMessage[]> {
    const messages = await db.messages
      .where('user_id')
      .equals(this.userId)
      .reverse() // newest first
      .limit(count)
      .toArray();

    return messages.reverse().map(this.dbMessageToChatMessage);
  }

  /**
   * Export messages as JSON
   */
  async exportMessages(): Promise<string> {
    const messages = await this.getAllMessages();
    return JSON.stringify(messages, null, 2);
  }

  /**
   * Import messages from JSON
   */
  async importMessages(jsonData: string): Promise<number> {
    const messages = JSON.parse(jsonData) as ChatMessage[];

    let imported = 0;
    for (const message of messages) {
      await this.addMessage(
        message.role,
        message.content,
        message.metadata
      );
      imported++;
    }

    return imported;
  }

  /**
   * Convert DBMessage to ChatMessage
   */
  private dbMessageToChatMessage(dbMessage: DBMessage): ChatMessage {
    return {
      id: String(dbMessage.id!),
      role: dbMessage.role,
      content: dbMessage.content,
      metadata: dbMessage.metadata,
      created_at: dbMessage.created_at.toISOString(),
    };
  }
}

/**
 * Create a ChatStore instance for a user
 */
export function createChatStore(userId: string): ChatStore {
  return new ChatStore(userId);
}

/**
 * Global chat store instance (set after login)
 */
let globalChatStore: ChatStore | null = null;

/**
 * Get the global chat store
 */
export function getChatStore(): ChatStore | null {
  return globalChatStore;
}

/**
 * Set the global chat store
 */
export function setChatStore(store: ChatStore): void {
  globalChatStore = store;
}

/**
 * Clear the global chat store
 */
export function clearChatStore(): void {
  globalChatStore = null;
}
