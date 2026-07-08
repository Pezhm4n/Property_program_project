-- Migration: 0004_rbac.sql
-- Description: Implement Enterprise RBAC and Sessions
-- Created at: 2026

PRAGMA foreign_keys=off;

-- 1. Create Roles Table
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- 2. Create Permissions Table
CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- 3. Create Role Permissions Join Table
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER,
    permission_id INTEGER,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY(permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

-- 4. Create Sessions Table (for rolling 30-min timeouts & caching)
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE,
    permissions_cache TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_activity TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. Seed default roles
INSERT INTO roles (id, name, description) VALUES (1, 'admin', 'System Administrator');
INSERT INTO roles (id, name, description) VALUES (2, 'user', 'Standard User (Agent)');

-- 6. Seed all permissions
INSERT INTO permissions (id, name) VALUES (1, 'VIEW_PROPERTIES');
INSERT INTO permissions (id, name) VALUES (2, 'CREATE_PROPERTY');
INSERT INTO permissions (id, name) VALUES (3, 'EDIT_PROPERTY');
INSERT INTO permissions (id, name) VALUES (4, 'DELETE_PROPERTY');
INSERT INTO permissions (id, name) VALUES (5, 'ARCHIVE_PROPERTY');
INSERT INTO permissions (id, name) VALUES (6, 'RESTORE_PROPERTY');
INSERT INTO permissions (id, name) VALUES (7, 'VIEW_REPORTS');
INSERT INTO permissions (id, name) VALUES (8, 'VIEW_FINANCIAL_REPORTS');
INSERT INTO permissions (id, name) VALUES (9, 'MANAGE_USERS');
INSERT INTO permissions (id, name) VALUES (10, 'CHANGE_USER_ROLE');
INSERT INTO permissions (id, name) VALUES (11, 'RESET_PASSWORD');
INSERT INTO permissions (id, name) VALUES (12, 'BACKUP_DATABASE');
INSERT INTO permissions (id, name) VALUES (13, 'RESTORE_DATABASE');
INSERT INTO permissions (id, name) VALUES (14, 'VIEW_SETTINGS');
INSERT INTO permissions (id, name) VALUES (15, 'VIEW_AUDIT_LOG');
INSERT INTO permissions (id, name) VALUES (16, 'EXPORT_REPORTS');

-- 7. Bind Permissions to Admin (All permissions)
INSERT INTO role_permissions (role_id, permission_id) 
SELECT 1, id FROM permissions;

-- 8. Bind Permissions to User (Limited permissions)
INSERT INTO role_permissions (role_id, permission_id) 
SELECT 2, id FROM permissions WHERE name IN (
    'VIEW_PROPERTIES', 'CREATE_PROPERTY', 'EDIT_PROPERTY', 'ARCHIVE_PROPERTY'
);

-- 9. Recreate users table to replace 'role' string with 'role_id' and add 'last_login_at'
CREATE TABLE users_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL DEFAULT 2,
    username TEXT NOT NULL UNIQUE CHECK(length(username) >= 3),
    password_hash TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    national_id TEXT NOT NULL UNIQUE CHECK(length(national_id) = 10),
    phone TEXT NOT NULL CHECK(length(phone) = 11 AND phone LIKE '09%'),
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TEXT,
    is_disabled INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    last_login_at TEXT,
    FOREIGN KEY(role_id) REFERENCES roles(id)
);

-- 10. Copy data (map 'admin' -> 1, 'agent' -> 2)
INSERT INTO users_new (
    id, role_id, username, password_hash, first_name, last_name, 
    national_id, phone, failed_attempts, locked_until, is_disabled, 
    created_at, updated_at
)
SELECT 
    id, 
    CASE WHEN role = 'admin' THEN 1 ELSE 2 END,
    username, password_hash, first_name, last_name, 
    national_id, phone, failed_attempts, locked_until, is_disabled, 
    created_at, updated_at
FROM users;

-- 11. Drop and Rename
DROP TABLE users;
ALTER TABLE users_new RENAME TO users;

PRAGMA foreign_keys=on;
