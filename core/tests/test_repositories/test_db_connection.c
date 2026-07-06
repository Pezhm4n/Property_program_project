/**
 * @file test_db_connection.c
 * @brief Unit tests for database connection lifecycle
 * @copyright Real Estate Management System
 */
#include "db_connection.h"
#include <stdio.h>
#include <assert.h>

int main() {
    printf("Running test_db_connection...\n");
    
    // Init memory database
    int rc = db_init(":memory:", 5000);
    assert(rc == 0);
    assert(db_get_connection() != NULL);
    
    rc = db_execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY);");
    assert(rc == 0);
    
    rc = db_begin_transaction();
    assert(rc == 0);
    
    rc = db_execute("INSERT INTO test_table (id) VALUES (1);");
    assert(rc == 0);
    
    rc = db_commit_transaction();
    assert(rc == 0);
    
    db_close();
    assert(db_get_connection() == NULL);
    
    printf("test_db_connection PASSED\n");
    return 0;
}
