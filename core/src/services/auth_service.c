/**
 * @file auth_service.c
 * @brief Authentication service implementation
 * @copyright Real Estate Management System
 */
#include "services.h"
#include "re_types.h"
#include "user_repo.h"
#include "audit_repo.h"
#include <cjson/cJSON.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>

int auth_login(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    
    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    
    cJSON* username_item = cJSON_GetObjectItem(root, "username");
    cJSON* password_item = cJSON_GetObjectItem(root, "password");
    if (!username_item || !password_item) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }
    
    const char* username = username_item->valuestring;
    const char* password = password_item->valuestring;
    
    User user;
    memset(&user, 0, sizeof(User));
    
    int rc = user_repo_get_by_username(username, &user);
    if (rc != 0) {
        cJSON_Delete(root);
        return RE_ERR_AUTH;
    }
    
    // Check if locked
    if (strlen(user.locked_until) > 0) {
        time_t now = time(NULL);
        int yr = 0, mo = 0, dy = 0, hr = 0, mn = 0, sc = 0;
        if (sscanf(user.locked_until, "%d-%d-%d %d:%d:%d", &yr, &mo, &dy, &hr, &mn, &sc) == 6) {
            struct tm lock_tm = {0};
            lock_tm.tm_year = yr - 1900;
            lock_tm.tm_mon = mo - 1;
            lock_tm.tm_mday = dy;
            lock_tm.tm_hour = hr;
            lock_tm.tm_min = mn;
            lock_tm.tm_sec = sc;
            time_t lock_time = mktime(&lock_tm);
            if (now < lock_time) {
                cJSON_Delete(root);
                return RE_ERR_LOCKED;
            }
        }
    }
    
    // Check password
    if (strcmp(user.password_hash, password) != 0) {
        int attempts = user.failed_attempts + 1;
        char lock_str[30] = {0};
        if (attempts >= 5) {
            time_t lock_end = time(NULL) + 300; // 5 mins
            struct tm* tm_info = localtime(&lock_end);
            strftime(lock_str, sizeof(lock_str), "%Y-%m-%d %H:%M:%S", tm_info);
            user_repo_update_failed_attempts(user.id, attempts, lock_str);
            audit_repo_log(user.id, "LOCKOUT", "users", user.id, "{}", "{\"status\":\"locked\"}", "127.0.0.1", "local");
        } else {
            user_repo_update_failed_attempts(user.id, attempts, "");
        }
        cJSON_Delete(root);
        return RE_ERR_AUTH;
    }
    
    // Reset failed attempts
    user_repo_update_failed_attempts(user.id, 0, "");
    
    // Log audit
    audit_repo_log(user.id, "LOGIN", "users", user.id, "{}", "{\"status\":\"success\"}", "127.0.0.1", "local");
    
    cJSON* resp = cJSON_CreateObject();
    cJSON_AddStringToObject(resp, "token", "session-token-123456");
    cJSON_AddStringToObject(resp, "role", user.role);
    cJSON_AddStringToObject(resp, "username", user.username);
    cJSON_AddStringToObject(resp, "first_name", user.first_name);
    cJSON_AddStringToObject(resp, "last_name", user.last_name);
    
    char* resp_str = cJSON_PrintUnformatted(resp);
    *res = strdup(resp_str);
    free(resp_str);
    cJSON_Delete(resp);
    cJSON_Delete(root);
    
    return 0;
}

int auth_logout(const char* req, char** res) {
    (void)req;
    audit_repo_log(1, "LOGOUT", "users", 1, "{}", "{\"status\":\"success\"}", "127.0.0.1", "local");
    if (res) *res = strdup("{\"status\":\"ok\"}");
    return 0;
}

int auth_validate_session(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    cJSON* token = cJSON_GetObjectItem(root, "token");
    if (!token || strlen(token->valuestring) == 0) {
        cJSON_Delete(root);
        return RE_ERR_AUTH;
    }
    cJSON_Delete(root);
    *res = strdup("{\"status\":\"valid\"}");
    return 0;
}

#include "db_connection.h"

int auth_has_any_user(const char* req, char** res) {
    (void)req;
    if (!res) return RE_ERR_VALIDATION;
    
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare("SELECT COUNT(*) FROM users;", &stmt);
    int count = 0;
    if (rc == 0) {
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            count = sqlite3_column_int(stmt, 0);
        }
        sqlite3_finalize(stmt);
    }
    
    cJSON* resp = cJSON_CreateObject();
    cJSON_AddBoolToObject(resp, "has_users", count > 0);
    char* resp_str = cJSON_PrintUnformatted(resp);
    *res = strdup(resp_str);
    free(resp_str);
    cJSON_Delete(resp);
    return 0;
}

int auth_create_initial_admin(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    
    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    
    cJSON* username_item = cJSON_GetObjectItem(root, "username");
    cJSON* password_item = cJSON_GetObjectItem(root, "password");
    if (!username_item || !password_item) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }
    
    const char* username = username_item->valuestring;
    const char* password = password_item->valuestring;
    
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare("SELECT COUNT(*) FROM users;", &stmt);
    int count = 0;
    if (rc == 0) {
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            count = sqlite3_column_int(stmt, 0);
        }
        sqlite3_finalize(stmt);
    }
    if (count > 0) {
        cJSON_Delete(root);
        return RE_ERR_FORBIDDEN;
    }
    
    User admin_user;
    memset(&admin_user, 0, sizeof(User));
    strncpy(admin_user.username, username, sizeof(admin_user.username) - 1);
    strncpy(admin_user.password_hash, password, sizeof(admin_user.password_hash) - 1);
    strcpy(admin_user.first_name, "مدیر");
    strcpy(admin_user.last_name, "سیستم");
    strcpy(admin_user.role, "admin");
    strcpy(admin_user.national_id, "0012345678");
    strcpy(admin_user.phone, "09123456789");
    admin_user.failed_attempts = 0;
    admin_user.is_disabled = 0;
    
    int new_id = 0;
    rc = user_repo_create(&admin_user, &new_id);
    if (rc != 0) {
        cJSON_Delete(root);
        return rc;
    }
    
    audit_repo_log(new_id, "WIZARD_CREATE_ADMIN", "users", new_id, "{}", "{\"status\":\"created\"}", "127.0.0.1", "local");
    
    cJSON_Delete(root);
    *res = strdup("{\"status\":\"created\"}");
    return 0;
}

int auth_change_password(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    
    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    
    cJSON* username_item = cJSON_GetObjectItem(root, "username");
    cJSON* current_pw_item = cJSON_GetObjectItem(root, "current_password");
    cJSON* new_pw_item = cJSON_GetObjectItem(root, "new_password");
    if (!username_item || !current_pw_item || !new_pw_item) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }
    
    const char* username = username_item->valuestring;
    const char* current_pw = current_pw_item->valuestring;
    const char* new_pw = new_pw_item->valuestring;
    
    if (strlen(new_pw) < 6) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }
    
    User user;
    memset(&user, 0, sizeof(User));
    int rc = user_repo_get_by_username(username, &user);
    if (rc != 0) {
        cJSON_Delete(root);
        return RE_ERR_NOT_FOUND;
    }
    
    if (strcmp(user.password_hash, current_pw) != 0) {
        cJSON_Delete(root);
        return RE_ERR_AUTH;
    }
    
    sqlite3_stmt* stmt = NULL;
    rc = db_prepare("UPDATE users SET password_hash = ? WHERE id = ?;", &stmt);
    if (rc != 0) {
        cJSON_Delete(root);
        return rc;
    }
    
    sqlite3_bind_text(stmt, 1, new_pw, -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(stmt, 2, user.id);
    
    int step_rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    
    if (step_rc != SQLITE_DONE) {
        cJSON_Delete(root);
        return db_map_error(step_rc);
    }
    
    audit_repo_log(user.id, "CHANGE_PASSWORD", "users", user.id, "{}", "{\"status\":\"success\"}", "127.0.0.1", "local");
    
    cJSON_Delete(root);
    *res = strdup("{\"status\":\"success\"}");
    return 0;
}

