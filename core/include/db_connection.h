/**
 * @file db_connection.h
 * @brief Database connection and transaction lifecycle management
 * @copyright Real Estate Management System
 */
#ifndef DB_CONNECTION_H
#define DB_CONNECTION_H

#include <sqlite3.h>

/**
 * @brief Connection Lifecycle
 * Application Start -> db_init() -> Repositories -> Services -> db_close() -> Application Exit
 */

/**
 * @brief Initialize the global database connection.
 * @param db_path Path to the SQLite database file.
 * @param busy_timeout_ms Timeout in milliseconds for SQLITE_BUSY errors.
 * @return 0 on success, negative error code on failure.
 */
int db_init(const char* db_path, int busy_timeout_ms);

/**
 * @brief Close the global database connection and cleanup resources.
 */
void db_close();

/**
 * @brief Retrieve the global singleton connection.
 * @return sqlite3* pointer to the connection.
 */
sqlite3* db_get_connection();

/**
 * @brief Execute a raw SQL statement (useful for PRAGMA or BEGIN/COMMIT).
 * @param sql The SQL string to execute.
 * @return 0 on success, negative error code on failure.
 */
int db_execute(const char* sql);

/**
 * @brief Prepare an SQL statement to prevent SQL injection.
 * @param sql The parameterized SQL string.
 * @param out_stmt Pointer to receive the prepared statement.
 * @return 0 on success, negative error code on failure.
 */
int db_prepare(const char* sql, sqlite3_stmt** out_stmt);

/**
 * @brief Transaction Helpers
 */
int db_begin_transaction();
int db_commit_transaction();
int db_rollback_transaction();

/**
 * @brief Maps native SQLite error codes to standard project error codes.
 * @param sqlite_err The SQLite return code.
 * @return Project error code (e.g. -1 for Validation, -7 for DB error).
 */
int db_map_error(int sqlite_err);

#endif // DB_CONNECTION_H
