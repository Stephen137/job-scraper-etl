# Databricks notebook source
"""
Silver Layer: Data Cleaning & Validation with integrated Quality Checks
- Validates required fields
- Logs dropped records with reasons
- Performs reconciliation with Bronze layer
"""

from pyspark.sql.functions import col, when, current_timestamp, current_date, lit, concat
from delta.tables import DeltaTable

# COMMAND ----------

# Configuration
CATALOG = "jobscrape"
BRONZE_TABLE = f"{CATALOG}.bronze.jobs_raw"
SILVER_TABLE = f"{CATALOG}.silver.jobs_clean"
DROPPED_RECORDS_TABLE = f"{CATALOG}.silver.dropped_records_log"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.silver")
spark.sql(f"USE CATALOG {CATALOG}")

print("=" * 80)
print("SILVER LAYER: DATA CLEANING & VALIDATION")
print("=" * 80)

# COMMAND ----------

# Read from Bronze layer
bronze_df = spark.read.table(BRONZE_TABLE)
bronze_count = bronze_df.count()

print(f"\n📥 Read {bronze_count} records from Bronze layer")

# COMMAND ----------

# Define data quality rules
# Records must have these fields to pass to Silver
required_fields = {
    "job_listing_id": "Job Listing ID is required",
    "job_title": "Job Title is required",
    "company_name": "Company Name is required",
    "job_level": "Job Level is required",
    "contract_type": "Contract Type is required"
}

# Flag records that fail validation
validated_df = bronze_df.withColumn(
    "validation_errors",
    concat(
        when(col("job_listing_id").isNull(), "Missing job_listing_id, ").otherwise(""),
        when(col("job_title").isNull(), "Missing job_title, ").otherwise(""),
        when(col("company_name").isNull(), "Missing company_name, ").otherwise(""),
        when(col("job_level").isNull(), "Missing job_level, ").otherwise(""),
        when(col("contract_type").isNull(), "Missing contract_type, ").otherwise("")
    )
)

# Separate valid and invalid records
valid_records = validated_df.filter(col("validation_errors") == "")
dropped_records = validated_df.filter(col("validation_errors") != "")

valid_count = valid_records.count()
dropped_count = dropped_records.count()

print(f"\n✅ Valid records: {valid_count}")
print(f"❌ Dropped records: {dropped_count}")

# COMMAND ----------

# Log dropped records with reasons
if dropped_count > 0:
    dropped_for_logging = dropped_records.select(
        col("job_listing_id"),
        col("job_title"),
        col("company_name"),
        col("validation_errors").alias("reason_dropped"),
        col("ingestion_timestamp"),
        lit(current_timestamp()).alias("validation_timestamp"),
        lit(current_date()).alias("validation_date")
    )
    
    dropped_for_logging.write.format("delta") \
        .mode("append") \
        .saveAsTable(DROPPED_RECORDS_TABLE)
    
    print(f"\n📋 Dropped Records Details:")
    dropped_for_logging.show(truncate=False)
    
    print(f"\n💾 Dropped records logged to: {DROPPED_RECORDS_TABLE}")

# COMMAND ----------

# Clean valid records and prepare for Silver layer
silver_df = valid_records.select(
    "job_listing_id",
    "job_title",
    "expiration_date",
    "company_name",
    "location",
    "address_1",
    "address_2",
    "work_mode",
    "job_level",
    "contract_type",
    "remuneration",
    "frequency",
    "gross_or_net",
    "expected_technologies",
    "requirements",
    "responsibilities",
    "ingestion_timestamp",
    "ingestion_date",
    "job_url",
    "source_file",
    col("_bronze_ingestion_time"),
    col("_record_processed_date"),
    lit(current_timestamp()).alias("_silver_transformation_time")
)

# Write to Silver layer
silver_df.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable(SILVER_TABLE)

print(f"\n✍️  Wrote {valid_count} cleaned records to Silver layer")

# COMMAND ----------

# Data Reconciliation: Bronze vs Silver
print("\n" + "=" * 80)
print("DATA RECONCILIATION CHECK")
print("=" * 80)

silver_loaded_count = spark.read.table(SILVER_TABLE).count()

print(f"\n📊 Record Counts:")
print(f"   Bronze Layer:    {bronze_count}")
print(f"   Silver Layer:    {silver_loaded_count}")
print(f"   Dropped:         {dropped_count}")
print(f"   Expected Silver: {bronze_count - dropped_count}")

if silver_loaded_count == (bronze_count - dropped_count):
    print(f"\n✅ Reconciliation PASSED - Record counts match")
else:
    print(f"\n⚠️  Reconciliation WARNING - Unexpected record count mismatch")

# COMMAND ----------

# Final Summary
print("\n" + "=" * 80)
print("SILVER LAYER SUMMARY")
print("=" * 80)
print(f"\n✅ Processing complete")
print(f"   • Records processed: {bronze_count}")
print(f"   • Records loaded to Silver: {valid_count}")
print(f"   • Records dropped: {dropped_count}")

if dropped_count > 0:
    print(f"\n   ⚠️  {dropped_count} record(s) dropped due to data quality issues")
    print(f"   📋 Review {DROPPED_RECORDS_TABLE} for details")
    
print(f"\n{'=' * 80}")
