/**
 * @file user_repo.h
 * @brief User & Session repository interface (RBAC-aware)
 * @copyright Real Estate Management System
 */
#ifndef USER_REPO_H
#define USER_REPO_H

#include "user_model.h"

/* User CRUD */
int user_repo_create(const User* user, int* out_id);
int user_repo_get_by_id(int id, User* out_user);
int user_repo_get_by_username(const char* username, User* out_user);
int user_repo_update_failed_attempts(int id, int attempts, const char* locked_until);
int user_repo_update_last_login(int id);
int user_repo_soft_delete(int id);
int user_repo_enable(int id);
int user_repo_update_role(int id, int new_role_id);
int user_repo_update_password(int id, const char* new_password_hash);
int user_repo_count_admins(int* count);
int user_repo_get_all(User* out_users, int max_count, int* out_count);

/* Session Management */
int session_repo_create(int user_id, const char* token, const char* permissions_json);
int session_repo_validate(const char* token, Session* out_session);
int session_repo_delete(const char* token);
int session_repo_delete_by_user(int user_id);

/* Permission Loading */
int permission_repo_get_by_role(int role_id, char* out_json, int max_len);
int permission_repo_get_ids_by_role(int role_id, int* out_ids, int max_count, int* out_count);

#endif // USER_REPO_H
