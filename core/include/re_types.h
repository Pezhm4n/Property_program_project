/**
 * @file re_types.h
 * @brief Common types and error codes for Real Estate Management System
 * @copyright Real Estate Management System
 */
#ifndef RE_TYPES_H
#define RE_TYPES_H

// Core Error Codes based on 09_ERROR_CODES.md
#define RE_OK                 0
#define RE_ERR_VALIDATION    -1
#define RE_ERR_NOT_FOUND     -2
#define RE_ERR_DUPLICATE     -3
#define RE_ERR_AUTH          -4
#define RE_ERR_LOCKED        -5
#define RE_ERR_FORBIDDEN     -6
#define RE_ERR_DB            -7
#define RE_ERR_SESSION_EXPIRED -8
#define RE_ERR_BUSY          -10
#define RE_ERR_CORRUPT       -11
#define RE_ERR_LAST_ADMIN    -12
#define RE_ERR_MEM           -98
#define RE_ERR_INTERNAL      -99
#define RE_ERR_NOT_IMPLEMENTED -100

// Permission Enum — IDs match the `permissions` table in the database
typedef enum {
    PERM_VIEW_PROPERTIES = 1,
    PERM_CREATE_PROPERTY = 2,
    PERM_EDIT_PROPERTY = 3,
    PERM_DELETE_PROPERTY = 4,
    PERM_ARCHIVE_PROPERTY = 5,
    PERM_RESTORE_PROPERTY = 6,
    PERM_VIEW_REPORTS = 7,
    PERM_VIEW_FINANCIAL_REPORTS = 8,
    PERM_MANAGE_USERS = 9,
    PERM_CHANGE_USER_ROLE = 10,
    PERM_RESET_PASSWORD = 11,
    PERM_BACKUP_DATABASE = 12,
    PERM_RESTORE_DATABASE = 13,
    PERM_VIEW_SETTINGS = 14,
    PERM_VIEW_AUDIT_LOG = 15,
    PERM_EXPORT_REPORTS = 16
} PermissionEnum;

#endif // RE_TYPES_H
