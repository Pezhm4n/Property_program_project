-- Migration: 0003_add_search_indices.sql
-- Description: Add search performance indices on properties table
-- Created at: 2026

CREATE INDEX IF NOT EXISTS idx_properties_search ON properties (city, category, listing_type);
