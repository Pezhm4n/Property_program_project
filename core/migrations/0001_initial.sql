-- Migration: 0001_initial.sql
-- Description: Core schema migrations
-- Created at: 2026

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE CHECK(length(username) >= 3),
    password_hash TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    national_id TEXT NOT NULL UNIQUE CHECK(length(national_id) = 10),
    phone TEXT NOT NULL CHECK(length(phone) = 11 AND phone LIKE '09%'),
    role TEXT NOT NULL CHECK(role IN ('admin', 'agent')),
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TEXT,
    is_disabled INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    is_archived INTEGER NOT NULL DEFAULT 0,
    category TEXT NOT NULL CHECK(category IN ('residential', 'office', 'land', 'مسکونی', 'تجاری', 'زمین')),
    listing_type TEXT NOT NULL CHECK(listing_type IN ('sale', 'rent', 'فروش', 'اجاره', 'رهن')),
    city TEXT NOT NULL DEFAULT 'تهران',
    municipal_district INTEGER NOT NULL,
    address TEXT NOT NULL,
    owner_phone TEXT NOT NULL CHECK(length(owner_phone) = 11),
    area_sqm INTEGER NOT NULL DEFAULT 0,
    sale_price INTEGER NOT NULL DEFAULT 0,
    rent_deposit INTEGER NOT NULL DEFAULT 0,
    rent_monthly INTEGER NOT NULL DEFAULT 0,
    created_by INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    archived_at TEXT,
    archived_by INTEGER,
    FOREIGN KEY(created_by) REFERENCES users(id),
    FOREIGN KEY(archived_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id INTEGER,
    action TEXT NOT NULL,
    entity TEXT NOT NULL,
    entity_id INTEGER,
    old_values_json TEXT,
    new_values_json TEXT,
    ip TEXT,
    machine TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(actor_id) REFERENCES users(id)
);

-- Seed default admin user (using SHA256 of 'admin123' or simple password for stub)
INSERT OR IGNORE INTO users (username, password_hash, first_name, last_name, national_id, phone, role, created_at)
VALUES ('admin', 'password123', 'مدیر', 'سیستم', '0012345678', '09123456789', 'admin', datetime('now'));
