   # Architecture Overview

   ## Data Pipeline Flow
```
   ┌─────────────────────┐
   │  Local Machine      │
   │  ┌───────────────┐  │
   │  │ job_scrape.py │  │
   │  │ (CRON: Daily) │  │
   │  └───────┬───────┘  │
   └──────────┼──────────┘
              │
              ▼
   ┌─────────────────────────┐
   │  ADLS Landing Zone      │
   │  (jobscrape_data/)      │
   └──────────┬──────────────┘
              │ File Arrival Trigger
              ▼
   ┌─────────────────────────────────────┐
   │  Databricks Workspace               │
   │  ┌──────────────────────────────┐   │
   │  │ 01_bronze_load.py            │   │
   │  │ (Read CSV → Bronze Delta)    │   │
   │  └──────────────┬───────────────┘   │
   │                 ▼                    │
   │  ┌──────────────────────────────┐   │
   │  │ 02_silver_cleaning.py        │   │
   │  │ (Validate → Silver Delta)    │   │
   │  └──────────────┬───────────────┘   │
   │                 ▼                    │
   │  ┌──────────────────────────────┐   │
   │  │ 03_gold_aggregations.sql     │   │
   │  │ (Views → Gold Layer)         │   │
   │  └──────────────────────────────┘   │
   └─────────────────────────────────────┘
```

   ## Components

   ### 1. Local Scraper (`job_scrape.py`)
   - Runs on local machine via CRON scheduler (daily at 2 AM recommended)
   - Scrapes job listings from TheProtocol.it
   - Uses Playwright for dynamic content handling
   - Extracts structured data using BeautifulSoup
   - Exports data as CSV with timestamp: `the_it_protocol_jobs_YYYYMMdd_HHmmss.csv`
   - Uploads to ADLS landing zone

   **Technologies:**
   - Playwright (web automation)
   - BeautifulSoup (HTML parsing)
   - Azure Storage SDK (ADLS upload)

   ### 2. Bronze Layer (`01_bronze_load.py`)
   - Triggered automatically when CSV lands in ADLS
   - Loads raw CSV data into Bronze Delta table
   - Preserves all data as-is (no transformations)
   - Adds metadata: ingestion timestamp, source file, processing date
   - Loads only the latest CSV file by filename timestamp

   **Key Features:**
   - Latest file selection
   - Metadata enrichment
   - Full audit trail

   ### 3. Silver Layer (`02_silver_cleaning.py`)
   - Validates data quality
   - Enforces required fields: job_listing_id, job_title, company_name, job_level, contract_type
   - Logs dropped records with failure reasons
   - Performs Bronze-to-Silver reconciliation
   - Creates cleaned, validated data for analytics

   **Key Features:**
   - Data validation
   - Quality checks
   - Dropped records logging
   - Reconciliation reporting

   ### 4. Gold Layer (`03_gold_aggregations.sql`)
   - Creates business-ready views for analytics and reporting
   - Aggregations by job level, company, technology stack
   - Salary analysis
   - No data is modified, only curated views created

   **Key Views:**
   - `v_jobs_summary` - All jobs with key fields
   - `v_jobs_by_level` - Distribution by job level
   - `v_top_companies` - Top hiring companies
   - `v_technology_demand` - Technology stack analysis
   - `v_salary_analysis` - Remuneration breakdown

   ## Data Quality

   The pipeline includes comprehensive validation:
   - **Required fields validation**: Checks all critical fields are populated
   - **Dropped records logging**: Tracks all failed records with reasons
   - **Reconciliation checks**: Verifies record counts across layers
   - **Audit trail**: Timestamps and source tracking at each layer

   ## Orchestration

   - **Local Scraper**: CRON scheduled (e.g., `0 2 * * * /path/to/job_scrape.py`)
   - **Databricks**: File arrival trigger on ADLS path `/Volumes/jobscrape/landing/jobscrape_data/*.csv`
   - **Task Chain**: Bronze → Silver → Gold (automatic sequential execution)

   ## Security

   - **Credentials**: Managed via environment variables and Azure Secrets
   - **Storage**: Azure ADLS with role-based access control (RBAC)
   - **Catalog**: Unity Catalog with data governance
   - **Audit**: All operations logged with timestamps and sources

   ## Performance Considerations

   - Latest file selection by timestamp (efficient)
   - Batch processing (no streaming overhead)
   - Delta Lake optimization (Parquet format, automatic optimizations)
   - Medallion architecture (separation of concerns, independent scaling)
  