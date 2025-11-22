# Required libraries
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os
import re

# Access helper functions
from helper_functions.addresses import extract_addresses
from helper_functions.application_deadline import extract_expiration_date
from helper_functions.job_posting_date import extract_job_posting_date
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

# ---------------------------------------------------------------------
# Helper Function to Extract Job Listing ID
# ---------------------------------------------------------------------
def extract_job_listing_id(job_url: str) -> str:
    """
    Extract the Job Listing ID (UUID) from the job URL.
    
    Args:
        job_url: The full job URL
        
    Returns:
        The job listing ID (UUID) or None if not found
    """
    if not job_url:
        return None
    
    # Match UUID pattern (8-4-4-4-12 hex digits)
    match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', job_url)
    if match:
        return match.group(1)
    
    return None

# ---------------------------------------------------------------------
# Main HTML Parse Function
# ---------------------------------------------------------------------
def scrape_theprotocol_jobs(max_pages: int = 5, delay: float = 1.0):
    """
    Scrape job listings from TheProtocol.it using Playwright (handles dynamic content).
    Returns a list of dicts with structured job data.
    
    Args:
        max_pages: Maximum number of pages to scrape
        delay: Delay in seconds between page requests
    """

    jobs_data = []

    # Capture ingestion timestamp once at the start of scraping
    ingestion_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ingestion_date = datetime.now().strftime("%Y-%m-%d")

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()

        for page_num in range(1, max_pages + 1):
            url = f"https://theprotocol.it/filtry/data-analytics-bi,big-data-science,business-analytics;sp/krakow;wp?sort=date&pageNumber={page_num}"
            print(f"🌐 Loading page {page_num}: {url}")

            page.goto(url, timeout=60000)
            try:
                page.wait_for_selector('[data-test="text-jobTitle"]', timeout=15000)
            except:
                print(f"⚠️  No job listings found on page {page_num}. Stopping.")
                break

            soup = BeautifulSoup(page.content(), "html.parser")
            job_links = soup.find_all("a", {"data-test": "list-item-offer"})
            
            if not job_links:
                print(f"✅ No job listings found on page {page_num}.")
                break

            print(f"📋 Found {len(job_links)} job listings on page {page_num}")

            # Process each job listing
            for idx, link_tag in enumerate(job_links, 1):
                try:
                    job_url = link_tag.get('href')
                    if job_url and not job_url.startswith('http'):
                        job_url = f"https://theprotocol.it{job_url}"
                    
                    print(f"\n  [{idx}/{len(job_links)}] Processing: {job_url}")
                    
                    # Extract Job Listing ID from URL
                    job_listing_id = extract_job_listing_id(job_url)
                    print(f"  Job Listing ID: {job_listing_id}")
                    
                    # Extract basic info from listings
                    listing = link_tag.find("div", {"class": "p17ye701"})
                    if not listing:
                        continue
                    
                    job_title_tag = listing.find("h2", {"data-test": "text-jobTitle"})
                    company_tag = listing.find("div", {"data-test": "text-employerName"})
                    location_tag = listing.find("div", {"data-test": "text-workplaces"})
                    work_mode_tag = listing.find("div", {"data-test": "text-workModes"})

                    # Initialize variables with default values
                    expiration_date = None
                    job_posting_date = None
                    job_level = None
                    contract_type = None
                    salary_details = {'remuneration': None, 'frequency': None, 'gross_or_net': None}
                    expected_technologies = []
                    requirements = [] 
                    responsibilities = []  
                    addresses = {'address_1': None, 'address_2': None}

                    # Navigate to job detail page ONCE and extract ALL data
                    if job_url:
                        try:
                            page.goto(job_url, timeout=30000)
                            
                            # Extract all data in one go - PASS THE PAGE OBJECT to each function
                            expiration_date = extract_expiration_date(page)
                            job_posting_date = extract_job_posting_date(page)
                            job_level = extract_level(page)
                            contract_type = extract_type(page)
                            salary_details = extract_salary_details(page)
                            expected_technologies = extract_expected_technologies(page)
                            addresses = extract_addresses(page)
                            requirements = extract_requirements(page)
                            responsibilities = extract_responsibilities(page)
                            
                            # Go back to listing page
                            page.go_back(timeout=10000)
                            page.wait_for_selector('[data-test="text-jobTitle"]', timeout=10000)
                            time.sleep(0.5)
                            
                        except Exception as e:
                            print(f"    ⚠️  Error extracting data from detail page: {e}")
                            # Try to return to listing page
                            try:
                                page.goto(url, timeout=30000)
                                page.wait_for_selector('[data-test="text-jobTitle"]', timeout=10000)
                            except:
                                print(f"    ❌ Failed to return to listing page")

                    jobs_data.append({
                        "job_listing_id": job_listing_id,
                        "job_title": job_title_tag.get_text(strip=True) if job_title_tag else None,
                        "expiration_date": expiration_date,
                        "job_posting_date": job_posting_date,
                        "company_name": company_tag.get_text(strip=True) if company_tag else None,
                        "location": location_tag.get_text(strip=True) if location_tag else None,
                        "address_1": addresses['address_1'],
                        "address_2": addresses['address_2'], 
                        "work_mode": work_mode_tag.get_text(strip=True) if work_mode_tag else None,
                        "job_level": job_level,
                        "contract_type": contract_type,
                        "remuneration": salary_details['remuneration'],
                        "frequency": salary_details['frequency'],
                        "gross_or_net": salary_details.get('gross_or_net'),
                        "expected_technologies": expected_technologies,
                        "requirements": requirements,  
                        "responsibilities": responsibilities,                         
                        "ingestion_timestamp": ingestion_timestamp,
                        "ingestion_date": ingestion_date,
                        "job_url": job_url
                    })

                except Exception as e:
                    print(f"  ❌ Error processing job listing: {e}")
                    continue

            print(f"\n✅ Page {page_num}: collected {len(job_links)} jobs. Total so far: {len(jobs_data)}")
            time.sleep(delay)

        browser.close()

    print(f"\n🎉 Scraping complete. Total jobs collected: {len(jobs_data)}")
    return jobs_data

# ---------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------
if __name__ == "__main__":
    try:
        # Run the scraper
        jobs = scrape_theprotocol_jobs(max_pages=5, delay=1.0)
        
        # Save the results
        save_results(jobs)
        
        print("\n✅ Job scraping and upload completed successfully")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        raise