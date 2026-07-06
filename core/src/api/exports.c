/**
 * @file exports.c
 * @brief DLL API Export Facades
 * @copyright Real Estate Management System
 */
#include "re_core.h"
#include <stdlib.h>

// Forward declarations to Service Layer (which will handle the business logic)
extern int auth_login(const char* req, char** res);
extern int auth_logout(const char* req, char** res);
extern int property_create(const char* req, char** res);
extern int property_archive(const char* req, char** res);
extern int report_generate(const char* req, char** res);

RE_API void re_free_string(char* str) {
    if (str) {
        free(str);
    }
}

RE_API int re_login(const char* request_json, char** response_json_out) {
    return auth_login(request_json, response_json_out);
}

RE_API int re_logout(const char* request_json, char** response_json_out) {
    return auth_logout(request_json, response_json_out);
}

RE_API int re_create_property(const char* request_json, char** response_json_out) {
    return property_create(request_json, response_json_out);
}

RE_API int re_archive_property(const char* request_json, char** response_json_out) {
    return property_archive(request_json, response_json_out);
}

RE_API int re_get_report(const char* request_json, char** response_json_out) {
    return report_generate(request_json, response_json_out);
}
