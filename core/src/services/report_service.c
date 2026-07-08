/**
 * @file report_service.c
 * @brief Reporting and Dashboard service implementation
 * @copyright Real Estate Management System
 */
#include "services.h"
#include "re_types.h"
#include "db_connection.h"
#include <cjson/cJSON.h>
#include <sqlite3.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>

static void calculate_financials(const char* category, const char* listing_type, int sale_price, int rent_deposit, int rent_monthly, double* commission_out, double* tax_out) {
    double commission = 0.0;
    if (strcmp(listing_type, "فروش") == 0 || strcmp(listing_type, "sale") == 0) {
        double rate = (strcmp(category, "تجاری") == 0 || strcmp(category, "commercial") == 0) ? 0.005 : 0.0025;
        commission = sale_price * rate;
    } else if (strcmp(listing_type, "اجاره") == 0 || strcmp(listing_type, "rent") == 0 || strcmp(listing_type, "رهن") == 0) {
        double monthly_rent = rent_monthly + (rent_deposit * 0.03);
        commission = monthly_rent * 0.25;
    }
    *commission_out = commission;
    *tax_out = commission * 0.09;
}

int report_generate(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    cJSON* token_item = cJSON_GetObjectItem(root, "token");
    int actor_id = 0;
    if (!token_item) { cJSON_Delete(root); return RE_ERR_AUTH; }
    int perm_rc = validate_session_and_permission(token_item->valuestring, PERM_VIEW_REPORTS, &actor_id);
    cJSON_Delete(root);
    if (perm_rc != 0) return perm_rc;
    return property_get_all(req, res);
}

int report_get_statistics(const char* req, char** res) {
    (void)req;
    if (res) *res = strdup("{\"status\":\"ok\"}");
    return 0;
}

int report_get_dashboard(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    
    // RBAC: Validate session (VIEW_PROPERTIES is enough for basic dashboard)
    cJSON* root_rbac = cJSON_Parse(req);
    if (!root_rbac) return RE_ERR_VALIDATION;
    cJSON* token_item = cJSON_GetObjectItem(root_rbac, "token");
    int actor_id = 0;
    if (!token_item) { cJSON_Delete(root_rbac); return RE_ERR_AUTH; }
    int perm_rc = validate_session_and_permission(token_item->valuestring, PERM_VIEW_PROPERTIES, &actor_id);
    cJSON_Delete(root_rbac);
    if (perm_rc != 0) return perm_rc;
    sqlite3_stmt* stmt = NULL;
    int rc = db_prepare("SELECT COUNT(*), SUM(CASE WHEN is_archived = 0 THEN 1 ELSE 0 END), SUM(CASE WHEN is_archived = 1 THEN 1 ELSE 0 END) FROM properties;", &stmt);
    int total_props = 0, active_props = 0, archived_props = 0;
    if (rc == 0) {
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            total_props = sqlite3_column_int(stmt, 0);
            active_props = sqlite3_column_int(stmt, 1);
            archived_props = sqlite3_column_int(stmt, 2);
        }
        sqlite3_finalize(stmt);
    }
    
    int total_users = 1;
    rc = db_prepare("SELECT COUNT(*) FROM users WHERE is_disabled = 0;", &stmt);
    if (rc == 0) {
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            total_users = sqlite3_column_int(stmt, 0);
        }
        sqlite3_finalize(stmt);
    }
    
    double total_commission = 0.0;
    double total_tax = 0.0;
    rc = db_prepare("SELECT category, listing_type, sale_price, rent_deposit, rent_monthly FROM properties;", &stmt);
    if (rc == 0) {
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            const char* cat = (const char*)sqlite3_column_text(stmt, 0);
            const char* lt = (const char*)sqlite3_column_text(stmt, 1);
            int sale_p = sqlite3_column_int(stmt, 2);
            int rent_d = sqlite3_column_int(stmt, 3);
            int rent_m = sqlite3_column_int(stmt, 4);
            double comm = 0.0, tax = 0.0;
            calculate_financials(cat, lt, sale_p, rent_d, rent_m, &comm, &tax);
            total_commission += comm;
            total_tax += tax;
        }
        sqlite3_finalize(stmt);
    }
    
    cJSON* activities_arr = cJSON_CreateArray();
    rc = db_prepare(
        "SELECT audit_logs.created_at, COALESCE(users.username, 'system'), audit_logs.action, audit_logs.new_values_json "
        "FROM audit_logs LEFT JOIN users ON audit_logs.actor_id = users.id "
        "ORDER BY audit_logs.id DESC LIMIT 5;", 
        &stmt
    );
    if (rc == 0) {
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            cJSON* act = cJSON_CreateObject();
            cJSON_AddStringToObject(act, "timestamp", (const char*)sqlite3_column_text(stmt, 0));
            cJSON_AddStringToObject(act, "user", (const char*)sqlite3_column_text(stmt, 1));
            cJSON_AddStringToObject(act, "action", (const char*)sqlite3_column_text(stmt, 2));
            cJSON_AddStringToObject(act, "details", (const char*)sqlite3_column_text(stmt, 3));
            cJSON_AddItemToArray(activities_arr, act);
        }
        sqlite3_finalize(stmt);
    }
    
    int sales_counts[6] = {0, 0, 0, 0, 0, 0};
    int rent_counts[6] = {0, 0, 0, 0, 0, 0};
    
    time_t t = time(NULL);
    struct tm* tm_info = localtime(&t);
    int current_year = tm_info ? (tm_info->tm_year + 1900) : 2026;
    int current_month = tm_info ? (tm_info->tm_mon + 1) : 7;
    
    char query_buf[256];
    for (int i = 0; i < 6; ++i) {
        int target_mon = current_month - (5 - i);
        int target_yr = current_year;
        while (target_mon <= 0) {
            target_mon += 12;
            target_yr -= 1;
        }
        char month_str[16];
        sprintf(month_str, "%04d-%02d", target_yr, target_mon);
        
        // Query sales for this month
        sprintf(query_buf, "SELECT COUNT(*) FROM properties WHERE (listing_type='فروش' OR listing_type='sale') AND created_at LIKE '%s%%';", month_str);
        sqlite3_stmt* month_stmt = NULL;
        int db_count = 0;
        if (db_prepare(query_buf, &month_stmt) == 0) {
            if (sqlite3_step(month_stmt) == SQLITE_ROW) {
                db_count = sqlite3_column_int(month_stmt, 0);
            }
            sqlite3_finalize(month_stmt);
        }
        sales_counts[i] += db_count;
        
        // Query rents for this month
        sprintf(query_buf, "SELECT COUNT(*) FROM properties WHERE (listing_type='اجاره' OR listing_type='rent' OR listing_type='رهن') AND created_at LIKE '%s%%';", month_str);
        db_count = 0;
        if (db_prepare(query_buf, &month_stmt) == 0) {
            if (sqlite3_step(month_stmt) == SQLITE_ROW) {
                db_count = sqlite3_column_int(month_stmt, 0);
            }
            sqlite3_finalize(month_stmt);
        }
        rent_counts[i] += db_count;
    }

    cJSON* dashboard = cJSON_CreateObject();
    cJSON_AddNumberToObject(dashboard, "total_properties", total_props);
    cJSON_AddNumberToObject(dashboard, "active_properties", active_props);
    cJSON_AddNumberToObject(dashboard, "archived_properties", archived_props);
    cJSON_AddNumberToObject(dashboard, "total_users", total_users);
    cJSON_AddNumberToObject(dashboard, "total_agents", total_users);
    cJSON_AddStringToObject(dashboard, "last_update", "الان");
    cJSON_AddItemToObject(dashboard, "recent_activities", activities_arr);

    cJSON* charts = cJSON_CreateObject();
    cJSON* monthly_sales = cJSON_CreateArray();
    for (int i = 0; i < 6; ++i) {
        cJSON_AddItemToArray(monthly_sales, cJSON_CreateNumber(sales_counts[i]));
    }
    cJSON_AddItemToObject(charts, "monthly_sales", monthly_sales);

    cJSON* monthly_rents = cJSON_CreateArray();
    for (int i = 0; i < 6; ++i) {
        cJSON_AddItemToArray(monthly_rents, cJSON_CreateNumber(rent_counts[i]));
    }
    cJSON_AddItemToObject(charts, "monthly_rents", monthly_rents);

    cJSON* financials = cJSON_CreateObject();
    cJSON_AddNumberToObject(financials, "commission", (int)total_commission);
    cJSON_AddNumberToObject(financials, "tax", (int)total_tax);
    cJSON_AddItemToObject(charts, "financials", financials);

    cJSON_AddItemToObject(dashboard, "charts", charts);

    char* resp_str = cJSON_PrintUnformatted(dashboard);
    *res = strdup(resp_str);
    free(resp_str);
    cJSON_Delete(dashboard);
    
    return 0;
}
