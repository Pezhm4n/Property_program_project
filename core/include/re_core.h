/**
 * @file re_core.h
 * @brief Core DLL API Exports
 * @copyright Real Estate Management System
 */
#ifndef RE_CORE_H
#define RE_CORE_H

#ifdef _WIN32
  #define RE_API __declspec(dllexport)
#else
  #define RE_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Thread Safety Policy:
 * All re_* functions are thread-safe ONLY IF SQLite is compiled with serialized mode
 * and concurrent connections are properly managed. Until Phase 6, assume single-threaded.
 * Undefined behavior may occur if called concurrently from Python without locks.
 */

/**
 * @brief Get expected API version.
 * @return Integer representing API version (e.g. 100 for 1.0.0).
 */
RE_API int re_get_api_version();

/**
 * @brief Get DLL actual build version.
 * @return Integer representing DLL version (e.g. 100 for 1.0.0).
 */
RE_API int re_get_dll_version();

/**
 * @brief Get the last error code encountered by the DLL in the current thread.
 * @return Project error code.
 */
RE_API int re_get_last_error();

/**
 * @brief Frees a string allocated by the DLL.
 * MUST be called by the Python bridge for any string returned.
 */
RE_API void re_free_string(char* str);

/**
 * @brief Authenticate user.
 * @param request_json JSON containing username and password.
 * @param response_json_out Output JSON containing session token on success.
 * @return 0 on success, negative RE_ERR_* on failure.
 */
RE_API int re_login(const char* request_json, char** response_json_out);

/**
 * @brief Logout user.
 * @param request_json JSON containing session_token.
 * @param response_json_out Empty output JSON on success.
 * @return 0 on success, negative RE_ERR_* on failure.
 */
RE_API int re_logout(const char* request_json, char** response_json_out);

/**
 * @brief Create a new property listing.
 * @param request_json JSON containing property details and session token.
 * @param response_json_out Output JSON containing new property ID.
 * @return 0 on success, negative RE_ERR_* on failure.
 */
RE_API int re_create_property(const char* request_json, char** response_json_out);

/**
 * @brief Archive an existing property.
 * @param request_json JSON containing property ID and session token.
 * @param response_json_out Empty output JSON on success.
 * @return 0 on success, negative RE_ERR_* on failure.
 */
RE_API int re_archive_property(const char* request_json, char** response_json_out);

/**
 * @brief Get property reports.
 * @param request_json JSON containing filters and session token.
 * @param response_json_out Output JSON containing aggregate report.
 * @return 0 on success, negative RE_ERR_* on failure.
 */
RE_API int re_get_report(const char* request_json, char** response_json_out);

#ifdef __cplusplus
}
#endif

#endif // RE_CORE_H
