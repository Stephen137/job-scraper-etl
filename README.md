# Job Scraper ETL Pipeline

[![Tests](https://github.com/Stephen137/job-scraper-etl/actions/workflows/tests.yml/badge.svg)](https://github.com/Stephen137/job-scraper-etl/actions/workflows/tests.yml)

**Production-grade ETL pipeline** that automates job market intelligence collection and analysis. Built a full-stack data engineering solution combining local web scraping with cloud-based data warehouse transformation.

## 🚀 Quick Overview

```
Local Machine → ADLS Landing Zone → Databricks → Analytics Layer
(Web Scraper)   (Cloud Storage)    (Transform)   (Gold Views)
```

## 📋 Key Features

- **Web Scraper**: Playwright-based scraper handling dynamic content, pagination, and error recovery
- **Data Validation**: Comprehensive quality checks with dropped records logging
- **Medallion Architecture**: Bronze (raw) → Silver (clean) → Gold (analytics) layers
- **Infrastructure-as-Code**: Reproducible setup with environment-based configuration
- **Automated Testing**: 35+ pytest tests with GitHub Actions CI/CD
- **Production Ready**: Comprehensive error handling, logging, and reconciliation checks

## 🛠 Tech Stack

- **Local**: Python, Playwright, BeautifulSoup, Pandas
- **Cloud**: Azure ADLS, Databricks, Delta Lake, PySpark, SQL
- **DevOps**: GitHub Actions, Bash, Git
- **Testing**: Pytest, pytest-cov, Mock

## 📁 Project Structure

```
job-scraper-etl/
├── job_scrape.py                 # Main web scraper
├── helper_functions/             # 9 modular extraction functions
├── notebooks/
│   ├── 01_bronze_load.py         # Bronze layer (raw data ingestion)
│   ├── 02_silver_cleaning.py     # Silver layer (validation & cleaning)
│   └── 03_gold_aggregations.sql  # Gold layer (analytics views)|   
|   
├── tests/
│   └── test_helper_functions.py  # 35+ pytest tests
├── docs/
│   ├── ARCHITECTURE.md           # Detailed architecture
│   ├── SETUP_GUIDE.md           # Step-by-step setup
│   └── TROUBLESHOOTING.md       # Common issues & fixes
├── .github/workflows/
│   └── tests.yml                 # GitHub Actions CI/CD
├── requirements.txt              # Python dependencies
├── .env.example                  # Configuration template
├── run_job.sh                    # CRON-schedulable runner
└── .gitignore                    # Git ignore rules
```

## 🚀 Quick Start

### Local Setup (Web Scraper)

```bash
# Clone repository
git clone https://github.com/Stephen137/job-scraper-etl.git
cd job-scraper-etl

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your Azure credentials

# Run scraper
python job_scrape.py
```

### Databricks Setup (Cloud Transformation)

1. **Create Cluster**: Runtime 13.3 LTS or later
2. **Create Catalog & Schemas**:
   ```sql
   CREATE CATALOG IF NOT EXISTS jobscrape;
   CREATE SCHEMA IF NOT EXISTS jobscrape.bronze;
   CREATE SCHEMA IF NOT EXISTS jobscrape.silver;
   CREATE SCHEMA IF NOT EXISTS jobscrape.gold;
   ```
3. **Upload Notebooks**: `notebooks/01_*.py`, `02_*.py`, `03_*.sql`, `04_*.sql`
4. **Set Up File Arrival Trigger**: 
   - Path: `/Volumes/jobscrape/landing/jobscrape_data/`
   - Pattern: `*.csv`
   - Tasks: Bronze → Silver → Gold (sequential)

## 🧪 Testing

Run the test suite locally:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
pytest tests/ --cov=helper_functions --cov-report=html

# Run specific test file
pytest tests/test_helper_functions.py -v
```

**Test Coverage:**
- 10 tests for `extract_addresses`
- 11 tests for `extract_type`
- 11 tests for `extract_level`
- 3 integration tests
- Total: 35 tests ✅

Tests run automatically on every push via GitHub Actions!

## 🔄 Data Flow

### 1. Local Scraper (CRON Scheduled)
- Runs daily via `run_job.sh`
- Scrapes TheProtocol.it job listings
- Generates timestamped CSV: `the_it_protocol_jobs_YYYYMMdd_HHmmss.csv`
- Uploads to ADLS landing zone

### 2. Bronze Layer (Triggered on File Arrival)
- Loads raw CSV to Bronze Delta table
- Adds metadata: ingestion timestamp, source file, processing date
- Latest file selection by timestamp
- No transformations (preserve raw data)

### 3. Silver Layer (Data Validation)
- Validates required fields
- Enforces data quality rules
- Logs dropped records with failure reasons
- Bronze-to-Silver reconciliation
- Returns cleaned, validated data

### 4. Gold Layer (Analytics)
- Creates business-ready views
- Aggregations by job level, company, technology
- Salary analysis
- No data modification, only curated views

## 📊 Data Quality

The pipeline includes built-in validation:
- **Required fields**: job_listing_id, job_title, company_name, job_level, contract_type
- **Dropped records logging**: Tracks all failures with reasons
- **Reconciliation checks**: Bronze → Silver record count verification
- **Data quality notebook**: SQL queries for analysis and monitoring

## 🔐 Security & Configuration

- **Credentials**: Managed via environment variables (`.env` not committed)
- **Template**: `.env.example` shows required variables
- **RBAC**: Azure ADLS with role-based access control
- **Secrets**: Use Databricks Secrets for sensitive data in notebooks

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Detailed technical architecture
- **[SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Step-by-step setup instructions
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues & solutions

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes and test: `pytest tests/ -v`
3. Commit with clear messages: `git commit -m "feat: description"`
4. Push and create a Pull Request

## 📈 Monitoring & Logs

### Local Logs
- `logs/job_scrape.log` - Web scraper execution logs
- Check for `⚠️ Error extracting data from detail page` warnings

### Databricks Logs
- Workflow run history in Databricks UI
- Query `jobscrape.silver.dropped_records_log` for data quality issues
- Review timestamps: `_bronze_ingestion_time`, `_silver_transformation_time`

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 👤 Author

Stephen Barrie
- [GitHub](https://github.com/Stephen137)
- [LinkedIn](https://linkedin.com/in/sjbarrie)

## 🎯 Next Steps

- [x] Web scraper with error handling
- [x] Databricks medallion architecture
- [x] Data validation and quality checks
- [x] Automated testing (35+ tests)
- [x] GitHub Actions CI/CD
- [ ] Code coverage dashboard (Codecov)
- [ ] Performance benchmarking
- [ ] Additional job sites integration

## 📞 Support

For issues, questions, or suggestions:
1. Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Review existing [GitHub Issues](https://github.com/Stephen137/job-scraper-etl/issues)
3. Create a new issue with details

---

**Happy scraping! 🚀**
