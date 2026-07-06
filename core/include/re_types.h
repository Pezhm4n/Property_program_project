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
#define RE_ERR_BUSY          -10
#define RE_ERR_CORRUPT       -11
#define RE_ERR_MEM           -98
#define RE_ERR_INTERNAL      -99
#define RE_ERR_NOT_IMPLEMENTED -100

#endif // RE_TYPES_H
