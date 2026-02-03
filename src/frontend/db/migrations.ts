/**
 * Database Migrations
 *
 * Handles database schema versioning and migrations.
 */

import { db, DB_VERSION, DB_NAME } from './index';

export interface Migration {
  version: number;
  name: string;
  migrate: (db: typeof db) => Promise<void>;
}

/**
 * Migration: Add user_id index for better query performance
 */
const migration_1_add_user_index: Migration = {
  version: 1,
  name: 'add_user_id_index',
  migrate: async (database) => {
    // This is already handled in the schema definition
    // Future migrations can add new tables or indexes here
    console.log('Migration 1: User ID index already defined in schema');
  },
};

/**
 * Future migration examples:
 *
 * const migration_2_add_sessions_table: Migration = {
 *   version: 2,
 *   name: 'add_sessions_table',
 *   migrate: async (database) => {
 *     // Add a new sessions table
 *     database.version(2).stores({
 *       messages: '++id, user_id, created_at',
 *       sessions: 'userId, lastActive',
 *     });
 *   },
 * };
 */

/**
 * All migrations in order
 */
const migrations: Migration[] = [
  migration_1_add_user_index,
  // Add future migrations here
];

/**
 * Run pending migrations
 */
export async function runMigrations(): Promise<void> {
  const currentVersion = await getCurrentVersion();

  console.log(`Current DB version: ${currentVersion}`);
  console.log(`Expected DB version: ${DB_VERSION}`);

  if (currentVersion >= DB_VERSION) {
    console.log('Database is up to date');
    return;
  }

  console.log('Running migrations...');

  for (const migration of migrations) {
    if (migration.version > currentVersion) {
      console.log(`Running migration: ${migration.name}`);
      try {
        await migration.migrate(db);
        console.log(`Migration ${migration.name} completed`);
      } catch (error) {
        console.error(`Migration ${migration.name} failed:`, error);
        throw error;
      }
    }
  }

  console.log('All migrations completed');
}

/**
 * Get current database version
 */
async function getCurrentVersion(): Promise<number> {
  try {
    // Dexie doesn't have a direct API to get current version
    // We'll check the version from the database name or IndexedDB
    const databases = await indexedDB.databases();
    const dbInfo = databases.find(d => d.name === DB_NAME);

    if (dbInfo && dbInfo.version) {
      return dbInfo.version;
    }

    return 0;
  } catch {
    return 0;
  }
}

/**
 * Reset database (for development/debugging)
 */
export async function resetDatabase(): Promise<void> {
  console.warn('Resetting database...');

  await db.delete();
  console.log('Database deleted. Reloading page...');

  // Reload page to reinitialize database
  window.location.reload();
}
