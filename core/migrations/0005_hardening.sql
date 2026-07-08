-- Migration: 0005_hardening.sql
-- Description: Add performance indexes to speed up sorting and pagination
-- Created at: 2026

CREATE INDEX IF NOT EXISTS idx_properties_list ON properties (is_archived, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties (is_archived, sale_price);
CREATE INDEX IF NOT EXISTS idx_properties_area ON properties (is_archived, area_sqm);
CREATE INDEX IF NOT EXISTS idx_properties_district ON properties (is_archived, municipal_district);
