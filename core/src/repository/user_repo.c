/**
 * @file user_repo.c
 * @brief User repository implementation (RBAC-aware)
 * @copyright Real Estate Management System
 */
#include "user_repo.h"
#include "db_connection.h"
#include "re_types.h"
#include <sqlite3.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#include "audit_repo.h"

/* ======================== USER CRUD ======================== */

int user_repo_create(const User* user, int* out_id) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "INSERT INTO users (role_id, username, password_hash, first_name, last_name, national_id, phone, failed_attempts, locked_until, is_disabled, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'));",
        &stmt
    );
    if (rc != 0) return rc;

    sqlite3_bind_int(stmt, 1, user->role_id);
    sqlite3_bind_text(stmt, 2, user->username, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, user->password_hash, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 4, user->first_name, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 5, user->last_name, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 6, user->national_id, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 7, user->phone, -1, SQLITE_TRANSIENT);
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

static void safe_copy(char* dest, const unsigned char* src, size_t max_len) {
    if (src) {
        strncpy(dest, (const char*)src, max_len - 1);
        dest[max_len - 1] = '\0';
    } else {
        dest[0] = '\0';
    }
}

static void map_row_to_user(sqlite3_stmt* stmt, User* out_user) {
    out_user->id = sqlite3_column_int(stmt, 0);
    out_user->role_id = sqlite3_column_int(stmt, 1);
    safe_copy(out_user->username, sqlite3_column_text(stmt, 2), sizeof(out_user->username));
    safe_copy(out_user->password_hash, sqlite3_column_text(stmt, 3), sizeof(out_user->password_hash));
    safe_copy(out_user->first_name, sqlite3_column_text(stmt, 4), sizeof(out_user->first_name));
    safe_copy(out_user->last_name, sqlite3_column_text(stmt, 5), sizeof(out_user->last_name));
    safe_copy(out_user->national_id, sqlite3_column_text(stmt, 6), sizeof(out_user->national_id));
    safe_copy(out_user->phone, sqlite3_column_text(stmt, 7), sizeof(out_user->phone));
    out_user->failed_attempts = sqlite3_column_int(stmt, 8);
    safe_copy(out_user->locked_until, sqlite3_column_text(stmt, 9), sizeof(out_user->locked_until));
    out_user->is_disabled = sqlite3_column_int(stmt, 10);
    safe_copy(out_user->role_name, sqlite3_column_text(stmt, 11), sizeof(out_user->role_name));
    safe_copy(out_user->created_at, sqlite3_column_text(stmt, 12), sizeof(out_user->created_at));
    safe_copy(out_user->updated_at, sqlite3_column_text(stmt, 13), sizeof(out_user->updated_at));
    safe_copy(out_user->last_login_at, sqlite3_column_text(stmt, 14), sizeof(out_user->last_login_at));
}

#define USER_SELECT_COLS \
    "u.id, u.role_id, u.username, u.password_hash, u.first_name, u.last_name, " \
    "u.national_id, u.phone, u.failed_attempts, u.locked_until, u.is_disabled, " \
    "r.name AS role_name, u.created_at, u.updated_at, u.last_login_at"

int user_repo_get_by_id(int id, User* out_user) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "SELECT " USER_SELECT_COLS " FROM users u JOIN roles r ON u.role_id = r.id WHERE u.id = ?;",
        &stmt
    );
    if (rc != 0) return rc;

    sqlite3_bind_int(stmt, 1, id);

    int step_rc = sqlite3_step(stmt);
    if (step_rc == SQLITE_ROW) {
        map_row_to_user(stmt, out_user);
        rc = 0;
    } else if (step_rc == SQLITE_DONE) {
        rc = RE_ERR_NOT_FOUND;
    } else {
        rc = db_map_error(step_rc);
    }
    sqlite3_finalize(stmt);
    return rc;
}

int user_repo_get_by_username(const char* username, User* out_user) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "SELECT " USER_SELECT_COLS " FROM users u JOIN roles r ON u.role_id = r.id WHERE u.username = ? AND u.is_disabled = 0;",
        &stmt
    );
    if (rc != 0) return rc;

    sqlite3_bind_text(stmt, 1, username, -1, SQLITE_TRANSIENT);

    int step_rc = sqlite3_step(stmt);
    if (step_rc == SQLITE_ROW) {
        map_row_to_user(stmt, out_user);
        rc = 0;
    } else if (step_rc == SQLITE_DONE) {
        rc = RE_ERR_NOT_FOUND;
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

int user_repo_update_last_login(int id) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare("UPDATE users SET last_login_at = datetime('now') WHERE id = ?;", &stmt);
    if (rc != 0) return rc;
    sqlite3_bind_int(stmt, 1, id);
    int step_rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return (step_rc == SQLITE_DONE) ? 0 : db_map_error(step_rc);
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

int user_repo_enable(int id) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare("UPDATE users SET is_disabled = 0 WHERE id = ?;", &stmt);
    if (rc != 0) return rc;
    sqlite3_bind_int(stmt, 1, id);
    int step_rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return (step_rc == SQLITE_DONE) ? 0 : db_map_error(step_rc);
}

int user_repo_update_role(int id, int new_role_id) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare("UPDATE users SET role_id = ?, updated_at = datetime('now') WHERE id = ?;", &stmt);
    if (rc != 0) return rc;
    sqlite3_bind_int(stmt, 1, new_role_id);
    sqlite3_bind_int(stmt, 2, id);
    int step_rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return (step_rc == SQLITE_DONE) ? 0 : db_map_error(step_rc);
}

int user_repo_update_password(int id, const char* new_password_hash) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare("UPDATE users SET password_hash = ?, updated_at = datetime('now') WHERE id = ?;", &stmt);
    if (rc != 0) return rc;
    sqlite3_bind_text(stmt, 1, new_password_hash, -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(stmt, 2, id);
    int step_rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return (step_rc == SQLITE_DONE) ? 0 : db_map_error(step_rc);
}

int user_repo_count_admins(int* count) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "SELECT COUNT(*) FROM users u JOIN roles r ON u.role_id = r.id WHERE r.name = 'admin' AND u.is_disabled = 0;",
        &stmt
    );
    if (rc != 0) return rc;
    int step_rc = sqlite3_step(stmt);
    if (step_rc == SQLITE_ROW) {
        *count = sqlite3_column_int(stmt, 0);
        rc = 0;
    } else {
        rc = db_map_error(step_rc);
    }
    sqlite3_finalize(stmt);
    return rc;
}

int user_repo_get_all(User* out_users, int max_count, int* out_count) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "SELECT " USER_SELECT_COLS " FROM users u JOIN roles r ON u.role_id = r.id ORDER BY u.id;",
        &stmt
    );
    if (rc != 0) return rc;
    
    int count = 0;
    while (sqlite3_step(stmt) == SQLITE_ROW && count < max_count) {
        map_row_to_user(stmt, &out_users[count]);
        count++;
    }
    *out_count = count;
    sqlite3_finalize(stmt);
    return 0;
}

/* ======================== SESSION MANAGEMENT ======================== */

int session_repo_create(int user_id, const char* token, const char* permissions_json) {
    // Delete old sessions for this user first
    sqlite3_stmt* del_stmt = NULL;
    int rc = db_prepare("DELETE FROM sessions WHERE user_id = ?;", &del_stmt);
    if (rc != 0) return rc;
    sqlite3_bind_int(del_stmt, 1, user_id);
    sqlite3_step(del_stmt);
    sqlite3_finalize(del_stmt);
    
    sqlite3_stmt* stmt = NULL;
    rc = db_prepare(
        "INSERT INTO sessions (user_id, token, permissions_cache, created_at, last_activity, expires_at) "
        "VALUES (?, ?, ?, datetime('now'), datetime('now'), datetime('now', '+30 minutes'));",
        &stmt
    );
    if (rc != 0) return rc;
    
    sqlite3_bind_int(stmt, 1, user_id);
    sqlite3_bind_text(stmt, 2, token, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, permissions_json, -1, SQLITE_TRANSIENT);
    
    int step_rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return (step_rc == SQLITE_DONE) ? 0 : db_map_error(step_rc);
}

int session_repo_validate(const char* token, Session* out_session) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "SELECT user_id, token, permissions_cache, (datetime('now') >= expires_at) FROM sessions "
        "WHERE token = ?;",
        &stmt
    );
    if (rc != 0) return rc;
    
    sqlite3_bind_text(stmt, 1, token, -1, SQLITE_TRANSIENT);
    
    int step_rc = sqlite3_step(stmt);
    int expired = 0;
    if (step_rc == SQLITE_ROW) {
        out_session->user_id = sqlite3_column_int(stmt, 0);
        safe_copy(out_session->token, sqlite3_column_text(stmt, 1), sizeof(out_session->token));
        safe_copy(out_session->permissions_cache, sqlite3_column_text(stmt, 2), sizeof(out_session->permissions_cache));
        expired = sqlite3_column_int(stmt, 3);
        rc = 0;
    } else {
        rc = RE_ERR_SESSION_EXPIRED;
    }
    sqlite3_finalize(stmt);
    
    if (rc == 0) {
        if (expired) {
            int uid = out_session->user_id;
            session_repo_delete(token);
            audit_repo_log(uid, "SESSION_TIMEOUT", "users", uid, "{}", "{\"status\":\"expired\"}", "127.0.0.1", "local");
            rc = RE_ERR_SESSION_EXPIRED;
        } else {
            // Rolling timeout: refresh activity and expiry
            sqlite3_stmt* upd = NULL;
            int urc = db_prepare(
                "UPDATE sessions SET last_activity = datetime('now'), expires_at = datetime('now', '+30 minutes') WHERE token = ?;",
                &upd
            );
            if (urc == 0) {
                sqlite3_bind_text(upd, 1, token, -1, SQLITE_TRANSIENT);
                sqlite3_step(upd);
                sqlite3_finalize(upd);
            }
        }
    }
    return rc;
}

int session_repo_delete(const char* token) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare("DELETE FROM sessions WHERE token = ?;", &stmt);
    if (rc != 0) return rc;
    sqlite3_bind_text(stmt, 1, token, -1, SQLITE_TRANSIENT);
    int step_rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return (step_rc == SQLITE_DONE) ? 0 : db_map_error(step_rc);
}

int session_repo_delete_by_user(int user_id) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare("DELETE FROM sessions WHERE user_id = ?;", &stmt);
    if (rc != 0) return rc;
    sqlite3_bind_int(stmt, 1, user_id);
    int step_rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return (step_rc == SQLITE_DONE) ? 0 : db_map_error(step_rc);
}

/* ======================== PERMISSION LOADING ======================== */

int permission_repo_get_by_role(int role_id, char* out_json, int max_len) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "SELECT p.name FROM permissions p "
        "JOIN role_permissions rp ON p.id = rp.permission_id "
        "WHERE rp.role_id = ? ORDER BY p.id;",
        &stmt
    );
    if (rc != 0) return rc;
    
    sqlite3_bind_int(stmt, 1, role_id);
    
    // Build JSON array manually
    int offset = 0;
    offset += snprintf(out_json + offset, (size_t)(max_len - offset), "[");
    
    int first = 1;
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        const char* pname = (const char*)sqlite3_column_text(stmt, 0);
        if (!first) {
            offset += snprintf(out_json + offset, (size_t)(max_len - offset), ",");
        }
        offset += snprintf(out_json + offset, (size_t)(max_len - offset), "\"%s\"", pname);
        first = 0;
    }
    
    snprintf(out_json + offset, (size_t)(max_len - offset), "]");
    
    sqlite3_finalize(stmt);
    return 0;
}

int permission_repo_get_ids_by_role(int role_id, int* out_ids, int max_count, int* out_count) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "SELECT permission_id FROM role_permissions WHERE role_id = ? ORDER BY permission_id;",
        &stmt
    );
    if (rc != 0) return rc;
    
    sqlite3_bind_int(stmt, 1, role_id);
    
    int count = 0;
    while (sqlite3_step(stmt) == SQLITE_ROW && count < max_count) {
        out_ids[count++] = sqlite3_column_int(stmt, 0);
    }
    *out_count = count;
    sqlite3_finalize(stmt);
    return 0;
}
