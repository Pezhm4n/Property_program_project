/**
 * @file user_repo.c
 * @brief User repository implementation
 * @copyright Real Estate Management System
 */
#include "user_repo.h"
#include "db_connection.h"
#include <sqlite3.h>
#include <string.h>

int user_repo_create(const User* user, int* out_id) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "INSERT INTO users (username, password_hash, first_name, last_name, national_id, phone, role, failed_attempts, locked_until, is_disabled, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'));",
        &stmt
    );
    if (rc != 0) return rc;

    sqlite3_bind_text(stmt, 1, user->username, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, user->password_hash, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, user->first_name, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 4, user->last_name, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 5, user->national_id, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 6, user->phone, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 7, user->role, -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(stmt, 8, user->failed_attempts);
    if (strlen(user->locked_until) > 0) {
        sqlite3_bind_text(stmt, 9, user->locked_until, -1, SQLITE_TRANSIENT);
    } else {
        sqlite3_bind_null(stmt, 9);
    }
    sqlite3_bind_int(stmt, 10, user->is_disabled);

    int step_rc = sqlite3_step(stmt);
    if (step_rc == SQLITE_DONE && out_id) {
        *out_id = (int)sqlite3_last_insert_rowid(db_get_connection());
    }
    sqlite3_finalize(stmt);

    if (step_rc != SQLITE_DONE) {
        return db_map_error(step_rc);
    }
    return 0;
}

static void map_row_to_user(sqlite3_stmt* stmt, User* out_user) {
    out_user->id = sqlite3_column_int(stmt, 0);
    strcpy(out_user->username, (const char*)sqlite3_column_text(stmt, 1));
    strcpy(out_user->password_hash, (const char*)sqlite3_column_text(stmt, 2));
    strcpy(out_user->first_name, (const char*)sqlite3_column_text(stmt, 3));
    strcpy(out_user->last_name, (const char*)sqlite3_column_text(stmt, 4));
    strcpy(out_user->national_id, (const char*)sqlite3_column_text(stmt, 5));
    strcpy(out_user->phone, (const char*)sqlite3_column_text(stmt, 6));
    strcpy(out_user->role, (const char*)sqlite3_column_text(stmt, 7));
    out_user->failed_attempts = sqlite3_column_int(stmt, 8);
    const char* locked = (const char*)sqlite3_column_text(stmt, 9);
    if (locked) {
        strcpy(out_user->locked_until, locked);
    } else {
        out_user->locked_until[0] = '\0';
    }
    out_user->is_disabled = sqlite3_column_int(stmt, 10);
}

int user_repo_get_by_id(int id, User* out_user) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "SELECT id, username, password_hash, first_name, last_name, national_id, phone, role, failed_attempts, locked_until, is_disabled FROM users WHERE id = ?;",
        &stmt
    );
    if (rc != 0) return rc;

    sqlite3_bind_int(stmt, 1, id);

    int step_rc = sqlite3_step(stmt);
    if (step_rc == SQLITE_ROW) {
        map_row_to_user(stmt, out_user);
        rc = 0;
    } else if (step_rc == SQLITE_DONE) {
        rc = -2; // RE_ERR_NOT_FOUND
    } else {
        rc = db_map_error(step_rc);
    }
    sqlite3_finalize(stmt);
    return rc;
}

int user_repo_get_by_username(const char* username, User* out_user) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "SELECT id, username, password_hash, first_name, last_name, national_id, phone, role, failed_attempts, locked_until, is_disabled FROM users WHERE username = ? AND is_disabled = 0;",
        &stmt
    );
    if (rc != 0) return rc;

    sqlite3_bind_text(stmt, 1, username, -1, SQLITE_TRANSIENT);

    int step_rc = sqlite3_step(stmt);
    if (step_rc == SQLITE_ROW) {
        map_row_to_user(stmt, out_user);
        rc = 0;
    } else if (step_rc == SQLITE_DONE) {
        rc = -2; // RE_ERR_NOT_FOUND
    } else {
        rc = db_map_error(step_rc);
    }
    sqlite3_finalize(stmt);
    return rc;
}

int user_repo_update_failed_attempts(int id, int attempts, const char* locked_until) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare("UPDATE users SET failed_attempts = ?, locked_until = ? WHERE id = ?;", &stmt);
    if (rc != 0) return rc;

    sqlite3_bind_int(stmt, 1, attempts);
    if (locked_until && strlen(locked_until) > 0) {
        sqlite3_bind_text(stmt, 2, locked_until, -1, SQLITE_TRANSIENT);
    } else {
        sqlite3_bind_null(stmt, 2);
    }
    sqlite3_bind_int(stmt, 3, id);

    int step_rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    if (step_rc != SQLITE_DONE) {
        return db_map_error(step_rc);
    }
    return 0;
}

int user_repo_soft_delete(int id) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare("UPDATE users SET is_disabled = 1 WHERE id = ?;", &stmt);
    if (rc != 0) return rc;

    sqlite3_bind_int(stmt, 1, id);

    int step_rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    if (step_rc != SQLITE_DONE) {
        return db_map_error(step_rc);
    }
    return 0;
}
