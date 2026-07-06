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
    return property_get_all(req, res);
}

int report_get_statistics(const char* req, char** res) {
    (void)req;
    if (res) *res = strdup("{\"status\":\"ok\"}");
    return 0;
}

int report_get_dashboard(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    
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
    cJSON_AddItemToArray(monthly_sales, cJSON_CreateNumber(total_props * 2));
    cJSON_AddItemToArray(monthly_sales, cJSON_CreateNumber(total_props * 3));
    cJSON_AddItemToArray(monthly_sales, cJSON_CreateNumber(total_props));
    cJSON_AddItemToObject(charts, "monthly_sales", monthly_sales);

    cJSON* monthly_rents = cJSON_CreateArray();
    cJSON_AddItemToArray(monthly_rents, cJSON_CreateNumber(active_props));
    cJSON_AddItemToArray(monthly_rents, cJSON_CreateNumber(archived_props));
    cJSON_AddItemToArray(monthly_rents, cJSON_CreateNumber(total_props));
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
