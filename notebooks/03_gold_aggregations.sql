   -- Databricks notebook source
   -- Gold Layer: Business-Ready Aggregations & Analytics
   
   -- COMMAND ----------
   
   -- Use the jobscrape catalog and silver schema
   USE CATALOG jobscrape;
   USE SCHEMA silver;
   
   -- COMMAND ----------
   
   -- Create Gold Schema if it doesn't exist
   CREATE SCHEMA IF NOT EXISTS jobscrape.gold;
   
   -- COMMAND ----------
   
   -- Gold View 1: Jobs Summary
   CREATE OR REPLACE VIEW jobscrape.gold.v_jobs_summary AS
   SELECT
       job_listing_id,
       job_title,
       company_name,
       location,
       job_level,
       contract_type,
       work_mode,
       remuneration,
       frequency,
       gross_or_net,
       expiration_date,
       ingestion_date,
       _silver_transformation_time AS last_updated
   FROM jobscrape.silver.jobs_clean
   ORDER BY ingestion_date DESC, job_title;
   
   -- COMMAND ----------
   
   -- Gold View 2: Jobs by Job Level Distribution
   CREATE OR REPLACE VIEW jobscrape.gold.v_jobs_by_level AS
   SELECT
       job_level,
       COUNT(*) AS job_count,
       COUNT(DISTINCT company_name) AS company_count,
       ingestion_date
   FROM jobscrape.silver.jobs_clean
   WHERE job_level IS NOT NULL
   GROUP BY job_level, ingestion_date
   ORDER BY ingestion_date DESC, job_count DESC;
   
   -- COMMAND ----------
   
   -- Gold View 3: Top Companies by Job Count
   CREATE OR REPLACE VIEW jobscrape.gold.v_top_companies AS
   SELECT
       company_name,
       COUNT(*) AS open_positions,
       COUNT(DISTINCT job_level) AS job_levels_offered,
       COLLECT_LIST(DISTINCT job_title) AS job_titles,
       ingestion_date
   FROM jobscrape.silver.jobs_clean
   WHERE company_name IS NOT NULL
   GROUP BY company_name, ingestion_date
   ORDER BY open_positions DESC, ingestion_date DESC;
   
   -- COMMAND ----------
   
   -- Gold View 4: Technology Stack Analysis
   CREATE OR REPLACE VIEW jobscrape.gold.v_technology_demand AS
   SELECT
       EXPLODE(SPLIT(expected_technologies, ',')) AS technology,
       COUNT(*) AS job_count,
       ingestion_date
   FROM jobscrape.silver.jobs_clean
   WHERE expected_technologies IS NOT NULL AND expected_technologies != ''
   GROUP BY TRIM(technology), ingestion_date
   ORDER BY job_count DESC, ingestion_date DESC;
   
   -- COMMAND ----------
   
   -- Gold View 5: Salary Distribution
   CREATE OR REPLACE VIEW jobscrape.gold.v_salary_analysis AS
   SELECT
       job_level,
       contract_type,
       COUNT(*) AS count,
       COUNT(DISTINCT company_name) AS companies,
       ingestion_date
   FROM jobscrape.silver.jobs_clean
   WHERE remuneration IS NOT NULL
   GROUP BY job_level, contract_type, ingestion_date
   ORDER BY ingestion_date DESC;
   
   -- COMMAND ----------
   
   SELECT 'Gold Layer Views Created Successfully' AS status;
   