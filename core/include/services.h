/**
 * @file services.h
 * @brief Service Layer interfaces
 * @copyright Real Estate Management System
 */
#ifndef SERVICES_H
#define SERVICES_H

int auth_login(const char* req, char** res);
int auth_logout(const char* req, char** res);
int property_create(const char* req, char** res);
int property_archive(const char* req, char** res);
int report_generate(const char* req, char** res);

#endif // SERVICES_H
