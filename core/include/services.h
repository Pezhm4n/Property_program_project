/**
 * @file services.h
 * @brief Service Layer interfaces (RBAC-aware)
 * @copyright Real Estate Management System
 */
#ifndef SERVICES_H
#define SERVICES_H

#include "re_types.h"

/* Central RBAC validation — used by all endpoints */
int validate_session_and_permission(const char* token, PermissionEnum required_perm, int* out_user_id);

/* Auth */
int auth_login(const char* req, char** res);
int auth_logout(const char* req, char** res);
int auth_validate_session(const char* req, char** res);
int auth_has_any_user(const char* req, char** res);
int auth_create_initial_admin(const char* req, char** res);
int auth_change_password(const char* req, char** res);
int auth_log_audit(const char* req, char** res);

/* User Management (Admin-only) */
int user_management_get_all(const char* req, char** res);
int user_management_create(const char* req, char** res);
int user_management_change_role(const char* req, char** res);
int user_management_reset_password(const char* req, char** res);
int user_management_toggle_status(const char* req, char** res);

/* Property */
int property_create(const char* req, char** res);
int property_update(const char* req, char** res);
int property_get_all(const char* req, char** res);
int property_get_by_id(const char* req, char** res);
int property_archive(const char* req, char** res);
int property_restore(const char* req, char** res);

/* Reports & Dashboard */
int report_generate(const char* req, char** res);
int report_get_statistics(const char* req, char** res);
int report_get_dashboard(const char* req, char** res);

#endif // SERVICES_H
