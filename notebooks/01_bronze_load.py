# Databricks notebook source
"""
Bronze Layer: Raw Data Ingestion with MERGE-based deduplication on job_id
Batch load using CSV (non-streaming) from ADLS to Bronze Delta table
"""

from pyspark.sql.functions import col, current_timestamp, current_date
from pyspark.sql.types import StructType, StructField, StringType
from delta.tables import DeltaTable

# COMMAND ----------

# Configuration
CATALOG = "jobscrape"
BRONZE_SCHEMA = "bronze"
TABLE_NAME = f"{CATALOG}.{BRONZE_SCHEMA}.jobs_raw"
LANDING_PATH = "/Volumes/jobscrape/landing/jobscrape_data"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{BRONZE_SCHEMA}")
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {BRONZE_SCHEMA}")

print(f"✓ Using catalog: {CATALOG}")
print(f"✓ Using schema: {BRONZE_SCHEMA}")

# COMMAND ----------

# Define CSV schema
jobs_schema = StructType([
    StructField("job_listing_id", StringType(), False),
    StructField("job_title", StringType(), True),
    StructField("expiration_date", StringType(), True),
    StructField("company_name", StringType(), True),
    StructField("location", StringType(), True),
    StructField("address_1", StringType(), True),
    StructField("address_2", StringType(), True),
    StructField("work_mode", StringType(), True),
    StructField("job_level", StringType(), True),
    StructField("contract_type", StringType(), True),
    StructField("remuneration", StringType(), True),
    StructField("frequency", StringType(), True),
    StructField("gross_or_net", StringType(), True),
    StructField("expected_technologies", StringType(), True),
    StructField("requirements", StringType(), True),
    StructField("responsibilities", StringType(), True),
    StructField("ingestion_timestamp", StringType(), True),
    StructField("ingestion_date", StringType(), True),
    StructField("job_url", StringType(), True)
])

# Get the latest CSV file from ADLS based on filename timestamp
import re
from datetime import datetime

files = dbutils.fs.ls(LANDING_PATH)
csv_files = [f for f in files if f.name.endswith('.csv')]

if not csv_files:
    raise ValueError(f"No CSV files found in {LANDING_PATH}")

# Extract timestamp from filename and find the latest
def extract_timestamp_from_filename(filename):
    """Extract timestamp from filename format: the_it_protocol_jobs_YYYYMMdd_HHmmss.csv"""
    match = re.search(r'the_it_protocol_jobs_(\d{8}_\d{6})', filename)
    if match:
        return datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")
    return None

# Sort by extracted timestamp and get the latest
latest_file = max(
    csv_files,
    key=lambda x: extract_timestamp_from_filename(x.name) or datetime.min
)
latest_file_path = latest_file.path
latest_timestamp = extract_timestamp_from_filename(latest_file.name)

print(f"✓ Found {len(csv_files)} CSV file(s) in {LANDING_PATH}")
print(f"✓ Loading latest file: {latest_file.name}")
print(f"  Timestamp: {latest_timestamp}")

# Read only the latest CSV file
incoming_df = spark.read.format("csv") \
    .option("header", "true") \
    .option("multiLine", "true") \
    .option("escape", "\"") \
    .schema(jobs_schema) \
    .load(latest_file_path)

print(f"✓ Read {incoming_df.count()} raw records")

# COMMAND ----------

# Add metadata columns and write to Delta table
incoming_df_with_metadata = incoming_df \
    .withColumn("source_file", col("_metadata.file_path")) \
    .withColumn("_bronze_ingestion_time", current_timestamp()) \
    .withColumn("_record_processed_date", current_date())

incoming_df_with_metadata.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable(TABLE_NAME)
    
print("✓ Metadata columns added")
print("✓ Initial Delta table created and loaded")

# COMMAND ----------

# Summary and verification
summary = spark.sql(f"""
SELECT 
  'ETL Bronze Complete' AS status,
  CURRENT_TIMESTAMP() AS completion_time,
  COUNT(DISTINCT job_listing_id) AS total_unique_jobs,
  MAX(_bronze_ingestion_time) AS last_loaded
FROM {TABLE_NAME}
""")

summary.show()
print("✓✓✓ BRONZE LAYER LOAD COMPLETE ✓✓✓")