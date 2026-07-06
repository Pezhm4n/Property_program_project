/**
 * @file user_model.h
 * @brief User data structures
 * @copyright Real Estate Management System
 */
#ifndef USER_MODEL_H
#define USER_MODEL_H

typedef struct {
    int id;
    char username[50];
    char password_hash[255];
    char first_name[50];
    char last_name[50];
    char national_id[20];
    char phone[20];
    char role[20];
    int failed_attempts;
    char locked_until[30];
    int is_disabled;
} User;

#endif // USER_MODEL_H
