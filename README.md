# Complete GitHub Setup Guide: Job Scraper ETL

Complete step-by-step instructions from creating a GitHub repo to your first commit and push.

---

## Step 1: Create Repository on GitHub

### 1.1 Go to GitHub
- Open https://github.com in your browser
- Click the **+** icon in the top right → **New repository**

### 1.2 Configure Repository
- **Repository name**: `job-scraper-etl`
- **Description**: `Production-grade ETL pipeline for scraping TheProtocol.it job listings with Databricks`
- **Visibility**: Choose **Public** (for portfolio) or **Private** (for confidential)
- **Initialize this repository with**:
  - ✅ Add a README file
  - ✅ Add .gitignore (select **Python**)
  - ✅ Choose a license (**MIT** recommended)

### 1.3 Create Repository
Click **Create repository**

You now have an empty repo on GitHub! ✅

---

## Step 2: Clone Repository Locally

### 2.1 Get Repository URL
- On your GitHub repo page, click the green **Code** button
- Copy the HTTPS URL (e.g., `https://github.com/yourusername/job-scraper-etl.git`)

### 2.2 Open Terminal/Command Prompt
```bash
# Navigate to where you want to store your project
cd ~/Documents  # or any preferred location

# Clone the repository
git clone https://github.com/yourusername/job-scraper-etl.git

# Navigate into the project
cd job-scraper-etl
```

Verify you're in the right location:
```bash
pwd  # On Mac/Linux - shows current path
cd   # On Windows - shows current path
ls   # List files in directory
```

You should see: `README.md`, `.gitignore`, `LICENSE`

---

## Step 3: Create Project Structure from Command Line

### 3.1 Create Directories
```bash
# Create main directories
mkdir -p helper_functions
mkdir -p notebooks
mkdir -p config
mkdir -p docs
mkdir -p tests
mkdir -p logs

# Verify structure
ls -la  # See all directories created
```

You should see:
```
.
├── helper_functions/
├── notebooks/
├── config/
├── docs/
├── tests/
├── logs/
├── README.md
├── .gitignore
└── LICENSE
```

---

## Step 4: Create Configuration Files

### 4.1 Create requirements.txt
```bash
cat > requirements.txt << 'EOF'
# Web Scraping
playwright==1.40.0
beautifulsoup4==4.12.2

# Azure Storage & Authentication
azure-identity==1.14.0
azure-storage-blob==12.19.0

# Configuration Management
python-dotenv==1.0.0

# Data Processing
pandas==2.1.3

# Utilities
requests==2.31.0

# Development & Testing (Optional)
pytest==7.4.3
black==23.11.0
flake8==6.1.0
EOF
```

Verify it was created:
```bash
cat requirements.txt
```

### 4.2 Create .env.example
```bash
cat > .env.example << 'EOF'
# ================================================================
# Azure Storage Configuration
# ================================================================
TENANT_ID=your-azure-tenant-id-here
CLIENT_ID=your-service-principal-app-id-here
CLIENT_SECRET=your-service-principal-password-here

STORAGE_ACCOUNT_NAME=yourstorageaccount
CONTAINER_NAME=jobscrape-landing

# ================================================================
# Web Scraper Configuration
# ================================================================
MAX_PAGES=5
DELAY_BETWEEN_PAGES=1.0

# ================================================================
# Logging Configuration (Optional)
# ================================================================
LOG_LEVEL=INFO
EOF
```

Verify:
```bash
cat .env.example
```

### 4.3 Create .gitignore (enhanced)
Since GitHub already created a basic `.gitignore`, enhance it:

```bash
cat >> .gitignore << 'EOF'

# ================================================================
# CRITICAL: Never commit credentials or sensitive data
# ================================================================
.env
.env.local
.env.*.local

# ================================================================
# Project Specific
# ================================================================
data/
*.csv
*.xlsx
job_scrape.log
logs/

# Browser data from Playwright
.playwright/
*.db
EOF
```

---

## Step 5: Create Main Python Script File

### 5.1 Create job_scrape.py (stub)
```bash
cat > job_scrape.py << 'EOF'
# Required libraries
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os

# Access helper functions
from helper_functions.addresses import extract_addresses
from helper_functions.application_deadline import extract_expiration_date
from helper_functions.contract_type import extract_type
from helper_functions.expected_tech import extract_expected_technologies
from helper_functions.job_level import extract_level
from helper_functions.job_requirements import extract_requirements
from helper_functions.job_responsibilities import extract_responsibilities
from helper_functions.salary_info import extract_salary_details
from helper_functions.save_results_adls import save_results

# Verify Azure credentials are available
required_env_vars = ["TENANT_ID", "CLIENT_ID", "CLIENT_SECRET", "STORAGE_ACCOUNT_NAME", "CONTAINER_NAME"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {missing_vars}")

print("✅ Azure credentials loaded from environment variables")

def scrape_theprotocol_jobs(max_pages: int = 5, delay: float = 1.0):
    """
    Scrape job listings from TheProtocol.it using Playwright (handles dynamic content).
    Returns a list of dicts with structured job data.
    
    Args:
        max_pages: Maximum number of pages to scrape
        delay: Delay in seconds between page requests
    """
    # Implementation here
    pass

if __name__ == "__main__":
    try:
        jobs = scrape_theprotocol_jobs(max_pages=5, delay=1.0)
        save_results(jobs)
        print("\n✅ Job scraping and upload completed successfully")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        raise
EOF
```

---

## Step 6: Create Notebook Files

### 6.1 Create Databricks Notebooks
```bash
cat > notebooks/01_bronze_load.py << 'EOF'
# Databricks notebook source
"""
Bronze Layer: Raw Data Ingestion
Batch load using CSV from ADLS to Bronze Delta table
"""

# Implementation here

print("✅ Bronze layer loaded successfully")
EOF
```

```bash
cat > notebooks/02_silver_cleaning.py << 'EOF'
# Databricks notebook source
"""
Silver Layer: Data Cleaning & Validation
"""

# Implementation here

print("✅ Silver layer cleaned successfully")
EOF
```

```bash
cat > notebooks/03_gold_aggregations.sql << 'EOF'
-- Databricks notebook source
-- Gold Layer: Business-Ready Aggregations

-- Implementation here

SELECT 'Gold layer created successfully' AS status;
EOF
```

---

## Step 7: Create Documentation Files

### 7.1 Create ARCHITECTURE.md
```bash
cat > docs/ARCHITECTURE.md << 'EOF'
# Architecture Overview

## Data Flow

Local Machine → ADLS → Databricks → Gold Layer

### Components

1. **job_scrape.py** (Local)
   - Scrapes TheProtocol.it daily via CRON
   - Outputs CSV to ADLS landing zone

2. **01_bronze_load.py** (Databricks)
   - Triggered on file arrival
   - Loads raw CSV to Bronze Delta table

3. **02_silver_cleaning.py** (Databricks)
   - Validates and cleans data
   - Loads to Silver Delta table

4. **03_gold_aggregations.sql** (Databricks)
   - Creates business-ready views
   - Aggregations and reporting layer
EOF
```

### 7.2 Create SETUP_GUIDE.md
```bash
cat > docs/SETUP_GUIDE.md << 'EOF'
# Setup Guide

## Local Setup

1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure `.env` from `.env.example`
6. Run scraper: `python job_scrape.py`

## Databricks Setup

1. Create cluster with Runtime 13.3 LTS+
2. Upload notebooks to workspace
3. Create catalog and schemas
4. Set up file arrival trigger
EOF
```

---

## Step 8: Check Git Status

Before committing, see what files have been created/modified:

```bash
git status
```

You should see something like:
```
On branch main
Changes not staged for commit:
  modified:   .gitignore
  modified:   README.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        .env.example
        requirements.txt
        job_scrape.py
        helper_functions/
        notebooks/
        config/
        docs/
        tests/
        logs/
```

---

## Step 9: Add Files to Git Staging

```bash
# Add all changes
git add .

# Or add specific files
git add requirements.txt .env.example job_scrape.py notebooks/ docs/

# Verify what's staged
git status
```

All files should now show as "Changes to be committed" (in green)

---

## Step 10: Create First Commit

```bash
git commit -m "Initial project setup with structure and configuration files"
```

Better commit message format:
```bash
git commit -m "feat: Initialize job scraper ETL project

- Add project structure with helper functions, notebooks, and docs
- Add requirements.txt with dependencies
- Add .env.example for configuration template
- Add Databricks notebooks for Bronze, Silver, and Gold layers
- Add architecture and setup documentation"
```

Verify the commit:
```bash
git log --oneline
```

---

## Step 11: Push to GitHub

```bash
# Push your commits to GitHub
git push origin main
```

If you get an authentication prompt:
- Use Personal Access Token (recommended) or GitHub password
- Or configure SSH keys (see GitHub docs)

Success message:
```
Enumerating objects: 15, done.
Counting objects: 100% (15/15), done.
Writing objects: 100% (15/15), 1.23 KiB | 1.23 MiB/s, done.
Total 15 (delta 5), reused 0 (delta 0)
To https://github.com/yourusername/job-scraper-etl.git
   abc123..def456  main -> main
```

---

## Step 12: Verify on GitHub

1. Go to https://github.com/yourusername/job-scraper-etl
2. Refresh the page
3. You should see your files and folder structure
4. Click on commits to see your commit history

✅ **Success! Your project is now on GitHub!**

---

## Common Commands Reference

```bash
# Check status
git status

# Add all changes
git add .

# Add specific file
git add filename.py

# Commit changes
git commit -m "Your message here"

# Push to GitHub
git push origin main

# Pull latest changes from GitHub
git pull origin main

# View commit history
git log --oneline

# View what changed in last commit
git show

# Undo last commit (keep changes locally)
git reset --soft HEAD~1
```

---

## Next Steps

After your initial push:

1. **Add your actual code files** to replace stubs
2. **Update README.md** with real instructions
3. **Add collaborators** if working with a team
4. **Enable GitHub Pages** for documentation
5. **Set up branch protection** for main branch
6. **Add GitHub Actions** for CI/CD (optional but impressive!)

---

## Troubleshooting

### "fatal: not a git repository"
```bash
# Make sure you're in the repo directory
cd job-scraper-etl
```

### "Permission denied (publickey)"
You need to set up SSH keys. Use HTTPS instead:
```bash
git remote set-url origin https://github.com/yourusername/job-scraper-etl.git
```

### "failed to push some refs"
Your local is out of sync. Pull first:
```bash
git pull origin main
git push origin main
```

### Files not showing on GitHub
Make sure they were added and committed:
```bash
git add .
git commit -m "Add files"
git push origin main
```