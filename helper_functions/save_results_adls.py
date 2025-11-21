from datetime import datetime
import csv
import json
import os
from io import StringIO
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import ClientSecretCredential

# Azure credentials - READ FROM ENVIRONMENT VARIABLES
ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "dbricksetlprojectstorage")
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "jobscrape")
DIRECTORY_NAME = "landing/jobscrape_data"

# Get credentials from environment variables (in priority order)
CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Validate that we have at least one auth method
if not (CONNECTION_STRING or ACCOUNT_KEY or (TENANT_ID and CLIENT_ID and CLIENT_SECRET)):
    raise ValueError(
        "No Azure credentials found. Please set one of:\n"
        "  - AZURE_STORAGE_CONNECTION_STRING\n"
        "  - AZURE_STORAGE_ACCOUNT_KEY\n"
        "  - TENANT_ID, CLIENT_ID, CLIENT_SECRET"
    )

# ---------------------------------------------------------------------
# SAVE RESULTS TO ADLS
# ---------------------------------------------------------------------

def get_adls_client():
    """
    Create and return an ADLS client.
    Supports multiple authentication methods (in priority order):
    1. Connection string
    2. Account key
    3. Service principal (client credentials)
    """
    if CONNECTION_STRING:
        print("🔐 Using connection string authentication")
        return DataLakeServiceClient.from_connection_string(CONNECTION_STRING)
    
    elif ACCOUNT_KEY:
        print("🔐 Using account key authentication")
        return DataLakeServiceClient(
            account_url=f"https://{ACCOUNT_NAME}.dfs.core.windows.net",
            credential=ACCOUNT_KEY
        )
    
    else:
        print("🔐 Using service principal authentication")
        credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
        return DataLakeServiceClient(
            account_url=f"https://{ACCOUNT_NAME}.dfs.core.windows.net",
            credential=credential
        )

def save_results(jobs_data):
    """
    Save scraped jobs to CSV and JSON in ADLS with timestamped filenames.
    Technologies are comma-separated in CSV, lists in JSON.
    
    Args:
        jobs_data: List of dictionaries containing job information
    """
    if not jobs_data:
        print("⚠️  No data to save.")
        return

    try:
        client = get_adls_client()
        file_system_client = client.get_file_system_client(file_system=CONTAINER_NAME)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"the_it_protocol_jobs_{timestamp}.csv"
        #json_filename = f"the_it_protocol_jobs_{timestamp}.json"
        
        csv_path = f"{DIRECTORY_NAME}/{csv_filename}"
        #json_path = f"{DIRECTORY_NAME}/{json_filename}"
        
        # Prepare CSV data
        csv_buffer = StringIO()
        fieldnames = list(jobs_data[0].keys())
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()
        
        for job in jobs_data:
            job_csv = job.copy()
            # Convert lists to strings for CSV
            if "expected_technologies" in job_csv and isinstance(job_csv["expected_technologies"], list):
                job_csv["expected_technologies"] = ", ".join(job_csv["expected_technologies"])
            if "requirements" in job_csv and isinstance(job_csv["requirements"], list):
                job_csv["requirements"] = " | ".join(job_csv["requirements"])
            if "responsibilities" in job_csv and isinstance(job_csv["responsibilities"], list):
                job_csv["responsibilities"] = " | ".join(job_csv["responsibilities"])
            writer.writerow(job_csv)
        
        csv_data = csv_buffer.getvalue()
        
        # Upload CSV to ADLS
        file_client = file_system_client.get_file_client(csv_path)
        file_client.upload_data(csv_data, overwrite=True)
        print(f"💾 Saved CSV to ADLS: {csv_path}")
        
        # Prepare JSON data
        #json_data = json.dumps(jobs_data, ensure_ascii=False, indent=2)
        
        # Upload JSON to ADLS
        #file_client = file_system_client.get_file_client(json_path)
        #file_client.upload_data(json_data, overwrite=True)
        #print(f"💾 Saved JSON to ADLS: {json_path}")
        
        print(f"✅ Successfully saved {len(jobs_data)} jobs to ADLS")
        
    except Exception as e:
        print(f"❌ Error saving to ADLS: {e}")
        raise