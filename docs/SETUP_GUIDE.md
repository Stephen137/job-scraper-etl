   # Complete Setup Guide

   ## Prerequisites

   - Python 3.8+ (local scraper)
   - Databricks workspace with Unity Catalog enabled
   - Azure Storage Account with ADLS Gen2
   - Service Principal with Storage Blob Data Contributor role
   - Git installed on local machine

   ## Local Setup (Web Scraper)

   ### 1. Clone Repository
```bash
   git clone https://github.com/yourusername/job-scraper-etl.git
   cd job-scraper-etl
```

   ### 2. Create Virtual Environment
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

   ### 3. Install Dependencies
```bash
   pip install -r requirements.txt
```

   ### 4. Configure Environment Variables
```bash
   cp .env.example .env
```

   Edit `.env` with your Azure credentials:
```
   TENANT_ID=your-actual-tenant-id
   CLIENT_ID=your-actual-client-id
   CLIENT_SECRET=your-actual-client-secret
   STORAGE_ACCOUNT_NAME=your-storage-account
   CONTAINER_NAME=your-container-name
   MAX_PAGES=5
   DELAY_BETWEEN_PAGES=1.0
```

   ### 5. Test the Scraper
```bash
   python job_scrape.py
```

   ### 6. Schedule with CRON (Linux/Mac)
```bash
   # Edit crontab
   crontab -e

   # Add this line to run daily at 2 AM
   0 2 * * * cd /path/to/job-scraper-etl && /path/to/venv/bin/python job_scrape.py >> logs/job_scrape.log 2>&1
```

   For Windows, use Task Scheduler instead.

   ## Databricks Setup

   ### 1. Create Cluster
   - Go to Databricks workspace
   - Create new cluster with:
     - Runtime: 13.3 LTS or later
     - Python: 3.10+
     - No additional packages needed (Delta Lake included)

   ### 2. Create Catalog & Schemas
```sql
   CREATE CATALOG IF NOT EXISTS jobscrape;
   CREATE SCHEMA IF NOT EXISTS jobscrape.bronze;
   CREATE SCHEMA IF NOT EXISTS jobscrape.silver;
   CREATE SCHEMA IF NOT EXISTS jobscrape.gold;
```

   ### 3. Upload Notebooks
   - In Databricks workspace, create a folder: `/Users/[your-email]/job-scraper-etl/`
   - Upload three notebooks:
     - `notebooks/01_bronze_load.py`
     - `notebooks/02_silver_cleaning.py`
     - `notebooks/03_gold_aggregations.sql`
     - `notebooks/04_jobs_expiring_soon.sql`
     
   ### 4. Create File Arrival Trigger Job
   1. Go to Workflows (left sidebar)
   2. Click "Create job"
   3. Configure:
      - **Name**: `job-scraper-etl-pipeline`
      - **Trigger type**: "File arrival in ADLS"
      - **Path**: `/Volumes/jobscrape/landing/jobscrape_data/`
      - **File pattern**: `*.csv`
   4. Add tasks in sequence:
      - Task 1: Run `01_bronze_load.py`
      - Task 2: Run `02_silver_cleaning.py` (depends on Task 1)
      - Task 3: Run `03_gold_aggregations.sql` (depends on Task 2)
      - Task 4: Run `04_jobs_expiring_soon.sql` (depends on Task 3)
   5. Save and activate

   ### 5. Verify Setup
```sql
   -- Check if catalog was created
   SELECT * FROM jobscrape.bronze.jobs_raw LIMIT 5;

   -- Check silver layer
   SELECT * FROM jobscrape.silver.jobs_clean LIMIT 5;

   -- Check gold views
   SELECT * FROM jobscrape.gold.v_jobs_summary LIMIT 5;
```

   ## Azure Storage Setup

   ### 1. Create Storage Account
   - In Azure Portal, create Storage Account
   - Enable "Hierarchical namespace" (ADLS Gen2)

   ### 2. Create Service Principal
```bash
   # Using Azure CLI
   az ad sp create-for-rbac --name job-scraper-sp
```

   Copy the output:
   - `appId` → `CLIENT_ID`
   - `password` → `CLIENT_SECRET`
   - `tenant` → `TENANT_ID`

   ### 3. Grant RBAC Role
   - In Azure Portal, go to Storage Account
   - Access Control (IAM)
   - Add role assignment: "Storage Blob Data Contributor"
   - Assign to your Service Principal

   ### 4. Create Container
```bash
   # Using Azure CLI
   az storage container create \
     --name jobscrape-landing \
     --account-name yourstorageaccount \
     --auth-mode login
```

   ## Testing & Validation

   ### Local Scraper Test
```bash
   # Test with 1 page only
   python job_scrape.py  # Edit job_scrape.py to set max_pages=1
```

   ### Databricks Test
   1. Manually trigger the notebook: Click "Run all"
   2. Check output tables:
```sql
      SELECT COUNT(*) FROM jobscrape.bronze.jobs_raw;
      SELECT COUNT(*) FROM jobscrape.silver.jobs_clean;
```
   3. Review dropped records:
```sql
      SELECT * FROM jobscrape.silver.dropped_records_log;
```

   ### End-to-End Test
   1. Run local scraper
   2. Wait for file to upload to ADLS (check logs)
   3. Check Databricks Workflows for automatic trigger
   4. Verify data in Gold layer views

   ## Monitoring

   ### Local Logs
   - Check `logs/job_scrape.log` for scraper execution logs
   - Look for `⚠️ Error extracting data from detail page` warnings

   ### Databricks Logs
   - Go to Workflows → job-scraper-etl-pipeline → Run history
   - Click on run to see detailed logs
   - Check `jobscrape.silver.dropped_records_log` for data quality issues

   ## Troubleshooting

   See [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.
   