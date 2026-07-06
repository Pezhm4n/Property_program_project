/**
 * @file audit_repo.c
 * @brief Audit repository implementation
 * @copyright Real Estate Management System
 */
#include "audit_repo.h"
#include "db_connection.h"
#include <sqlite3.h>
#include <stddef.h>

int audit_repo_log(int actor_id, const char* action, const char* entity, int entity_id, const char* old_vals, const char* new_vals, const char* ip, const char* machine) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "INSERT INTO audit_logs (actor_id, action, entity, entity_id, old_values_json, new_values_json, ip, machine, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'));",
        &stmt
    );
    if (rc != 0) return rc;

    if (actor_id > 0) {
        sqlite3_bind_int(stmt, 1, actor_id);
    } else {
        sqlite3_bind_null(stmt, 1);
    }
    sqlite3_bind_text(stmt, 2, action, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, entity, -1, SQLITE_TRANSIENT);
    if (entity_id > 0) {
        sqlite3_bind_int(stmt, 4, entity_id);
    } else {
        sqlite3_bind_null(stmt, 4);
    }
    sqlite3_bind_text(stmt, 5, old_vals ? old_vals : "{}", -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 6, new_vals ? new_vals : "{}", -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 7, ip ? ip : "127.0.0.1", -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 8, machine ? machine : "local", -1, SQLITE_TRANSIENT);

    int step_rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    if (step_rc != SQLITE_DONE) {
        return db_map_error(step_rc);
    }
    return 0; // RE_OK
}
