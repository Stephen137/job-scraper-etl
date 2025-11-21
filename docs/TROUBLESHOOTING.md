   # Troubleshooting Guide

   ## Local Scraper Issues

   ### Issue: "Timeout 30000ms exceeded"
   **Cause**: theprotocol.it website is slow to respond  
   **Solution**:
   - Increase timeout in `job_scrape.py`: `page.goto(url, timeout=60000)`
   - Increase delay between pages: `DELAY_BETWEEN_PAGES=2.0` in `.env`
   - Try running at off-peak hours

   ### Issue: "Missing required environment variables"
   **Cause**: `.env` file not configured  
   **Solution**:
```bash
   # Verify .env exists and is in the right place
   cat .env

   # Make sure all required variables are set
   echo $TENANT_ID
   echo $CLIENT_ID
```

   ### Issue: "Authentication failed to ADLS"
   **Cause**: Invalid Service Principal credentials  
   **Solution**:
   - Verify credentials in `.env`
   - Check Service Principal still exists in Azure AD
   - Verify RBAC role assignment in storage account
   - Try re-generating Service Principal credentials

   ### Issue: Scraper ran but no file in ADLS
   **Cause**: Azure upload failed silently  
   **Solution**:
   - Check `logs/job_scrape.log` for upload errors
   - Verify container name in `.env`: `CONTAINER_NAME=your-container-name`
   - Check Azure Storage permissions

   ### Issue: "No job listings found on page 1"
   **Cause**: Website HTML structure changed or blocked scraper  
   **Solution**:
   - Check if website is accessible: `curl https://theprotocol.it`
   - Review BeautifulSoup selectors in helper functions
   - Check if Playwright is installed: `python -c "from playwright.sync_api import sync_playwright"`

   ## Databricks Issues

   ### Issue: "File not triggering workflow"
   **Cause**: File arrival pattern doesn't match  
   **Solution**:
   - Verify ADLS path: `/Volumes/jobscrape/landing/jobscrape_data/`
   - Verify file pattern: `*.csv`
   - Check file was actually uploaded to ADLS
   - Try manually running notebook: Workflows → Run now

   ### Issue: "Schema mismatch" error in Bronze notebook
   **Cause**: CSV column names don't match defined schema  
   **Solution**:
   - Check CSV headers match `jobs_schema` in `01_bronze_load.py`
   - Verify scraper is outputting correct column names
   - Update schema if scraper logic changed

   ### Issue: "Unity Catalog not found"
   **Cause**: Catalog `jobscrape` doesn't exist  
   **Solution**:
```sql
   -- Create missing catalog
   CREATE CATALOG IF NOT EXISTS jobscrape;

   -- Create missing schemas
   CREATE SCHEMA IF NOT EXISTS jobscrape.bronze;
   CREATE SCHEMA IF NOT EXISTS jobscrape.silver;
   CREATE SCHEMA IF NOT EXISTS jobscrape.gold;
```

   ### Issue: "Dropped records more than expected"
   **Cause**: Data quality validation is too strict or scraper failed  
   **Solution**:
   - Check `jobscrape.silver.dropped_records_log`:
```sql
     SELECT reason_dropped, COUNT(*) as count
     FROM jobscrape.silver.dropped_records_log
     GROUP BY reason_dropped;
```
   - If many timeouts: increase scraper timeout
   - If missing fields: check scraper extraction logic

   ### Issue: "Bronze to Silver reconciliation failed"
   **Cause**: Records not matching between layers  
   **Solution**:
   - Check Bronze table count:
```sql
     SELECT COUNT(*) FROM jobscrape.bronze.jobs_raw;
```
   - Check Silver table count:
```sql
     SELECT COUNT(*) FROM jobscrape.silver.jobs_clean;
```
   - Review Silver notebook output for reconciliation details

   ## General Debugging

   ### Enable Debug Logging
   In `.env`:
```
   LOG_LEVEL=DEBUG
```

   ### Manual CSV Testing
```python
   import pandas as pd

   # Load and inspect CSV
   df = pd.read_csv('the_it_protocol_jobs_20251121_144752.csv')
   print(df.head())
   print(df.columns)
   print(df.dtypes)
   print(df.isnull().sum())
```

   ### Verify Git Setup
```bash
   # Check git status
   git status

   # Check git log
   git log --oneline

   # Verify remote
   git remote -v
```

   ## Getting Help

   1. Check logs first (local: `logs/job_scrape.log`, Databricks: workflow run history)
   2. Review this troubleshooting guide
   3. Check ARCHITECTURE.md and SETUP_GUIDE.md
   4. Open an issue on GitHub with:
      - Error message/log snippet
      - Steps to reproduce
      - What you've already tried
 