/**
 * @file auth_service.c
 * @brief Authentication service implementation (RBAC-aware)
 * @copyright Real Estate Management System
 */
#include "services.h"
#include "re_types.h"
#include "user_repo.h"
#include "audit_repo.h"
#include "db_connection.h"
#include <cjson/cJSON.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>

/* ======================== SECURE TOKEN GENERATION ======================== */

#ifdef _WIN32
#include <windows.h>
#include <wincrypt.h>
#endif

/**
 * Generate a cryptographically random 256-bit hex token (64 characters).
 * Uses Windows CryptoAPI (CryptGenRandom) or /dev/urandom on POSIX.
 */
static void generate_secure_token(char* out_token, size_t max_len) {
    unsigned char bytes[32]; // 256 bits
    memset(bytes, 0, sizeof(bytes));

#ifdef _WIN32
    HCRYPTPROV hProv = 0;
    if (CryptAcquireContextA(&hProv, NULL, NULL, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT)) {
        CryptGenRandom(hProv, 32, bytes);
        CryptReleaseContext(hProv, 0);
    } else {
        // Fallback: use time-based entropy
        srand((unsigned)time(NULL));
        for (int i = 0; i < 32; i++) {
            bytes[i] = (unsigned char)(rand() % 256);
        }
    }
#else
    FILE* f = fopen("/dev/urandom", "rb");
    if (f) {
        fread(bytes, 1, 32, f);
        fclose(f);
    } else {
        srand((unsigned)time(NULL));
        for (int i = 0; i < 32; i++) {
            bytes[i] = (unsigned char)(rand() % 256);
        }
    }
#endif

    for (int i = 0; i < 32 && (size_t)(i * 2 + 2) < max_len; i++) {
        sprintf(out_token + (i * 2), "%02x", bytes[i]);
    }
    out_token[64] = '\0';
}

static void trim_whitespace(char* str) {
    if (!str) return;
    char* start = str;
    while (*start == ' ' || *start == '\t' || *start == '\r' || *start == '\n') {
        start++;
    }
    if (start != str) {
        memmove(str, start, strlen(start) + 1);
    }
    size_t len = strlen(str);
    while (len > 0 && (str[len - 1] == ' ' || str[len - 1] == '\t' || str[len - 1] == '\r' || str[len - 1] == '\n')) {
        str[len - 1] = '\0';
        len--;
    }
}

static int validate_phone(const char* phone) {
    if (!phone || strlen(phone) != 11) return 0;
    if (phone[0] != '0' || phone[1] != '9') return 0;
    for (int i = 0; i < 11; ++i) {
        if (phone[i] < '0' || phone[i] > '9') return 0;
    }
    return 1;
}

static int validate_national_id(const char* nid) {
    if (!nid || strlen(nid) != 10) return 0;
    
    int all_same = 1;
    for (int i = 1; i < 10; ++i) {
        if (nid[i] != nid[0]) {
            all_same = 0;
            break;
        }
    }
    if (all_same) return 0;

    for (int i = 0; i < 10; ++i) {
        if (nid[i] < '0' || nid[i] > '9') return 0;
    }

    int sum = 0;
    for (int i = 0; i < 9; ++i) {
        sum += (nid[i] - '0') * (10 - i);
    }
    int rem = sum % 11;
    int control = nid[9] - '0';
    if (rem < 2) {
        return control == rem;
    } else {
        return control == (11 - rem);
    }
}

static int validate_username(const char* username, int is_initial_creation) {
    if (!username || strlen(username) < 3 || strlen(username) > 50) return 0;
    for (int i = 0; username[i] != '\0'; ++i) {
        char c = username[i];
        if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-')) {
            return 0;
        }
    }
    const char* reserved[] = {"administrator", "root", "system"};
    int reserved_count = 3;
    char lower_uname[64];
    size_t len = strlen(username);
    if (len >= sizeof(lower_uname)) return 0;
    for (size_t i = 0; i < len; ++i) {
        char c = username[i];
        if (c >= 'A' && c <= 'Z') {
            lower_uname[i] = c + 32;
        } else {
            lower_uname[i] = c;
        }
    }
    lower_uname[len] = '\0';
    for (int i = 0; i < reserved_count; ++i) {
        if (strcmp(lower_uname, reserved[i]) == 0) {
            return 0;
        }
    }
    if (!is_initial_creation && strcmp(lower_uname, "admin") == 0) {
        return 0;
    }
    return 1;
}

/* ======================== PERMISSION VALIDATION ======================== */

/**
 * Central permission validation function.
 * Validates the token, checks session expiry (30-min rolling timeout),
 * refreshes the session, and verifies the user has the required permission.
 *
 * @param token         The session token from the request
 * @param required_perm The PermissionEnum value required (0 = no permission check, just validate session)
 * @param out_user_id   Output: the authenticated user's ID
 * @return RE_OK on success, RE_ERR_SESSION_EXPIRED, RE_ERR_FORBIDDEN, or other error
 */
int validate_session_and_permission(const char* token, PermissionEnum required_perm, int* out_user_id) {
    if (!token || strlen(token) == 0) return RE_ERR_AUTH;

    Session session;
    memset(&session, 0, sizeof(Session));

    int rc = session_repo_validate(token, &session);
    if (rc != 0) return rc; // RE_ERR_SESSION_EXPIRED if expired

    *out_user_id = session.user_id;

    // If no specific permission is required, just validate the session
    if (required_perm == 0) return RE_OK;

    // Check permission from the cached permissions JSON
    // Parse the permissions_cache JSON array and check for the required permission name
    const char* perm_name = NULL;
    switch (required_perm) {
        case PERM_VIEW_PROPERTIES:       perm_name = "VIEW_PROPERTIES"; break;
        case PERM_CREATE_PROPERTY:       perm_name = "CREATE_PROPERTY"; break;
        case PERM_EDIT_PROPERTY:         perm_name = "EDIT_PROPERTY"; break;
        case PERM_DELETE_PROPERTY:       perm_name = "DELETE_PROPERTY"; break;
        case PERM_ARCHIVE_PROPERTY:      perm_name = "ARCHIVE_PROPERTY"; break;
        case PERM_RESTORE_PROPERTY:      perm_name = "RESTORE_PROPERTY"; break;
        case PERM_VIEW_REPORTS:          perm_name = "VIEW_REPORTS"; break;
        case PERM_VIEW_FINANCIAL_REPORTS: perm_name = "VIEW_FINANCIAL_REPORTS"; break;
        case PERM_MANAGE_USERS:          perm_name = "MANAGE_USERS"; break;
        case PERM_CHANGE_USER_ROLE:      perm_name = "CHANGE_USER_ROLE"; break;
        case PERM_RESET_PASSWORD:        perm_name = "RESET_PASSWORD"; break;
        case PERM_BACKUP_DATABASE:       perm_name = "BACKUP_DATABASE"; break;
        case PERM_RESTORE_DATABASE:      perm_name = "RESTORE_DATABASE"; break;
        case PERM_VIEW_SETTINGS:         perm_name = "VIEW_SETTINGS"; break;
        case PERM_VIEW_AUDIT_LOG:        perm_name = "VIEW_AUDIT_LOG"; break;
        case PERM_EXPORT_REPORTS:        perm_name = "EXPORT_REPORTS"; break;
        default: return RE_ERR_FORBIDDEN;
    }

    // Search for the permission name in the cached JSON array string
    if (strstr(session.permissions_cache, perm_name) != NULL) {
        return RE_OK;
    }

    return RE_ERR_FORBIDDEN;
}

/* ======================== AUTH ENDPOINTS ======================== */

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

    if (strlen(username) >= 50 || strlen(password) >= 255) {
        cJSON_Delete(root);
        return RE_ERR_AUTH;
    }

    User user;
    memset(&user, 0, sizeof(User));

    int rc = user_repo_get_by_username(username, &user);
    if (rc != 0) {
        audit_repo_log(0, "LOGIN_FAILED", "users", 0, "{}", "{\"status\":\"failed\"}", "127.0.0.1", "local");
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
                audit_repo_log(user.id, "LOGIN_FAILED", "users", user.id, "{}", "{\"status\":\"locked\"}", "127.0.0.1", "local");
                memset(&user, 0, sizeof(User));
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
        audit_repo_log(user.id, "LOGIN_FAILED", "users", user.id, "{}", "{\"status\":\"failed\"}", "127.0.0.1", "local");
        memset(&user, 0, sizeof(User));
        cJSON_Delete(root);
        return RE_ERR_AUTH;
    }

    // Reset failed attempts
    user_repo_update_failed_attempts(user.id, 0, "");

    // Update last login timestamp
    user_repo_update_last_login(user.id);

    // Load permissions for this user's role from the database
    char perms_json[2048] = {0};
    rc = permission_repo_get_by_role(user.role_id, perms_json, sizeof(perms_json));
    if (rc != 0) {
        memset(&user, 0, sizeof(User));
        cJSON_Delete(root);
        return RE_ERR_INTERNAL;
    }

    // Single active session policy: Delete previous sessions of this user
    session_repo_delete_by_user(user.id);

    // Generate secure 256-bit token
    char token[65] = {0};
    generate_secure_token(token, sizeof(token));

    // Create session in database
    rc = session_repo_create(user.id, token, perms_json);
    if (rc != 0) {
        memset(&user, 0, sizeof(User));
        cJSON_Delete(root);
        return RE_ERR_INTERNAL;
    }

    // Log audit
    audit_repo_log(user.id, "LOGIN_SUCCESS", "users", user.id, "{}", "{\"status\":\"success\"}", "127.0.0.1", "local");

    // Build response with token, role, and permissions
    cJSON* resp = cJSON_CreateObject();
    cJSON_AddStringToObject(resp, "token", token);
    cJSON_AddNumberToObject(resp, "user_id", user.id);
    cJSON_AddStringToObject(resp, "username", user.username);
    cJSON_AddStringToObject(resp, "role", user.role_name);
    cJSON_AddNumberToObject(resp, "role_id", user.role_id);
    cJSON_AddStringToObject(resp, "first_name", user.first_name);
    cJSON_AddStringToObject(resp, "last_name", user.last_name);

    // Add permissions array
    cJSON* perms_arr = cJSON_Parse(perms_json);
    if (perms_arr) {
        cJSON_AddItemToObject(resp, "permissions", perms_arr);
    }

    char* resp_str = cJSON_PrintUnformatted(resp);
    *res = strdup(resp_str);
    free(resp_str);
    cJSON_Delete(resp);
    cJSON_Delete(root);
    memset(&user, 0, sizeof(User));
    return 0;
}

int auth_logout(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;

    cJSON* root = cJSON_Parse(req);
    if (!root) {
        *res = strdup("{\"status\":\"ok\"}");
        return 0;
    }

    cJSON* token_item = cJSON_GetObjectItem(root, "token");
    if (token_item && token_item->valuestring) {
        // Get user_id before deleting session for audit
        Session session;
        memset(&session, 0, sizeof(Session));
        if (session_repo_validate(token_item->valuestring, &session) == 0) {
            audit_repo_log(session.user_id, "LOGOUT", "users", session.user_id, "{}", "{\"status\":\"success\"}", "127.0.0.1", "local");
        }
        session_repo_delete(token_item->valuestring);
    }
    cJSON_Delete(root);
    *res = strdup("{\"status\":\"ok\"}");
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

    int user_id = 0;
    int rc = validate_session_and_permission(token->valuestring, 0, &user_id);
    cJSON_Delete(root);

    if (rc != 0) return rc;

    *res = strdup("{\"status\":\"valid\"}");
    return 0;
}

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

    if (strlen(username) >= 50 || strlen(password) >= 255) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }

    if (!validate_username(username, 1)) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }
    if (strlen(password) < 6) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }

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
    trim_whitespace(admin_user.username);
    strcpy(admin_user.first_name, "\xd9\x85\xd8\xaf\xdb\x8c\xd8\xb1"); // مدیر
    strcpy(admin_user.last_name, "\xd8\xb3\xdb\x8c\xd8\xb3\xd8\xaa\xd9\x85"); // سیستم
    admin_user.role_id = 1; // admin role
    strcpy(admin_user.national_id, "0012345678");
    strcpy(admin_user.phone, "09123456789");
    admin_user.failed_attempts = 0;
    admin_user.is_disabled = 0;

    int new_id = 0;
    rc = user_repo_create(&admin_user, &new_id);
    if (rc != 0) {
        memset(&admin_user, 0, sizeof(User));
        cJSON_Delete(root);
        return rc;
    }

    audit_repo_log(new_id, "WIZARD_CREATE_ADMIN", "users", new_id, "{}", "{\"status\":\"created\"}", "127.0.0.1", "local");

    memset(&admin_user, 0, sizeof(User));
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

    if (strlen(username) >= 50 || strlen(current_pw) >= 255 || strlen(new_pw) >= 255) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }

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
        memset(&user, 0, sizeof(User));
        cJSON_Delete(root);
        return RE_ERR_AUTH;
    }

    rc = user_repo_update_password(user.id, new_pw);
    if (rc != 0) {
        memset(&user, 0, sizeof(User));
        cJSON_Delete(root);
        return rc;
    }

    audit_repo_log(user.id, "PASSWORD_CHANGED", "users", user.id, "{}", "{\"status\":\"success\"}", "127.0.0.1", "local");

    memset(&user, 0, sizeof(User));
    cJSON_Delete(root);
    *res = strdup("{\"status\":\"success\"}");
    return 0;
}

/* ======================== USER MANAGEMENT ENDPOINTS ======================== */

int user_management_get_all(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;

    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    cJSON* token_item = cJSON_GetObjectItem(root, "token");
    if (!token_item) { cJSON_Delete(root); return RE_ERR_AUTH; }

    int actor_id = 0;
    int rc = validate_session_and_permission(token_item->valuestring, PERM_MANAGE_USERS, &actor_id);
    cJSON_Delete(root);
    if (rc != 0) return rc;

    User users[200];
    int count = 0;
    rc = user_repo_get_all(users, 200, &count);
    if (rc != 0) return rc;

    cJSON* resp = cJSON_CreateObject();
    cJSON* arr = cJSON_CreateArray();
    for (int i = 0; i < count; i++) {
        cJSON* item = cJSON_CreateObject();
        cJSON_AddNumberToObject(item, "id", users[i].id);
        cJSON_AddStringToObject(item, "username", users[i].username);
        cJSON_AddStringToObject(item, "first_name", users[i].first_name);
        cJSON_AddStringToObject(item, "last_name", users[i].last_name);
        cJSON_AddStringToObject(item, "role", users[i].role_name);
        cJSON_AddNumberToObject(item, "role_id", users[i].role_id);
        cJSON_AddBoolToObject(item, "is_disabled", users[i].is_disabled);
        cJSON_AddStringToObject(item, "created_at", users[i].created_at);
        cJSON_AddStringToObject(item, "last_login_at", users[i].last_login_at);
        cJSON_AddStringToObject(item, "phone", users[i].phone);
        cJSON_AddItemToArray(arr, item);
    }
    cJSON_AddItemToObject(resp, "users", arr);

    char* resp_str = cJSON_PrintUnformatted(resp);
    *res = strdup(resp_str);
    free(resp_str);
    cJSON_Delete(resp);
    memset(users, 0, sizeof(users));
    return 0;
}

int user_management_create(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;

    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    cJSON* token_item = cJSON_GetObjectItem(root, "token");
    if (!token_item) { cJSON_Delete(root); return RE_ERR_AUTH; }

    int actor_id = 0;
    int rc = validate_session_and_permission(token_item->valuestring, PERM_MANAGE_USERS, &actor_id);
    if (rc != 0) { cJSON_Delete(root); return rc; }

    cJSON* user_obj = cJSON_GetObjectItem(root, "user");
    if (!user_obj) { cJSON_Delete(root); return RE_ERR_VALIDATION; }

    cJSON* u_name = cJSON_GetObjectItem(user_obj, "username");
    cJSON* u_pass = cJSON_GetObjectItem(user_obj, "password");
    cJSON* u_fname = cJSON_GetObjectItem(user_obj, "first_name");
    cJSON* u_lname = cJSON_GetObjectItem(user_obj, "last_name");
    cJSON* u_nid = cJSON_GetObjectItem(user_obj, "national_id");
    cJSON* u_phone = cJSON_GetObjectItem(user_obj, "phone");
    cJSON* u_role_id = cJSON_GetObjectItem(user_obj, "role_id");

    if (!u_name || !u_pass || !u_fname || !u_lname || !u_nid || !u_phone || !u_role_id) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }

    User new_user;
    memset(&new_user, 0, sizeof(User));
    strncpy(new_user.username, u_name->valuestring, sizeof(new_user.username) - 1);
    strncpy(new_user.password_hash, u_pass->valuestring, sizeof(new_user.password_hash) - 1);
    strncpy(new_user.first_name, u_fname->valuestring, sizeof(new_user.first_name) - 1);
    strncpy(new_user.last_name, u_lname->valuestring, sizeof(new_user.last_name) - 1);
    strncpy(new_user.national_id, u_nid->valuestring, sizeof(new_user.national_id) - 1);
    strncpy(new_user.phone, u_phone->valuestring, sizeof(new_user.phone) - 1);
    new_user.role_id = u_role_id->valueint;
    new_user.is_disabled = 0;

    // Hardening Trim & Validations
    trim_whitespace(new_user.username);
    trim_whitespace(new_user.first_name);
    trim_whitespace(new_user.last_name);
    trim_whitespace(new_user.national_id);
    trim_whitespace(new_user.phone);

    if (!validate_username(new_user.username, 0)) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }
    if (!validate_phone(new_user.phone)) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }
    if (!validate_national_id(new_user.national_id)) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }
    if (strlen(new_user.first_name) == 0 || strlen(new_user.last_name) == 0) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }
    if (strlen(new_user.password_hash) < 6) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }

    int new_id = 0;
    rc = user_repo_create(&new_user, &new_id);
    if (rc != 0) {
        memset(&new_user, 0, sizeof(User));
        cJSON_Delete(root);
        return rc;
    }

    audit_repo_log(actor_id, "CREATE_USER", "users", new_id, "{}", "{\"status\":\"created\"}", "127.0.0.1", "local");

    memset(&new_user, 0, sizeof(User));
    cJSON_Delete(root);

    cJSON* resp = cJSON_CreateObject();
    cJSON_AddStringToObject(resp, "status", "created");
    cJSON_AddNumberToObject(resp, "id", new_id);
    char* resp_str = cJSON_PrintUnformatted(resp);
    *res = strdup(resp_str);
    free(resp_str);
    cJSON_Delete(resp);
    return 0;
}

int user_management_change_role(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;

    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    cJSON* token_item = cJSON_GetObjectItem(root, "token");
    cJSON* target_id_item = cJSON_GetObjectItem(root, "user_id");
    cJSON* new_role_id_item = cJSON_GetObjectItem(root, "new_role_id");
    if (!token_item || !target_id_item || !new_role_id_item) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }

    int actor_id = 0;
    int rc = validate_session_and_permission(token_item->valuestring, PERM_CHANGE_USER_ROLE, &actor_id);
    if (rc != 0) { cJSON_Delete(root); return rc; }

    int target_id = target_id_item->valueint;
    int new_role_id = new_role_id_item->valueint;

    // Anti-lockout: if demoting from admin, check if this is the last admin
    User target_user;
    memset(&target_user, 0, sizeof(User));
    rc = user_repo_get_by_id(target_id, &target_user);
    if (rc != 0) { cJSON_Delete(root); return rc; }

    // Check if the user is currently admin and we're changing away from admin role
    if (target_user.role_id == 1 && new_role_id != 1) {
        int admin_count = 0;
        user_repo_count_admins(&admin_count);
        if (admin_count <= 1) {
            memset(&target_user, 0, sizeof(User));
            cJSON_Delete(root);
            return RE_ERR_LAST_ADMIN;
        }
    }

    rc = user_repo_update_role(target_id, new_role_id);
    memset(&target_user, 0, sizeof(User));
    if (rc != 0) { cJSON_Delete(root); return rc; }

    // Invalidate target user's sessions so they get new permissions on next login
    session_repo_delete_by_user(target_id);

    audit_repo_log(actor_id, "CHANGE_ROLE", "users", target_id, "{}", "{\"status\":\"changed\"}", "127.0.0.1", "local");

    cJSON_Delete(root);
    *res = strdup("{\"status\":\"success\"}");
    return 0;
}

int user_management_reset_password(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;

    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    cJSON* token_item = cJSON_GetObjectItem(root, "token");
    cJSON* target_id_item = cJSON_GetObjectItem(root, "user_id");
    cJSON* new_pw_item = cJSON_GetObjectItem(root, "new_password");
    if (!token_item || !target_id_item || !new_pw_item) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }

    int actor_id = 0;
    int rc = validate_session_and_permission(token_item->valuestring, PERM_RESET_PASSWORD, &actor_id);
    if (rc != 0) { cJSON_Delete(root); return rc; }

    int target_id = target_id_item->valueint;
    const char* new_pw = new_pw_item->valuestring;

    if (strlen(new_pw) < 6) { cJSON_Delete(root); return RE_ERR_VALIDATION; }

    rc = user_repo_update_password(target_id, new_pw);
    if (rc != 0) { cJSON_Delete(root); return rc; }

    audit_repo_log(actor_id, "RESET_PASSWORD", "users", target_id, "{}", "{\"status\":\"reset\"}", "127.0.0.1", "local");

    cJSON_Delete(root);
    *res = strdup("{\"status\":\"success\"}");
    return 0;
}

int user_management_toggle_status(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;

    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    cJSON* token_item = cJSON_GetObjectItem(root, "token");
    cJSON* target_id_item = cJSON_GetObjectItem(root, "user_id");
    cJSON* enable_item = cJSON_GetObjectItem(root, "enable");
    if (!token_item || !target_id_item || !enable_item) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }

    int actor_id = 0;
    int rc = validate_session_and_permission(token_item->valuestring, PERM_MANAGE_USERS, &actor_id);
    if (rc != 0) { cJSON_Delete(root); return rc; }

    int target_id = target_id_item->valueint;
    int enable = cJSON_IsTrue(enable_item);

    if (!enable) {
        // Safeguard: User cannot disable/deactivate themselves
        if (target_id == actor_id) {
            cJSON_Delete(root);
            return RE_ERR_LAST_ADMIN; // Maps to self lockout error
        }

        // Anti-lockout: cannot disable the last admin
        User target_user;
        memset(&target_user, 0, sizeof(User));
        rc = user_repo_get_by_id(target_id, &target_user);
        if (rc != 0) { cJSON_Delete(root); return rc; }

        if (target_user.role_id == 1) {
            int admin_count = 0;
            user_repo_count_admins(&admin_count);
            if (admin_count <= 1) {
                memset(&target_user, 0, sizeof(User));
                cJSON_Delete(root);
                return RE_ERR_LAST_ADMIN;
            }
        }
        memset(&target_user, 0, sizeof(User));

        rc = user_repo_soft_delete(target_id);
        session_repo_delete_by_user(target_id);
        audit_repo_log(actor_id, "USER_DISABLED", "users", target_id, "{}", "{\"status\":\"disabled\"}", "127.0.0.1", "local");
    } else {
        rc = user_repo_enable(target_id);
        audit_repo_log(actor_id, "USER_ENABLED", "users", target_id, "{}", "{\"status\":\"enabled\"}", "127.0.0.1", "local");
    }

    if (rc != 0) { cJSON_Delete(root); return rc; }

    cJSON_Delete(root);
    *res = strdup("{\"status\":\"success\"}");
    return 0;
}

int auth_log_audit(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;

    cJSON* token_item = cJSON_GetObjectItem(root, "token");
    cJSON* action_item = cJSON_GetObjectItem(root, "action");
    cJSON* entity_item = cJSON_GetObjectItem(root, "entity");
    cJSON* entity_id_item = cJSON_GetObjectItem(root, "entity_id");
    cJSON* old_vals_item = cJSON_GetObjectItem(root, "old_values");
    cJSON* new_vals_item = cJSON_GetObjectItem(root, "new_values");

    if (!token_item || !action_item || !entity_item) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }

    int actor_id = 0;
    // Just validate session (0 as required_perm)
    int rc = validate_session_and_permission(token_item->valuestring, 0, &actor_id);
    if (rc != 0) {
        cJSON_Delete(root);
        return rc;
    }

    int entity_id = entity_id_item ? entity_id_item->valueint : 0;
    const char* old_vals = old_vals_item ? old_vals_item->valuestring : "{}";
    const char* new_vals = new_vals_item ? new_vals_item->valuestring : "{}";

    rc = audit_repo_log(actor_id, action_item->valuestring, entity_item->valuestring, entity_id, old_vals, new_vals, "127.0.0.1", "local");
    cJSON_Delete(root);
    
    if (rc == 0) {
        *res = strdup("{\"status\":\"success\"}");
    }
    return rc;
}
