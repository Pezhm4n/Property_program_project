/**
 * @file db_connection.c
 * @brief Implementation of database connection and lifecycle
 * @copyright Real Estate Management System
 */
#include "db_connection.h"
#include <stdio.h>
#include <stdlib.h>

// Singleton connection instance
static sqlite3* g_db = NULL;

int db_map_error(int sqlite_err) {
    switch (sqlite_err) {
        case SQLITE_OK:
        case SQLITE_DONE:
        case SQLITE_ROW:
            return 0; // RE_OK
        case SQLITE_CONSTRAINT:
        case SQLITE_CONSTRAINT_CHECK:
        case SQLITE_CONSTRAINT_NOTNULL:
            return -1; // RE_ERR_VALIDATION
        case SQLITE_CONSTRAINT_UNIQUE:
        case SQLITE_CONSTRAINT_PRIMARYKEY:
            return -3; // RE_ERR_DUPLICATE
        case SQLITE_BUSY:
        case SQLITE_LOCKED:
            return -10; // RE_ERR_BUSY
        case SQLITE_CORRUPT:
            return -11; // RE_ERR_CORRUPT
        case SQLITE_NOMEM:
            return -98; // RE_ERR_MEM
        default:
            return -7; // RE_ERR_DB
    }
}

int db_execute(const char* sql) {
    if (!g_db) return -99; // RE_ERR_INTERNAL

    int rc = SQLITE_BUSY;
    int retries[] = {100, 200, 400};
    for (int i = 0; i < 4; ++i) {
        char* err_msg = NULL;
        rc = sqlite3_exec(g_db, sql, 0, 0, &err_msg);
        if (rc != SQLITE_OK) {
            if (err_msg) sqlite3_free(err_msg);
        }
        if (rc != SQLITE_BUSY && rc != SQLITE_LOCKED) {
            break;
        }
        if (i < 3) {
            sqlite3_sleep(retries[i]);
        }
    }
    return db_map_error(rc);
}

int db_init(const char* db_path, int busy_timeout_ms) {
    if (g_db != NULL) {
        return 0; // Already initialized
    }
    
    int rc = sqlite3_open(db_path, &g_db);
    if (rc != SQLITE_OK) {
        return db_map_error(rc);
    }
    
    sqlite3_busy_timeout(g_db, busy_timeout_ms);
    
    // Enforce PRAGMA policies
    db_execute("PRAGMA journal_mode=WAL;");
    db_execute("PRAGMA foreign_keys=ON;");
    
    return 0;
}

void db_close() {
    if (g_db) {
        sqlite3_close(g_db);
        g_db = NULL;
    }
}

sqlite3* db_get_connection() {
    return g_db;
}

int db_prepare(const char* sql, sqlite3_stmt** out_stmt) {
    if (!g_db) return -99; // RE_ERR_INTERNAL
    
    int rc = SQLITE_BUSY;
    int retries[] = {100, 200, 400};
    for (int i = 0; i < 4; ++i) {
        rc = sqlite3_prepare_v2(g_db, sql, -1, out_stmt, 0);
        if (rc != SQLITE_BUSY && rc != SQLITE_LOCKED) {
            break;
        }
        if (i < 3) {
            sqlite3_sleep(retries[i]);
        }
    }
    return db_map_error(rc);
}

int db_begin_transaction() {
    return db_execute("BEGIN TRANSACTION;");
}

int db_commit_transaction() {
    return db_execute("COMMIT;");
}

int db_rollback_transaction() {
    return db_execute("ROLLBACK;");
}
