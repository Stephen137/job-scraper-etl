# Databricks notebook source
"""
Silver Layer: Data Cleaning, Transformation & Validation
- Validates required fields
- Applies business logic transformations
- Filters expired job listings
- Logs dropped records with reasons
- Performs reconciliation with Bronze layer
"""

from pyspark.sql.functions import col, when, current_timestamp, current_date, lit, concat, to_date, datediff, trim, regexp_replace, regexp_extract
from pyspark.sql.types import StringType, StructType, StructField, IntegerType as SparkIntegerType
from delta.tables import DeltaTable
import re

# COMMAND ----------

# Configuration
CATALOG = "jobscrape"
BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"
BRONZE_TABLE = f"{CATALOG}.{BRONZE_SCHEMA}.jobs_raw"
SILVER_TABLE = f"{CATALOG}.{SILVER_SCHEMA}.jobs_cleaned"
DROPPED_RECORDS_TABLE = f"{CATALOG}.{SILVER_SCHEMA}.dropped_records_log"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SILVER_SCHEMA}")
spark.sql(f"USE CATALOG {CATALOG}")

print("=" * 80)
print("SILVER LAYER: DATA CLEANING, TRANSFORMATION & VALIDATION")
print("=" * 80)
print(f"\n✓ Reading from: {BRONZE_TABLE}")
print(f"✓ Writing to: {SILVER_TABLE}")

# COMMAND ----------

# Read from Bronze layer
df = spark.sql(f"SELECT * FROM {BRONZE_TABLE}")
bronze_count = df.count()

print(f"\n📥 Read {bronze_count} records from Bronze layer")

# COMMAND ----------

# ===== DATA VALIDATION: Flag records with missing required fields =====

required_fields = {
    "job_listing_id": "Job Listing ID is required",
    "job_title": "Job Title is required",
    "company_name": "Company Name is required",
    "job_level": "Job Level is required",
    "contract_type": "Contract Type is required"
}

# Flag records that fail validation
df = df.withColumn(
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
valid_records = df.filter(col("validation_errors") == "")
dropped_records = df.filter(col("validation_errors") != "")

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

# Continue with valid records for transformations
df = valid_records.drop("validation_errors")

# ===== TRANSFORMATION 1: Date Parsing (expiration_date) =====

month_mapping = {
    # English
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
    # Polish
    "stycznia": "01", "lutego": "02", "marca": "03", "kwietnia": "04",
    "maja": "05", "czerwca": "06", "lipca": "07", "sierpnia": "08",
    "września": "09", "października": "10", "listopada": "11", "grudnia": "12"
}

def convert_date(date_str):
    """Convert date string 'day month_name year' to 'YYYY-MM-DD'"""
    if not date_str:
        return None
    
    try:
        parts = date_str.strip().split()
        if len(parts) != 3:
            return None
        
        day, month_name, year = parts
        month_num = month_mapping.get(month_name.lower())
        
        if not month_num:
            return None
        
        formatted_date = f"{year}-{month_num}-{day.zfill(2)}"
        return formatted_date
    except:
        return None

convert_date_udf = spark.udf.register("convert_date", convert_date, StringType())

df = df.withColumn("expiration_date", 
                   to_date(convert_date_udf(col("expiration_date")), "yyyy-MM-dd"))

print("✓ Transformed: expiration_date")

df = df.withColumn("job_posting_date", 
                   to_date(convert_date_udf(col("job_posting_date")), "yyyy-MM-dd"))

print("✓ Transformed: job_posting_date")

# COMMAND ----------

# ===== TRANSFORMATION 2a: Days Until Expiry =====

df = df.withColumn("days_left", 
                   datediff(col("expiration_date"), current_date()))

print("✓ Added: days_left column")

# COMMAND ----------

# ===== TRANSFORMATION 2b: Days Since Posted =====

df = df.withColumn("days_since_posted", 
                  datediff(current_date(), col("job_posting_date")))

print("✓ Added: days_since_posted column")

# COMMAND ----------

# ===== TRANSFORMATION 3: Location Cleaning =====

df = df.withColumn("location", 
                   when(col("location").rlike("Oferta w wielu lokalizacjach|Multiple locations offer"), 
                        "Multiple locations")
                   .otherwise(col("location")))

print("✓ Cleaned: location (multi-location patterns)")

# COMMAND ----------

# ===== TRANSFORMATION 4: Work Mode Translation =====

work_mode_mapping = {
    "hybrydowa": "hybrid",
    "zdalna": "remote",
    "stacjonarna": "full office"
}

def translate_work_modes(work_modes_str):
    """Translate Polish work mode names to English, handling multiple modes"""
    if not work_modes_str:
        return None
    
    modes = [mode.strip().lower() for mode in work_modes_str.split(",")]
    translated_modes = []
    for mode in modes:
        translated_mode = work_mode_mapping.get(mode, mode)
        translated_modes.append(translated_mode)
    
    return ", ".join(translated_modes)

translate_work_modes_udf = spark.udf.register("translate_work_modes", translate_work_modes, StringType())

df = df.withColumn("work_mode", translate_work_modes_udf(col("work_mode")))

print("✓ Translated: work_mode (Polish to English)")

# COMMAND ----------

# ===== TRANSFORMATION 5: Job Level Cleaning =====

df = df.withColumn("job_level", 
                   trim(regexp_replace(col("job_level"), "•", ",")))

print("✓ Cleaned: job_level (bullet points to commas)")

# COMMAND ----------

# ===== TRANSFORMATION 6: Contract Type Translation =====

contract_type_mapping = {
    "kontrakt B2B (pełny etat)": "B2B contract (full-time)",
    "umowa o pracę (pełny etat)": "contract of employment (full-time)",
    "kontrakt B2B (część etatu, pełny etat)": "B2B contract (part-time, full-time)",
    "kontrakt B2B": "B2B contract"
}

def translate_contract_type(contract_type_str):
    """Translate Polish contract type to English"""
    if not contract_type_str:
        return None
    
    return contract_type_mapping.get(contract_type_str, contract_type_str)

translate_contract_type_udf = spark.udf.register("translate_contract_type", translate_contract_type, StringType())

df = df.withColumn("contract_type", translate_contract_type_udf(col("contract_type")))

print("✓ Translated: contract_type (Polish to English)")

# COMMAND ----------

# ===== TRANSFORMATION 7a: Salary Parsing =====

def extract_salary_range(remuneration_str):
    """Extract min and max salary from remuneration string"""
    if not remuneration_str or "null" in remuneration_str.lower():
        return (None, None)
    
    try:
        # Replace non-breaking spaces and other whitespace with regular spaces
        remuneration_str = remuneration_str.replace('\u00A0', ' ').replace('\u2009', ' ').replace('\u202F', ' ')
        
        # Extract numbers
        match = re.search(r'([\d\s,]+)\s*-\s*([\d\s,]+)', remuneration_str)
        
        if match:
            min_str = match.group(1).strip().replace(" ", "")
            max_str = match.group(2).strip().replace(" ", "")
            
            # Convert comma to dot for float parsing, then to int
            min_salary = int(float(min_str.replace(",", ".")))
            max_salary = int(float(max_str.replace(",", ".")))
            
            return (min_salary, max_salary)
    except:
        pass
    
    return (None, None)

# Register UDF with struct return type
salary_schema = StructType([
    StructField("min_salary", SparkIntegerType(), True),
    StructField("max_salary", SparkIntegerType(), True)
])

extract_salary_range_udf = spark.udf.register("extract_salary_range", extract_salary_range, salary_schema)

# Apply and extract both columns
df = df.withColumn("salary_range", extract_salary_range_udf(col("remuneration")))
df = df.withColumn("min_salary", col("salary_range.min_salary"))
df = df.withColumn("max_salary", col("salary_range.max_salary"))
df = df.drop("salary_range")

print("✓ Parsed: salary (min_salary, max_salary)")

# COMMAND ----------

# ===== TRANSFORMATION 7b: Split Salary by Frequency =====

df = df.withColumn("min_salary_mth",
                   when(col("frequency") == "monthly", col("min_salary"))
                   .otherwise(None))

df = df.withColumn("max_salary_mth",
                   when(col("frequency") == "monthly", col("max_salary"))
                   .otherwise(None))

df = df.withColumn("min_salary_hr",
                   when(col("frequency") == "hourly", col("min_salary"))
                   .otherwise(None))

df = df.withColumn("max_salary_hr",
                   when(col("frequency") == "hourly", col("max_salary"))
                   .otherwise(None))

print("✓ Created frequency-based salary columns (min/max_salary_mth and min/max_salary_hr)")

# COMMAND ----------

# ===== TRANSFORMATION 8: Frequency Translation =====

def translate_frequency(frequency_str):
    """Translate frequency values to standardized format"""
    if not frequency_str:
        return None
    
    freq_lower = frequency_str.lower().strip()
    
    if re.search(r'mth|mies', freq_lower):
        return "monthly"
    
    if re.search(r'hr|godz', freq_lower):
        return "hourly"
    
    return frequency_str

translate_frequency_udf = spark.udf.register("translate_frequency", translate_frequency, StringType())

df = df.withColumn("frequency", translate_frequency_udf(col("frequency")))

print("✓ Translated: frequency (monthly/hourly)")

# COMMAND ----------

# ===== FILTER EXPIRED LISTINGS =====

df_before_filter = df.count()
df = df.filter(col("days_left") >= 0)
df_after_filter = df.count()

print(f"✓ Filtered expired listings: {df_before_filter} → {df_after_filter} rows")

# COMMAND ----------

# ===== REORDER COLUMNS =====

column_order = [
    "job_listing_id", "days_since_posted", "company_name", "job_title", "days_left", "expected_technologies", 
    "min_salary", "max_salary", "min_salary_mth", "max_salary_mth", "min_salary_hr", "max_salary_hr",
    "frequency", "location", "address_1", "address_2", 
    "contract_type", "job_level", "work_mode", "responsibilities", "requirements", 
    "ingestion_date", "ingestion_timestamp", "job_posting_date", "expiration_date", "remuneration", "job_url",
    "source_file"
]

# Ensure 'source_file' exists in DataFrame
if "source_file" not in df.columns:
    df = df.withColumn("source_file", lit(None).cast(StringType()))

df = df.select(column_order)

print("✓ Reordered columns")

# COMMAND ----------

# ===== WRITE TO SILVER LAYER =====

print(f"\n📝 Writing to silver layer: {SILVER_TABLE}")

df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable(SILVER_TABLE)

silver_final_count = df.count()
print(f"✓ Successfully written {silver_final_count} rows to silver layer")

# COMMAND ----------

# ===== DATA RECONCILIATION =====

print("\n" + "=" * 80)
print("DATA RECONCILIATION CHECK")
print("=" * 80)

expected_silver = bronze_count - dropped_count

print(f"\n📊 Record Counts:")
print(f"   Bronze Layer (input):     {bronze_count}")
print(f"   Dropped (validation):     {dropped_count}")
print(f"   Filtered (expired):       {df_before_filter - df_after_filter}")
print(f"   Silver Layer (output):    {silver_final_count}")
print(f"   Expected Silver:          {expected_silver}")

if silver_final_count == expected_silver:
    print(f"\n✅ Reconciliation PASSED - Record counts match")
else:
    print(f"\n⚠️  Reconciliation WARNING - Record count mismatch")
    print(f"   Difference: {abs(silver_final_count - expected_silver)} rows")

# COMMAND ----------

# ===== FINAL SUMMARY =====

print("\n" + "=" * 80)
print("SILVER LAYER SUMMARY")
print("=" * 80)
print(f"\n✅ Processing complete")
print(f"   • Records processed: {bronze_count}")
print(f"   • Records dropped (validation): {dropped_count}")
print(f"   • Records filtered (expired): {df_before_filter - df_after_filter}")
print(f"   • Records loaded to Silver: {silver_final_count}")

if dropped_count > 0:
    print(f"\n   ⚠️  {dropped_count} record(s) dropped due to data quality issues")
    print(f"   📋 Review {DROPPED_RECORDS_TABLE} for details")

print(f"\n{'=' * 80}")

# COMMAND ----------

# ===== VERIFICATION =====

print("\n🔍 Sample data from Silver layer:")
silver_verification = spark.sql(f"SELECT * FROM {SILVER_TABLE}")
silver_verification.select("company_name", "job_title", "min_salary_mth", "max_salary_mth", 
                           "days_left", "work_mode", "contract_type").show(10, truncate=False)