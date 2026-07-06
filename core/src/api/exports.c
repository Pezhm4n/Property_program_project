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

RE_API int re_get_api_version() {
    return 100; // 1.0.0
}

RE_API int re_get_dll_version() {
    return 100; // 1.0.0
}

RE_API int re_get_last_error() {
    return last_error;
}

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
    if (!request_json || !response_json_out) return RE_ERR_VALIDATION;
    // TODO: Call property_service_create
    last_error = RE_ERR_NOT_IMPLEMENTED;
    return RE_ERR_NOT_IMPLEMENTED;
}

RE_API int re_update_property(const char* request_json, char** response_json_out) {
    if (!request_json || !response_json_out) return RE_ERR_VALIDATION;
    // TODO: Call property_service_update
    last_error = RE_ERR_NOT_IMPLEMENTED;
    return RE_ERR_NOT_IMPLEMENTED;
}

RE_API int re_get_properties(const char* request_json, char** response_json_out) {
    if (!request_json || !response_json_out) return RE_ERR_VALIDATION;
    // TODO: Call property_service_get_all
    last_error = RE_ERR_NOT_IMPLEMENTED;
    return RE_ERR_NOT_IMPLEMENTED;
}

RE_API int re_get_property(const char* request_json, char** response_json_out) {
    if (!request_json || !response_json_out) return RE_ERR_VALIDATION;
    // TODO: Call property_service_get_by_id
    last_error = RE_ERR_NOT_IMPLEMENTED;
    return RE_ERR_NOT_IMPLEMENTED;
}

RE_API int re_archive_property(const char* request_json, char** response_json_out) {
    if (!request_json || !response_json_out) return RE_ERR_VALIDATION;
    // TODO: Call property_service_archive
    last_error = RE_ERR_NOT_IMPLEMENTED;
    return RE_ERR_NOT_IMPLEMENTED;
}

RE_API int re_restore_property(const char* request_json, char** response_json_out) {
    if (!request_json || !response_json_out) return RE_ERR_VALIDATION;
    // TODO: Call property_service_restore
    last_error = RE_ERR_NOT_IMPLEMENTED;
    return RE_ERR_NOT_IMPLEMENTED;
}

RE_API int re_get_report(const char* request_json, char** response_json_out) {
    if (!request_json || !response_json_out) return RE_ERR_VALIDATION;
    // TODO: Call report_service_generate
    last_error = RE_ERR_NOT_IMPLEMENTED;
    return RE_ERR_NOT_IMPLEMENTED;
}

RE_API int re_get_statistics(const char* request_json, char** response_json_out) {
    if (!request_json || !response_json_out) return RE_ERR_VALIDATION;
    // TODO: Call report_service_stats
    last_error = RE_ERR_NOT_IMPLEMENTED;
    return RE_ERR_NOT_IMPLEMENTED;
}

RE_API int re_get_dashboard(const char* request_json, char** response_json_out) {
    if (!request_json || !response_json_out) return RE_ERR_VALIDATION;
    // TODO: Call report_service_dashboard
    last_error = RE_ERR_NOT_IMPLEMENTED;
    return RE_ERR_NOT_IMPLEMENTED;
}

RE_API int re_validate_session(const char* request_json, char** response_json_out) {
    if (!request_json || !response_json_out) return RE_ERR_VALIDATION;
    // TODO: Call auth_service_validate
    last_error = RE_ERR_NOT_IMPLEMENTED;
    return RE_ERR_NOT_IMPLEMENTED;
}

RE_API int re_ping(const char* request_json, char** response_json_out) {
    if (!response_json_out) return RE_ERR_VALIDATION;
    char* resp = (char*)malloc(16);
    if (!resp) return RE_ERR_INTERNAL;
    strcpy(resp, "{\"status\":\"ok\"}");
    *response_json_out = resp;
    return 0;
}
