-- Databricks notebook source
-- Gold Layer: Analytics and Business Insights
-- Creates views for BI and reporting

-- COMMAND ----------

USE CATALOG jobscrape;
CREATE SCHEMA IF NOT EXISTS gold;
USE CATALOG jobscrape;
USE SCHEMA gold;

-- COMMAND ----------

-- ===== VIEW 1: Job Market Overview =====
-- Summary of job distribution by key dimensions

CREATE OR REPLACE VIEW v_job_market_overview AS
SELECT 
    COUNT(DISTINCT job_listing_id) as total_active_listings,
    COUNT(DISTINCT company_name) as total_companies,
    COUNT(DISTINCT CASE WHEN min_salary IS NOT NULL THEN job_listing_id END) as listings_with_salary,
    ROUND(COUNT(DISTINCT CASE WHEN min_salary IS NOT NULL THEN job_listing_id END) * 100.0 / COUNT(DISTINCT job_listing_id), 2) as salary_coverage_pct,
    CURRENT_DATE as snapshot_date
FROM jobscrape.silver.jobs_cleaned;

SELECT * FROM v_job_market_overview;

-- COMMAND ----------

-- ===== VIEW 2: Jobs by Location =====
-- Shows which locations have the most job opportunities

CREATE OR REPLACE VIEW v_jobs_by_location AS
SELECT 
    location,
    COUNT(DISTINCT job_listing_id) as job_count,
    COUNT(DISTINCT company_name) as company_count,
    ROUND(AVG(min_salary), 0) as avg_min_salary,
    ROUND(AVG(max_salary), 0) as avg_max_salary,
    COUNT(DISTINCT CASE WHEN min_salary IS NOT NULL THEN job_listing_id END) as listings_with_salary
FROM jobscrape.silver.jobs_cleaned
WHERE location IS NOT NULL
GROUP BY location
ORDER BY job_count DESC;

SELECT * FROM v_jobs_by_location;

-- COMMAND ----------

-- ===== VIEW 3: Jobs by Contract Type =====
-- Distribution of employment types in the market

CREATE OR REPLACE VIEW v_jobs_by_contract_type AS
SELECT 
    contract_type,
    COUNT(DISTINCT job_listing_id) as job_count,
    COUNT(DISTINCT company_name) as company_count,
    ROUND(AVG(min_salary), 0) as avg_min_salary,
    ROUND(AVG(max_salary), 0) as avg_max_salary,
    ROUND(COUNT(DISTINCT CASE WHEN min_salary IS NOT NULL THEN job_listing_id END) * 100.0 / COUNT(DISTINCT job_listing_id), 2) as salary_coverage_pct
FROM jobscrape.silver.jobs_cleaned
WHERE contract_type IS NOT NULL
GROUP BY contract_type
ORDER BY job_count DESC;

SELECT * FROM v_jobs_by_contract_type;

-- COMMAND ----------

-- ===== VIEW 4: Jobs by Work Mode =====
-- Shows market preference for remote, hybrid, and office work

CREATE OR REPLACE VIEW v_jobs_by_work_mode AS
SELECT 
    work_mode,
    COUNT(DISTINCT job_listing_id) as job_count,
    COUNT(DISTINCT company_name) as company_count,
    ROUND(AVG(min_salary), 0) as avg_min_salary,
    ROUND(AVG(max_salary), 0) as avg_max_salary,
    ROUND(COUNT(DISTINCT CASE WHEN min_salary IS NOT NULL THEN job_listing_id END) * 100.0 / COUNT(DISTINCT job_listing_id), 2) as salary_coverage_pct
FROM jobscrape.silver.jobs_cleaned
WHERE work_mode IS NOT NULL
GROUP BY work_mode
ORDER BY job_count DESC;

SELECT * FROM v_jobs_by_work_mode;

-- COMMAND ----------

-- ===== VIEW 5: Jobs by Experience Level =====
-- Distribution by junior, mid, senior levels

CREATE OR REPLACE VIEW v_jobs_by_level AS
SELECT 
    job_level,
    COUNT(DISTINCT job_listing_id) as job_count,
    COUNT(DISTINCT company_name) as company_count,
    ROUND(AVG(min_salary), 0) as avg_min_salary,
    ROUND(AVG(max_salary), 0) as avg_max_salary,
    ROUND(COUNT(DISTINCT CASE WHEN min_salary IS NOT NULL THEN job_listing_id END) * 100.0 / COUNT(DISTINCT job_listing_id), 2) as salary_coverage_pct
FROM jobscrape.silver.jobs_cleaned
WHERE job_level IS NOT NULL
GROUP BY job_level
ORDER BY job_count DESC;

SELECT * FROM v_jobs_by_level;

-- COMMAND ----------

-- ===== VIEW 6: Salary Insights =====
-- Detailed salary analysis across the market

CREATE OR REPLACE VIEW v_salary_insights AS
SELECT 
    'Overall Market' as segment,
    COUNT(DISTINCT job_listing_id) as job_count,
    ROUND(AVG(min_salary), 0) as avg_min_salary,
    ROUND(AVG(max_salary), 0) as avg_max_salary,
    ROUND(MIN(min_salary), 0) as min_salary_lowest,
    ROUND(MAX(max_salary), 0) as max_salary_highest,
    ROUND(PERCENTILE(min_salary, 0.25), 0) as q1_min_salary,
    ROUND(PERCENTILE(min_salary, 0.5), 0) as median_min_salary,
    ROUND(PERCENTILE(min_salary, 0.75), 0) as q3_min_salary
FROM jobscrape.silver.jobs_cleaned
WHERE min_salary IS NOT NULL;

SELECT * FROM v_salary_insights;

-- COMMAND ----------

-- ===== VIEW 7: Top Technologies in Demand =====
-- Extract and rank the most requested technologies
-- Note: This parses the comma-separated expected_technologies field

CREATE OR REPLACE VIEW v_top_technologies AS
WITH tech_split AS (
    SELECT 
        TRIM(col) as technology,
        job_listing_id,
        company_name
    FROM jobscrape.silver.jobs_cleaned,
    LATERAL EXPLODE(SPLIT(expected_technologies, ',')) col
    WHERE expected_technologies IS NOT NULL AND expected_technologies != ''
)
SELECT 
    technology,
    COUNT(DISTINCT job_listing_id) as job_count,
    ROUND(COUNT(DISTINCT job_listing_id) * 100.0 / (SELECT COUNT(DISTINCT job_listing_id) FROM jobscrape.silver.jobs_cleaned), 2) as pct_of_all_jobs,
    COUNT(DISTINCT company_name) as company_count
FROM tech_split
GROUP BY technology
HAVING COUNT(DISTINCT job_listing_id) > 5  -- Filter out rare technologies
ORDER BY job_count DESC
LIMIT 50;

SELECT * FROM v_top_technologies;

-- COMMAND ----------

-- ===== VIEW 8: Job Expiry Tracking =====
-- Monitor which jobs are expiring soon

CREATE OR REPLACE VIEW v_jobs_expiring_soon AS
SELECT 
    company_name,
    days_left,
    job_title,
    min_salary,
    max_salary,
    expected_technologies,
    responsibilities,
    requirements,
    location,
    work_mode,
    contract_type,
    job_url,
    CASE 
        WHEN days_left < 0 THEN 'Expired'
        WHEN days_left = 0 THEN 'Expires Today'
        WHEN days_left <= 3 THEN 'Expires Very Soon (1-3 days)'
        WHEN days_left <= 7 THEN 'Expires Soon (4-7 days)'
        WHEN days_left <= 14 THEN 'Expires in 1-2 weeks'
        ELSE 'More than 2 weeks left'
    END as expiry_status
FROM jobscrape.silver.jobs_cleaned
ORDER BY days_left ASC;

SELECT * FROM v_jobs_expiring_soon LIMIT 20;

-- COMMAND ----------

-- ===== VIEW 9: Company Hiring Activity =====
-- Shows which companies are posting the most jobs

CREATE OR REPLACE VIEW v_top_hiring_companies AS
SELECT 
    company_name,
    COUNT(DISTINCT job_listing_id) as open_positions,
    COUNT(DISTINCT job_title) as unique_roles,
    ROUND(AVG(min_salary), 0) as avg_min_salary,
    ROUND(AVG(max_salary), 0) as avg_max_salary,
    MAX(job_title) as sample_role
FROM jobscrape.silver.jobs_cleaned
WHERE company_name IS NOT NULL
GROUP BY company_name
HAVING COUNT(DISTINCT job_listing_id) >= 2  -- Only companies with 2+ listings
ORDER BY open_positions DESC
LIMIT 50;

SELECT * FROM v_top_hiring_companies;

-- COMMAND ----------

-- ===== VIEW 10: Market Heatmap - Location + Work Mode =====
-- Cross-tabulation of locations vs work modes

CREATE OR REPLACE VIEW v_market_heatmap AS
SELECT 
    location,
    work_mode,
    COUNT(DISTINCT job_listing_id) as job_count,
    ROUND(AVG(min_salary), 0) as avg_min_salary,
    ROUND(AVG(max_salary), 0) as avg_max_salary
FROM jobscrape.silver.jobs_cleaned
WHERE location IS NOT NULL AND work_mode IS NOT NULL
GROUP BY location, work_mode
ORDER BY job_count DESC;

SELECT * FROM v_market_heatmap;

-- COMMAND ----------

-- ===== SUMMARY =====
-- Display all gold layer tables created

SHOW VIEWS IN jobscrape.gold;

-- COMMAND ----------

-- Quick Dashboard Data
SELECT '=== GOLD LAYER SUMMARY ===' as metric, '' as value
UNION ALL
SELECT 'Total Active Listings', CAST((SELECT COUNT(*) FROM jobscrape.silver.jobs_cleaned) AS STRING)
UNION ALL
SELECT 'Listings with Salary Data', CAST((SELECT COUNT(*) FROM jobscrape.silver.jobs_cleaned WHERE min_salary IS NOT NULL) AS STRING)
UNION ALL
SELECT 'Top Location', (SELECT location FROM jobs_by_location ORDER BY job_count DESC LIMIT 1)
UNION ALL
SELECT 'Most Common Work Mode', (SELECT work_mode FROM jobs_by_work_mode ORDER BY job_count DESC LIMIT 1)
UNION ALL
SELECT 'Top Technology', (SELECT technology FROM top_technologies ORDER BY job_count DESC LIMIT 1);