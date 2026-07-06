/**
 * @file property_repo.h
 * @brief Property repository interface
 * @copyright Real Estate Management System
 */
#ifndef PROPERTY_REPO_H
#define PROPERTY_REPO_H

#include "property_model.h"

int property_repo_create(const Property* prop, int* out_id);
int property_repo_update(const Property* prop);
int property_repo_get_by_id(int id, Property* out_prop);
int property_repo_archive(int id, int archived_by);
int property_repo_restore(int id);
int property_repo_get_all(const char* search_query, const char* category, const char* listing_type, const char* city, int district, int min_price, int max_price, int min_area, int max_area, const char* sort_col, int sort_asc, int limit, int offset, Property* out_props, int max_props, int* out_count);

#endif
