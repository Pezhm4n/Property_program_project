/**
 * @file migrations.h
 * @brief Database schema migration engine
 * @copyright Real Estate Management System
 */
#ifndef MIGRATIONS_H
#define MIGRATIONS_H

/**
 * @brief Reads the generated manifest and applies all pending migrations in order.
 * Wraps each migration in an atomic transaction (BEGIN/COMMIT).
 * Creates schema_migrations table if it does not exist.
 * @param migrations_dir The base directory path containing the .sql files.
 * @return 0 on success, negative error code on failure.
 */
int migrations_run_all(const char* migrations_dir);

#endif // MIGRATIONS_H
