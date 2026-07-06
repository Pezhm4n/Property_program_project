-- Migration: 0002_report_views.sql
-- Description: Standard views for reporting
-- Created at: 2026

CREATE VIEW IF NOT EXISTS vw_active_properties AS
SELECT * FROM properties WHERE is_archived = 0;

CREATE VIEW IF NOT EXISTS vw_sales_summary AS
SELECT SUM(sale_price) AS total_sales_value, COUNT(*) AS sales_count
FROM properties
WHERE is_archived = 0 AND listing_type IN ('sale', 'فروش');

CREATE VIEW IF NOT EXISTS vw_agent_statistics AS
SELECT created_by AS agent_id, COUNT(*) AS property_count, MAX(created_at) AS last_active
FROM properties
GROUP BY created_by;

CREATE VIEW IF NOT EXISTS vw_archived_properties AS
SELECT * FROM properties WHERE is_archived = 1;
