#!/bin/bash
# ================================================================
# Job Scraper Runner Script
# ================================================================
# This script is designed to be run by CRON scheduler
# Usage: 0 2 * * * /path/to/run_job.sh
#
# IMPORTANT: Environment variables must be set in .env file
# Do NOT commit credentials to Git
# ================================================================

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Source the .env file for credentials and configuration
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a  # Export all variables
    source "$SCRIPT_DIR/.env"
    set +a
else
    echo "❌ Error: .env file not found in $SCRIPT_DIR"
    echo "❌ Please create .env file from .env.example: cp .env.example .env"
    exit 1
fi

# Verify required environment variables
required_vars=("TENANT_ID" "CLIENT_ID" "CLIENT_SECRET" "STORAGE_ACCOUNT_NAME" "CONTAINER_NAME")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "❌ Error: Missing required environment variables: ${missing_vars[*]}"
    echo "❌ Please configure these in .env file"
    exit 1
fi

# Change to project directory
cd "$SCRIPT_DIR" || exit 1

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  Warning: Virtual environment not found"
    echo "⚠️  Attempting to run with system Python"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the job scraper
echo "🌐 Starting job scraper at $(date '+%Y-%m-%d %H:%M:%S')"
python3 job_scrape.py >> logs/job_scrape.log 2>> logs/job_scrape_error.log

# Capture exit code
exit_code=$?

# Log completion
if [ $exit_code -eq 0 ]; then
    echo "✅ Job scraper completed successfully at $(date '+%Y-%m-%d %H:%M:%S')" >> logs/job_scrape.log
else
    echo "❌ Job scraper failed with exit code $exit_code at $(date '+%Y-%m-%d %H:%M:%S')" >> logs/job_scrape_error.log
fi

exit $exit_code