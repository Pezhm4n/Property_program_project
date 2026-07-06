/**
 * @file dto_validators.c
 * @brief Data Transfer Object validators
 * @copyright Real Estate Management System
 */
#include "re_types.h"

/**
 * @todo Validate string lengths, price ranges, and nullability
 */
int validate_user_dto(const void* dto) {
    (void)dto;
    return RE_OK; // @todo return RE_ERR_VALIDATION on failure
}
