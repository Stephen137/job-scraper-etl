-- Databricks notebook source
SELECT 
  company_name,
  days_left,
  job_title,
  expected_technologies,
  responsibilities,
  requirements,
  min_salary,
  max_salary,
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
FROM jobscrape.gold.v_jobs_expiring_soon
WHERE days_left <= 3

--Here are the DataFrames in the session: