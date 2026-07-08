/**
 * @file user_model.h
 * @brief User data structures
 * @copyright Real Estate Management System
 */
#ifndef USER_MODEL_H
#define USER_MODEL_H

#define MAX_PERMISSIONS 32

typedef struct {
    int id;
    int role_id;
    char username[50];
    char password_hash[255];
    char first_name[50];
    char last_name[50];
    char national_id[20];
    char phone[20];
    char role_name[30];
    int failed_attempts;
    char locked_until[30];
    int is_disabled;
    char created_at[30];
    char updated_at[30];
    char last_login_at[30];
} User;

typedef struct {
    int user_id;
    char token[65];
    char permissions_cache[2048];
    int permission_ids[MAX_PERMISSIONS];
    int permission_count;
} Session;

#endif // USER_MODEL_H
