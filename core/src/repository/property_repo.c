/**
 * @file property_repo.c
 * @brief Property repository implementation
 * @copyright Real Estate Management System
 */
#include "property_repo.h"
#include "db_connection.h"
#include <sqlite3.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

int property_repo_create(const Property* prop, int* out_id) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "INSERT INTO properties (is_archived, category, listing_type, city, municipal_district, address, owner_phone, area_sqm, sale_price, rent_deposit, rent_monthly, created_by, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'));",
        &stmt
    );
    if (rc != 0) return rc;

    sqlite3_bind_int(stmt, 1, prop->is_archived);
    sqlite3_bind_text(stmt, 2, prop->category, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, prop->listing_type, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 4, prop->city, -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(stmt, 5, prop->municipal_district);
    sqlite3_bind_text(stmt, 6, prop->address, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 7, prop->owner_phone, -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(stmt, 8, prop->area_sqm);
    sqlite3_bind_int(stmt, 9, prop->sale_price);
    sqlite3_bind_int(stmt, 10, prop->rent_deposit);
    sqlite3_bind_int(stmt, 11, prop->rent_monthly);
    if (prop->created_by > 0) {
        sqlite3_bind_int(stmt, 12, prop->created_by);
    } else {
        sqlite3_bind_null(stmt, 12);
    }

    int step_rc = sqlite3_step(stmt);
    if (step_rc == SQLITE_DONE && out_id) {
        *out_id = (int)sqlite3_last_insert_rowid(db_get_connection());
    }
    sqlite3_finalize(stmt);

    if (step_rc != SQLITE_DONE) {
        return db_map_error(step_rc);
    }
    return 0;
}

int property_repo_update(const Property* prop) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "UPDATE properties SET is_archived = ?, category = ?, listing_type = ?, city = ?, municipal_district = ?, address = ?, owner_phone = ?, area_sqm = ?, sale_price = ?, rent_deposit = ?, rent_monthly = ?, updated_at = datetime('now') WHERE id = ?;",
        &stmt
    );
    if (rc != 0) return rc;

    sqlite3_bind_int(stmt, 1, prop->is_archived);
    sqlite3_bind_text(stmt, 2, prop->category, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, prop->listing_type, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 4, prop->city, -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(stmt, 5, prop->municipal_district);
    sqlite3_bind_text(stmt, 6, prop->address, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 7, prop->owner_phone, -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(stmt, 8, prop->area_sqm);
    sqlite3_bind_int(stmt, 9, prop->sale_price);
    sqlite3_bind_int(stmt, 10, prop->rent_deposit);
    sqlite3_bind_int(stmt, 11, prop->rent_monthly);
    sqlite3_bind_int(stmt, 12, prop->id);

    int step_rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    if (step_rc != SQLITE_DONE) {
        return db_map_error(step_rc);
    }
    return 0;
}

static void map_row_to_property(sqlite3_stmt* stmt, Property* out_prop) {
    out_prop->id = sqlite3_column_int(stmt, 0);
    out_prop->is_archived = sqlite3_column_int(stmt, 1);
    strcpy(out_prop->category, (const char*)sqlite3_column_text(stmt, 2));
    strcpy(out_prop->listing_type, (const char*)sqlite3_column_text(stmt, 3));
    strcpy(out_prop->city, (const char*)sqlite3_column_text(stmt, 4));
    out_prop->municipal_district = sqlite3_column_int(stmt, 5);
    strcpy(out_prop->address, (const char*)sqlite3_column_text(stmt, 6));
    strcpy(out_prop->owner_phone, (const char*)sqlite3_column_text(stmt, 7));
    out_prop->area_sqm = sqlite3_column_int(stmt, 8);
    out_prop->sale_price = sqlite3_column_int(stmt, 9);
    out_prop->rent_deposit = sqlite3_column_int(stmt, 10);
    out_prop->rent_monthly = sqlite3_column_int(stmt, 11);
    out_prop->created_by = sqlite3_column_int(stmt, 12);
    strcpy(out_prop->created_at, (const char*)sqlite3_column_text(stmt, 13));
    const char* arch_at = (const char*)sqlite3_column_text(stmt, 14);
    if (arch_at) {
        strcpy(out_prop->archived_at, arch_at);
    } else {
        out_prop->archived_at[0] = '\0';
    }
    out_prop->archived_by = sqlite3_column_int(stmt, 15);
}

int property_repo_get_by_id(int id, Property* out_prop) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(
        "SELECT id, is_archived, category, listing_type, city, municipal_district, address, owner_phone, area_sqm, sale_price, rent_deposit, rent_monthly, created_by, created_at, archived_at, archived_by FROM properties WHERE id = ?;",
        &stmt
    );
    if (rc != 0) return rc;

    sqlite3_bind_int(stmt, 1, id);

    int step_rc = sqlite3_step(stmt);
    if (step_rc == SQLITE_ROW) {
        map_row_to_property(stmt, out_prop);
        rc = 0;
    } else if (step_rc == SQLITE_DONE) {
        rc = -2; // RE_ERR_NOT_FOUND
    } else {
        rc = db_map_error(step_rc);
    }
    sqlite3_finalize(stmt);
    return rc;
}

int property_repo_archive(int id, int archived_by) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare("UPDATE properties SET is_archived = 1, archived_at = datetime('now'), archived_by = ? WHERE id = ?;", &stmt);
    if (rc != 0) return rc;

    sqlite3_bind_int(stmt, 1, archived_by);
    sqlite3_bind_int(stmt, 2, id);

    int step_rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    if (step_rc != SQLITE_DONE) {
        return db_map_error(step_rc);
    }
    return 0;
}

int property_repo_restore(int id) {
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare("UPDATE properties SET is_archived = 0, archived_at = NULL, archived_by = NULL WHERE id = ?;", &stmt);
    if (rc != 0) return rc;

    sqlite3_bind_int(stmt, 1, id);

    int step_rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    if (step_rc != SQLITE_DONE) {
        return db_map_error(step_rc);
    }
    return 0;
}
int property_repo_get_all(const char* search_query, const char* category, const char* listing_type, const char* city, int district, int min_price, int max_price, int min_area, int max_area, int is_archived_filter, const char* sort_col, int sort_asc, int limit, int offset, Property* out_props, int max_props, int* out_count) {
    char sql[2048] = "SELECT id, is_archived, category, listing_type, city, municipal_district, address, owner_phone, area_sqm, sale_price, rent_deposit, rent_monthly, created_by, created_at, archived_at, archived_by FROM properties WHERE 1=1";
    
    if (is_archived_filter == 0) {
        strcat(sql, " AND is_archived = 0");
    } else if (is_archived_filter == 1) {
        strcat(sql, " AND is_archived = 1");
    }

    if (search_query && strlen(search_query) > 0) {
        strcat(sql, " AND (address LIKE ? OR owner_phone LIKE ? OR category LIKE ?)");
    }
    if (category && strlen(category) > 0) {
        strcat(sql, " AND category = ?");
    }
    if (listing_type && strlen(listing_type) > 0) {
        strcat(sql, " AND listing_type = ?");
    }
    if (city && strlen(city) > 0) {
        strcat(sql, " AND city = ?");
    }
    if (district > 0) {
        strcat(sql, " AND municipal_district = ?");
    }
    if (min_price > 0) {
        strcat(sql, " AND sale_price >= ?");
    }
    if (max_price > 0) {
        strcat(sql, " AND sale_price <= ?");
    }
    if (min_area > 0) {
        strcat(sql, " AND area_sqm >= ?");
    }
    if (max_area > 0) {
        strcat(sql, " AND area_sqm <= ?");
    }
    
    const char* valid_cols[] = {"id", "is_archived", "category", "listing_type", "city", "municipal_district", "address", "owner_phone", "area_sqm", "sale_price", "rent_deposit", "rent_monthly", "created_by", "created_at"};
    const char* sort_str = "created_at";
    for (size_t i = 0; i < sizeof(valid_cols)/sizeof(char*); ++i) {
        if (sort_col && strcmp(sort_col, valid_cols[i]) == 0) {
            sort_str = valid_cols[i];
            break;
        }
    }
    char order_by[128];
    snprintf(order_by, sizeof(order_by), " ORDER BY %s %s", sort_str, sort_asc ? "ASC" : "DESC");
    strcat(sql, order_by);
    
    if (limit > 0) {
        strcat(sql, " LIMIT ? OFFSET ?");
    }
    
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare(sql, &stmt);
    if (rc != 0) return rc;
    
    int param_idx = 1;
    if (search_query && strlen(search_query) > 0) {
        char like_val[256];
        snprintf(like_val, sizeof(like_val), "%%%s%%", search_query);
        sqlite3_bind_text(stmt, param_idx++, like_val, -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt, param_idx++, like_val, -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt, param_idx++, like_val, -1, SQLITE_TRANSIENT);
    }
    if (category && strlen(category) > 0) {
        sqlite3_bind_text(stmt, param_idx++, category, -1, SQLITE_TRANSIENT);
    }
    if (listing_type && strlen(listing_type) > 0) {
        sqlite3_bind_text(stmt, param_idx++, listing_type, -1, SQLITE_TRANSIENT);
    }
    if (city && strlen(city) > 0) {
        sqlite3_bind_text(stmt, param_idx++, city, -1, SQLITE_TRANSIENT);
    }
    if (district > 0) {
        sqlite3_bind_int(stmt, param_idx++, district);
    }
    if (min_price > 0) {
        sqlite3_bind_int(stmt, param_idx++, min_price);
    }
    if (max_price > 0) {
        sqlite3_bind_int(stmt, param_idx++, max_price);
    }
    if (min_area > 0) {
        sqlite3_bind_int(stmt, param_idx++, min_area);
    }
    if (max_area > 0) {
        sqlite3_bind_int(stmt, param_idx++, max_area);
    }
    if (limit > 0) {
        sqlite3_bind_int(stmt, param_idx++, limit);
        sqlite3_bind_int(stmt, param_idx++, offset);
    }
    
    int count = 0;
    while (sqlite3_step(stmt) == SQLITE_ROW && count < max_props) {
        map_row_to_property(stmt, &out_props[count]);
        count++;
    }
    sqlite3_finalize(stmt);
    
    if (out_count) *out_count = count;
    return 0;
}
