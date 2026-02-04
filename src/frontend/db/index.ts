/**
 * Database Module
 *
 * Exports all database-related functionality.
 */
import Dexie, { Table } from 'dexie';
import type { DBMessage } from '@/types';

// Database configuration
export const DB_NAME = 'DahSchnappiDB';
export const DB_VERSION = 1;

/**
 * WorkLog Database Class
 * Extends Dexie to define the database schema
 */
export class WorkLogDB extends Dexie {
  messages!: Table<DBMessage, number>;

  constructor() {
    super(DB_NAME);

    this.version(DB_VERSION).stores({
      messages: '++id, user_id, created_at',
    });
  }

  /**
   * Get message count for a specific user
   */
  async getMessageCount(userId: string): Promise<number> {
    return await this.messages.where('user_id').equals(userId).count();
  }

  /**
   * Clear all data for a specific user
   */
  async clearUserData(userId: string): Promise<number> {
    return await this.messages.where('user_id').equals(userId).delete();
  }

  /**
   * Trim old messages for a user (keep only N most recent)
   */
  async trimOldMessages(userId: string, keepCount: number): Promise<void> {
    const allMessages = await this.messages
      .where('user_id')
      .equals(userId)
      .reverse()
      .toArray();

    if (allMessages.length > keepCount) {
      const toDelete = allMessages.slice(keepCount);
      await this.messages.bulkDelete(toDelete.map(m => m.id!));
    }
  }
}

// Global database instance
export const db = new WorkLogDB();

/**
 * Initialize the database
 */
export async function initDB(): Promise<void> {
  await db.open();
  console.log(`Database ${DB_NAME} v${DB_VERSION} initialized`);
}

/**
 * Close the database connection
 */
export async function closeDB(): Promise<void> {
  await db.close();
  console.log(`Database ${DB_NAME} closed`);
}

// Re-export chat store and migrations
export {
  ChatStore,
  createChatStore,
  getChatStore,
  setChatStore,
  clearChatStore,
} from './chatStore';
export { runMigrations, resetDatabase } from './migrations';
