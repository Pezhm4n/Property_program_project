/**
 * @file user_repo.h
 * @brief User repository interface
 * @copyright Real Estate Management System
 */
#ifndef USER_REPO_H
#define USER_REPO_H

#include "user_model.h"

int user_repo_create(const User* user, int* out_id);
int user_repo_get_by_id(int id, User* out_user);
int user_repo_get_by_username(const char* username, User* out_user);
int user_repo_update_failed_attempts(int id, int attempts, const char* locked_until);
int user_repo_soft_delete(int id);

#endif // USER_REPO_H
