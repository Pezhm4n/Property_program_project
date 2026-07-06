/**
 * @file user_repo.c
 * @brief User repository interface
 * @copyright Real Estate Management System
 */
#include "user_repo.h"

int user_repo_create(const User* user, int* out_id) {
    (void)user; (void)out_id;
    return -99; // TODO: Implement in Phase 3
}
int user_repo_get_by_id(int id, User* out_user) {
    (void)id; (void)out_user;
    return -99; // TODO: Implement in Phase 3
}
int user_repo_get_by_username(const char* username, User* out_user) {
    (void)username; (void)out_user;
    return -99; // TODO: Implement in Phase 3
}
int user_repo_update_failed_attempts(int id, int attempts, const char* locked_until) {
    (void)id; (void)attempts; (void)locked_until;
    return -99; // TODO: Implement in Phase 3
}
int user_repo_soft_delete(int id) {
    (void)id;
    return -99; // TODO: Implement in Phase 3
}
