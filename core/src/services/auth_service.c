/**
 * @file auth_service.c
 * @brief Authentication Service Implementation
 * @copyright Real Estate Management System
 */
#include "services.h"
#include "re_types.h"
#include "user_repo.h"
#include "audit_repo.h"
#include "db_connection.h"
#include <string.h>
#include <stdlib.h>

/**
 * @todo Implement cJSON parsing of request_json
 * @todo Implement Password Hashing comparison
 * @todo Implement Session UUID generation
 */
int auth_login(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    
    // 1. Validation (Extract from JSON)
    // 2. Begin Transaction
    int rc = db_begin_transaction();
    if (rc != RE_OK) return rc;
    
    // 3. Repo Call (Get User)
    User user;
    rc = user_repo_get_by_username("parsed_username", &user);
    if (rc != RE_OK) {
        db_rollback_transaction();
        return RE_ERR_AUTH; // Obfuscate exact error
    }
    
    // 4. Business Logic (Check lock, hash password)
    // if locked: rollback, return RE_ERR_LOCKED
    
    // 5. Audit Logging
    audit_repo_log(user.id, "LOGIN", "session", 0, "{}", "{\"status\":\"success\"}", "127.0.0.1", "API");
    
    // 6. Commit Transaction
    rc = db_commit_transaction();
    
    // 7. Format Output JSON
    *res = strdup("{\"token\":\"dummy-uuid\"}");
    
    return rc;
}

int auth_logout(const char* req, char** res) {
    (void)req; 
    if (res) *res = strdup("{}");
    return RE_OK;
}
