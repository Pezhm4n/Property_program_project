/**
 * @file exports.c
 * @brief DLL API Export Facades (RBAC-aware)
 * @copyright Real Estate Management System
 */
#include "re_core.h"
#include "re_types.h"
#include "services.h"
#include "db_connection.h"
#include "migrations.h"
#include <stdlib.h>
#include <string.h>

#if defined(_MSC_VER)
#define THREAD_LOCAL __declspec(thread)
#else
#define THREAD_LOCAL __thread
#endif

static THREAD_LOCAL int last_error = 0;

RE_API int re_get_api_version() {
    return 200; // 2.0.0 — RBAC release
}

RE_API int re_get_dll_version() {
    return 200; // 2.0.0
}

RE_API int re_get_last_error() {
    return last_error;
}

RE_API void re_free_string(char* str) {
    if (str) {
        free(str);
    }
}
RE_API int re_initialize(const char* db_path, const char* migrations_path) {
    int rc = db_init(db_path, 5000);
    if (rc != 0) {
        last_error = rc;
        return rc;
    }
    rc = migrations_run_all(migrations_path);
    if (rc != 0) {
        last_error = rc;
        return rc;
    }
    return 0;
}
RE_API void re_shutdown() {
    db_close();
}

RE_API int re_login(const char* request_json, char** response_json_out) {
    int rc = auth_login(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_logout(const char* request_json, char** response_json_out) {
    int rc = auth_logout(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_create_property(const char* request_json, char** response_json_out) {
    int rc = property_create(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_update_property(const char* request_json, char** response_json_out) {
    int rc = property_update(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_get_properties(const char* request_json, char** response_json_out) {
    int rc = property_get_all(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_get_property(const char* request_json, char** response_json_out) {
    int rc = property_get_by_id(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_archive_property(const char* request_json, char** response_json_out) {
    int rc = property_archive(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_restore_property(const char* request_json, char** response_json_out) {
    int rc = property_restore(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_get_report(const char* request_json, char** response_json_out) {
    int rc = report_generate(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_get_statistics(const char* request_json, char** response_json_out) {
    int rc = report_get_statistics(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_get_dashboard(const char* request_json, char** response_json_out) {
    int rc = report_get_dashboard(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_validate_session(const char* request_json, char** response_json_out) {
    int rc = auth_validate_session(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_ping(const char* request_json, char** response_json_out) {
    (void)request_json;
    if (!response_json_out) return RE_ERR_VALIDATION;
    char* resp = (char*)malloc(16);
    if (!resp) return RE_ERR_INTERNAL;
    strcpy(resp, "{\"status\":\"ok\"}");
    *response_json_out = resp;
    return 0;
}

RE_API int re_has_any_user(const char* request_json, char** response_json_out) {
    int rc = auth_has_any_user(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_create_initial_admin(const char* request_json, char** response_json_out) {
    int rc = auth_create_initial_admin(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_change_password(const char* request_json, char** response_json_out) {
    int rc = auth_change_password(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

/* ======================== USER MANAGEMENT API ======================== */

RE_API int re_get_users(const char* request_json, char** response_json_out) {
    int rc = user_management_get_all(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_create_user(const char* request_json, char** response_json_out) {
    int rc = user_management_create(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_change_user_role(const char* request_json, char** response_json_out) {
    int rc = user_management_change_role(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_reset_user_password(const char* request_json, char** response_json_out) {
    int rc = user_management_reset_password(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_toggle_user_status(const char* request_json, char** response_json_out) {
    int rc = user_management_toggle_status(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}

RE_API int re_log_audit(const char* request_json, char** response_json_out) {
    int rc = auth_log_audit(request_json, response_json_out);
    if (rc != 0) last_error = rc;
    return rc;
}
