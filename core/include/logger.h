/**
 * @file logger.h
 * @brief Stub logging macros for Service Layer
 * @copyright Real Estate Management System
 */
#ifndef LOGGER_H
#define LOGGER_H

#include <stdio.h>

/**
 * @todo (Phase 6) Implement real logger writing to file or syslog
 */
#define LOG_INFO(msg)      printf("[INFO] %s\n", (msg))
#define LOG_ERROR(msg)     fprintf(stderr, "[ERROR] %s\n", (msg))
#define LOG_SECURITY(msg)  fprintf(stderr, "[SECURITY] %s\n", (msg))

#endif // LOGGER_H
