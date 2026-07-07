/**
 * @file services.h
 * @brief Service Layer interfaces
 * @copyright Real Estate Management System
 */
#ifndef SERVICES_H
#define SERVICES_H
int auth_login(const char* req, char** res);
int auth_logout(const char* req, char** res);
int auth_validate_session(const char* req, char** res);
int auth_has_any_user(const char* req, char** res);
int auth_create_initial_admin(const char* req, char** res);
int auth_change_password(const char* req, char** res);
int property_create(const char* req, char** res);
int property_update(const char* req, char** res);
int property_get_all(const char* req, char** res);
int property_get_by_id(const char* req, char** res);
int property_archive(const char* req, char** res);
int property_restore(const char* req, char** res);

int report_generate(const char* req, char** res);
int report_get_statistics(const char* req, char** res);
int report_get_dashboard(const char* req, char** res);

#endif // SERVICES_H
