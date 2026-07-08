/**
 * @file property_service.c
 * @brief Property Service Implementation
 * @copyright Real Estate Management System
 */
#include "services.h"
#include "re_types.h"
#include "property_repo.h"
#include "audit_repo.h"
#include "db_connection.h"
#include <cjson/cJSON.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

static void trim_whitespace(char* str) {
    if (!str) return;
    char* start = str;
    while (*start == ' ' || *start == '\t' || *start == '\r' || *start == '\n') {
        start++;
    }
    if (start != str) {
        memmove(str, start, strlen(start) + 1);
    }
    size_t len = strlen(str);
    while (len > 0 && (str[len - 1] == ' ' || str[len - 1] == '\t' || str[len - 1] == '\r' || str[len - 1] == '\n')) {
        str[len - 1] = '\0';
        len--;
    }
}

static int validate_phone(const char* phone) {
    if (!phone || strlen(phone) != 11) return 0;
    if (phone[0] != '0' || phone[1] != '9') return 0;
    for (int i = 0; i < 11; ++i) {
        if (phone[i] < '0' || phone[i] > '9') return 0;
    }
    return 1;
}

static int map_json_to_property(cJSON* prop_obj, Property* p) {
    cJSON* cat = cJSON_GetObjectItem(prop_obj, "category");
    cJSON* lt = cJSON_GetObjectItem(prop_obj, "listing_type");
    cJSON* ct = cJSON_GetObjectItem(prop_obj, "city");
    cJSON* dist = cJSON_GetObjectItem(prop_obj, "municipal_district");
    cJSON* addr = cJSON_GetObjectItem(prop_obj, "address");
    cJSON* phone = cJSON_GetObjectItem(prop_obj, "owner_phone");
    cJSON* area = cJSON_GetObjectItem(prop_obj, "area_sqm");
    cJSON* sale_p = cJSON_GetObjectItem(prop_obj, "sale_price");
    cJSON* rent_d = cJSON_GetObjectItem(prop_obj, "rent_deposit");
    cJSON* rent_m = cJSON_GetObjectItem(prop_obj, "rent_monthly");
    cJSON* arch = cJSON_GetObjectItem(prop_obj, "is_archived");
    if (!cat || !lt || !addr || !phone || !area) return RE_ERR_VALIDATION;

    // Bounds checking to prevent buffer overflow
    if (strlen(cat->valuestring) >= sizeof(p->category)) return RE_ERR_VALIDATION;
    if (strlen(lt->valuestring) >= sizeof(p->listing_type)) return RE_ERR_VALIDATION;
    if (ct && strlen(ct->valuestring) >= sizeof(p->city)) return RE_ERR_VALIDATION;
    if (strlen(addr->valuestring) >= sizeof(p->address)) return RE_ERR_VALIDATION;
    if (strlen(phone->valuestring) >= sizeof(p->owner_phone)) return RE_ERR_VALIDATION;

    if (arch) {
        p->is_archived = cJSON_IsTrue(arch) ? 1 : 0;
    } else {
        p->is_archived = 0;
    }
    strcpy(p->category, cat->valuestring);
    strcpy(p->listing_type, lt->valuestring);
    strcpy(p->city, ct ? ct->valuestring : "تهران");
    p->municipal_district = dist ? dist->valueint : 1;
    strcpy(p->address, addr->valuestring);
    strcpy(p->owner_phone, phone->valuestring);

    // Hardening: trim input strings
    trim_whitespace(p->category);
    trim_whitespace(p->listing_type);
    trim_whitespace(p->city);
    trim_whitespace(p->address);
    trim_whitespace(p->owner_phone);

    // Validate fields
    if (!validate_phone(p->owner_phone)) return RE_ERR_VALIDATION;
    if (strlen(p->address) == 0) return RE_ERR_VALIDATION; // Reject whitespace-only address
    
    p->area_sqm = area->valueint;
    p->sale_price = sale_p ? sale_p->valueint : 0;
    p->rent_deposit = rent_d ? rent_d->valueint : 0;
    p->rent_monthly = rent_m ? rent_m->valueint : 0;

    // Additional validations
    if (p->area_sqm <= 0) return RE_ERR_VALIDATION;
    if (p->municipal_district < 1 || p->municipal_district > 22) return RE_ERR_VALIDATION;
    if (p->sale_price < 0 || p->rent_deposit < 0 || p->rent_monthly < 0) return RE_ERR_VALIDATION;
    
    if (strcmp(p->listing_type, "فروش") == 0 || strcmp(p->listing_type, "sale") == 0) {
        if (p->sale_price <= 0) return RE_ERR_VALIDATION;
        p->rent_deposit = 0;
        p->rent_monthly = 0;
    } else if (strcmp(p->listing_type, "اجاره") == 0 || strcmp(p->listing_type, "rent") == 0 || strcmp(p->listing_type, "رهن") == 0) {
        if (p->rent_deposit <= 0 && p->rent_monthly <= 0) return RE_ERR_VALIDATION;
        p->sale_price = 0;
    }

    return 0;
}

int property_create(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    
    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    
    // RBAC: Validate session and CREATE_PROPERTY permission
    cJSON* token_item = cJSON_GetObjectItem(root, "token");
    int actor_id = 0;
    if (!token_item) { cJSON_Delete(root); return RE_ERR_AUTH; }
    int perm_rc = validate_session_and_permission(token_item->valuestring, PERM_CREATE_PROPERTY, &actor_id);
    if (perm_rc != 0) { cJSON_Delete(root); return perm_rc; }
    
    cJSON* prop_obj = cJSON_GetObjectItem(root, "property");
    if (!prop_obj) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }
    
    Property p;
    memset(&p, 0, sizeof(Property));
    int val_rc = map_json_to_property(prop_obj, &p);
    if (val_rc != 0) {
        cJSON_Delete(root);
        return val_rc;
    }
    p.created_by = actor_id;
    
    int new_id = 0;
    int rc = db_begin_transaction();
    if (rc != 0) {
        cJSON_Delete(root);
        return rc;
    }
    
    rc = property_repo_create(&p, &new_id);
    if (rc != 0) {
        db_rollback_transaction();
        cJSON_Delete(root);
        return rc;
    }

    rc = audit_repo_log(actor_id, "CREATE_PROPERTY", "properties", new_id, "{}", "{\"status\":\"created\"}", "127.0.0.1", "local");
    if (rc != 0) {
        db_rollback_transaction();
        cJSON_Delete(root);
        return rc;
    }
    
    rc = db_commit_transaction();
    cJSON_Delete(root);
    
    if (rc == 0) {
        cJSON* resp = cJSON_CreateObject();
        cJSON_AddNumberToObject(resp, "id", new_id);
        char* resp_str = cJSON_PrintUnformatted(resp);
        *res = strdup(resp_str);
        free(resp_str);
        cJSON_Delete(resp);
    }
    return rc;
}

int property_update(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    
    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    
    // RBAC: Validate session and EDIT_PROPERTY permission
    cJSON* token_item = cJSON_GetObjectItem(root, "token");
    int actor_id = 0;
    if (!token_item) { cJSON_Delete(root); return RE_ERR_AUTH; }
    int perm_rc = validate_session_and_permission(token_item->valuestring, PERM_EDIT_PROPERTY, &actor_id);
    if (perm_rc != 0) { cJSON_Delete(root); return perm_rc; }
    
    cJSON* id_item = cJSON_GetObjectItem(root, "id");
    cJSON* prop_obj = cJSON_GetObjectItem(root, "property");
    if (!id_item || !prop_obj) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }
    
    Property p;
    memset(&p, 0, sizeof(Property));
    p.id = id_item->valueint;
    
    int val_rc = map_json_to_property(prop_obj, &p);
    if (val_rc != 0) {
        cJSON_Delete(root);
        return val_rc;
    }
    
    int rc = db_begin_transaction();
    if (rc != 0) {
        cJSON_Delete(root);
        return rc;
    }
    
    rc = property_repo_update(&p);
    if (rc != 0) {
        db_rollback_transaction();
        cJSON_Delete(root);
        return rc;
    }
    
    audit_repo_log(actor_id, "UPDATE_PROPERTY", "properties", p.id, "{}", "{\"status\":\"updated\"}", "127.0.0.1", "local");
    
    rc = db_commit_transaction();
    cJSON_Delete(root);
    
    if (rc == 0) {
        *res = strdup("{\"status\":\"ok\"}");
    }
    return rc;
}

int property_get_all(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    
    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    
    // RBAC: Validate session and VIEW_PROPERTIES permission
    cJSON* token_item = cJSON_GetObjectItem(root, "token");
    int actor_id = 0;
    if (!token_item) { cJSON_Delete(root); return RE_ERR_AUTH; }
    int perm_rc = validate_session_and_permission(token_item->valuestring, PERM_VIEW_PROPERTIES, &actor_id);
    if (perm_rc != 0) { cJSON_Delete(root); return perm_rc; }
    
    cJSON* state = cJSON_GetObjectItem(root, "search_state");
    const char* query = NULL;
    const char* category = NULL;
    const char* listing_type = NULL;
    const char* city = NULL;
    int district = 0;
    int min_price = 0, max_price = 0, min_area = 0, max_area = 0;
    int is_archived_filter = 0; // Default: show active only
    const char* sort_col = NULL;
    int sort_asc = 0;
    int limit = 0, offset = 0;

    if (state) {
        cJSON* q = cJSON_GetObjectItem(state, "query");
        if (q) query = q->valuestring;
        
        cJSON* filters = cJSON_GetObjectItem(state, "filters");
        if (filters) {
            cJSON* cat = cJSON_GetObjectItem(filters, "category");
            if (cat) category = cat->valuestring;
            cJSON* lt = cJSON_GetObjectItem(filters, "listing_type");
            if (lt) listing_type = lt->valuestring;
            cJSON* ct = cJSON_GetObjectItem(filters, "city");
            if (ct) city = ct->valuestring;
            cJSON* dist = cJSON_GetObjectItem(filters, "district");
            if (dist) district = dist->valueint;
            cJSON* min_p = cJSON_GetObjectItem(filters, "min_price");
            if (min_p) min_price = min_p->valueint;
            cJSON* max_p = cJSON_GetObjectItem(filters, "max_price");
            if (max_p) max_price = max_p->valueint;
            cJSON* min_a = cJSON_GetObjectItem(filters, "min_area");
            if (min_a) min_area = min_a->valueint;
            cJSON* max_a = cJSON_GetObjectItem(filters, "max_area");
            if (max_a) max_area = max_a->valueint;
            
            cJSON* arch = cJSON_GetObjectItem(filters, "is_archived");
            if (arch) {
                is_archived_filter = cJSON_IsTrue(arch) ? 1 : 0;
            } else {
                is_archived_filter = -1; // Omitted means Show all
            }
        }
        
        cJSON* sorting = cJSON_GetObjectItem(state, "sorting");
        if (sorting) {
            cJSON* col = cJSON_GetObjectItem(sorting, "column");
            if (col) sort_col = col->valuestring;
            cJSON* asc = cJSON_GetObjectItem(sorting, "ascending");
            if (asc) sort_asc = cJSON_IsTrue(asc) ? 1 : 0;
        }
        
        cJSON* pag = cJSON_GetObjectItem(state, "pagination");
        if (pag) {
            cJSON* ps = cJSON_GetObjectItem(pag, "page_size");
            if (ps) limit = ps->valueint;
            cJSON* pn = cJSON_GetObjectItem(pag, "page_number");
            if (pn) {
                int page_num = pn->valueint;
                if (page_num < 1) page_num = 1;
                offset = (page_num - 1) * limit;
            }
        }
    }

    Property props[200];
    memset(props, 0, sizeof(props));
    int count = 0;
    
    int rc = property_repo_get_all(query, category, listing_type, city, district, min_price, max_price, min_area, max_area, is_archived_filter, sort_col, sort_asc, limit, offset, props, 200, &count);
    cJSON_Delete(root);
    
    if (rc != 0) return rc;
    
    cJSON* resp_root = cJSON_CreateObject();
    cJSON* props_arr = cJSON_CreateArray();

    for (int i = 0; i < count; ++i) {
        cJSON* p_obj = cJSON_CreateObject();
        cJSON_AddNumberToObject(p_obj, "id", props[i].id);
        cJSON_AddBoolToObject(p_obj, "is_archived", props[i].is_archived ? 1 : 0);
        cJSON_AddStringToObject(p_obj, "category", props[i].category);
        cJSON_AddStringToObject(p_obj, "listing_type", props[i].listing_type);
        cJSON_AddStringToObject(p_obj, "city", props[i].city);
        cJSON_AddNumberToObject(p_obj, "municipal_district", props[i].municipal_district);
        cJSON_AddStringToObject(p_obj, "address", props[i].address);
        cJSON_AddStringToObject(p_obj, "owner_phone", props[i].owner_phone);
        cJSON_AddNumberToObject(p_obj, "area_sqm", props[i].area_sqm);
        cJSON_AddNumberToObject(p_obj, "sale_price", props[i].sale_price);
        cJSON_AddNumberToObject(p_obj, "rent_deposit", props[i].rent_deposit);
        cJSON_AddNumberToObject(p_obj, "rent_monthly", props[i].rent_monthly);
        cJSON_AddStringToObject(p_obj, "date_registered", props[i].created_at);
        cJSON_AddItemToArray(props_arr, p_obj);
    }

    cJSON_AddItemToObject(resp_root, "properties", props_arr);
    char* out_str = cJSON_PrintUnformatted(resp_root);
    *res = strdup(out_str);
    free(out_str);
    cJSON_Delete(resp_root);
    
    return 0;
}

int property_get_by_id(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    
    // RBAC: Validate session and VIEW_PROPERTIES permission
    cJSON* token_item = cJSON_GetObjectItem(root, "token");
    int actor_id = 0;
    (void)actor_id;
    if (!token_item) { cJSON_Delete(root); return RE_ERR_AUTH; }
    int perm_rc = validate_session_and_permission(token_item->valuestring, PERM_VIEW_PROPERTIES, &actor_id);
    if (perm_rc != 0) { cJSON_Delete(root); return perm_rc; }
    
    cJSON* id_item = cJSON_GetObjectItem(root, "id");
    if (!id_item) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }
    int id = id_item->valueint;
    
    Property p;
    memset(&p, 0, sizeof(Property));
    int rc = property_repo_get_by_id(id, &p);
    cJSON_Delete(root);
    if (rc != 0) return rc;
    
    cJSON* p_obj = cJSON_CreateObject();
    cJSON_AddNumberToObject(p_obj, "id", p.id);
    cJSON_AddBoolToObject(p_obj, "is_archived", p.is_archived ? 1 : 0);
    cJSON_AddStringToObject(p_obj, "category", p.category);
    cJSON_AddStringToObject(p_obj, "listing_type", p.listing_type);
    cJSON_AddStringToObject(p_obj, "city", p.city);
    cJSON_AddNumberToObject(p_obj, "municipal_district", p.municipal_district);
    cJSON_AddStringToObject(p_obj, "address", p.address);
    cJSON_AddStringToObject(p_obj, "owner_phone", p.owner_phone);
    cJSON_AddNumberToObject(p_obj, "area_sqm", p.area_sqm);
    cJSON_AddNumberToObject(p_obj, "sale_price", p.sale_price);
    cJSON_AddNumberToObject(p_obj, "rent_deposit", p.rent_deposit);
    cJSON_AddNumberToObject(p_obj, "rent_monthly", p.rent_monthly);
    cJSON_AddStringToObject(p_obj, "date_registered", p.created_at);
    
    char* out_str = cJSON_PrintUnformatted(p_obj);
    *res = strdup(out_str);
    free(out_str);
    cJSON_Delete(p_obj);
    return 0;
}

int property_archive(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    
    // RBAC: Validate session and ARCHIVE_PROPERTY permission
    cJSON* token_item = cJSON_GetObjectItem(root, "token");
    int actor_id = 0;
    if (!token_item) { cJSON_Delete(root); return RE_ERR_AUTH; }
    int perm_rc = validate_session_and_permission(token_item->valuestring, PERM_ARCHIVE_PROPERTY, &actor_id);
    if (perm_rc != 0) { cJSON_Delete(root); return perm_rc; }
    cJSON* id_item = cJSON_GetObjectItem(root, "id");
    if (!id_item) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }
    int id = id_item->valueint;
    int rc = property_repo_archive(id, actor_id);
    cJSON_Delete(root);
    if (rc == 0) {
        audit_repo_log(actor_id, "ARCHIVE_PROPERTY", "properties", id, "{}", "{\"status\":\"archived\"}", "127.0.0.1", "local");
        *res = strdup("{\"status\":\"ok\"}");
    }
    return rc;
}

int property_restore(const char* req, char** res) {
    if (!req || !res) return RE_ERR_VALIDATION;
    cJSON* root = cJSON_Parse(req);
    if (!root) return RE_ERR_VALIDATION;
    
    // RBAC: Validate session and RESTORE_PROPERTY permission
    cJSON* token_item = cJSON_GetObjectItem(root, "token");
    int actor_id = 0;
    if (!token_item) { cJSON_Delete(root); return RE_ERR_AUTH; }
    int perm_rc = validate_session_and_permission(token_item->valuestring, PERM_RESTORE_PROPERTY, &actor_id);
    if (perm_rc != 0) { cJSON_Delete(root); return perm_rc; }
    cJSON* id_item = cJSON_GetObjectItem(root, "id");
    if (!id_item) {
        cJSON_Delete(root);
        return RE_ERR_VALIDATION;
    }
    int id = id_item->valueint;
    int rc = property_repo_restore(id);
    cJSON_Delete(root);
    if (rc == 0) {
        audit_repo_log(actor_id, "RESTORE_PROPERTY", "properties", id, "{}", "{\"status\":\"restored\"}", "127.0.0.1", "local");
        *res = strdup("{\"status\":\"ok\"}");
    }
    return rc;
}
