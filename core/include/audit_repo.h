/**
 * @file audit_repo.h
 * @brief Audit repository interface
 * @copyright Real Estate Management System
 */
#ifndef AUDIT_REPO_H
#define AUDIT_REPO_H

int audit_repo_log(int actor_id, const char* action, const char* entity, int entity_id, const char* old_vals, const char* new_vals, const char* ip, const char* machine);

#endif
