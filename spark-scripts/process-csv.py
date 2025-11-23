from pyspark.sql import SparkSession
# from dotenv import load_dotenv
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, lower, regexp_replace, when
from pyspark.sql.types import DoubleType, IntegerType

# load_dotenv()

MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'http://minio-service:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')


# -----------------------------------------
# SPARK SESSION WITH MINIO CONFIG
# -----------------------------------------
spark = (
    SparkSession.builder
    .appName("Fintech-Cleaning")
    .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT)
    .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
    .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
    .getOrCreate()
)

# -----------------------------------------
# READ RAW PARQUET FROM MINIO
# -----------------------------------------
df = spark.read.csv(path="/data/input/financial_risk_assessment.csv", inferSchema=True, header=True)

df.show(10)
# -----------------------------------------
# BASIC CLEANING
# -----------------------------------------
# Trim whitespace
df = df.select([trim(col(c)).alias(c) for c in df.columns])

# Normalize categorical fields (lowercase + underscores)
categorical_cols = [
    "Gender", "Education Level", "Marital Status", "Loan Purpose",
    "Employment Status", "Payment History", "City", "State", "Country",
    "Risk Rating"
]

for c in categorical_cols:
    if c in df.columns:
        df = df.withColumn(
            c,
            lower(regexp_replace(col(c), " ", "_"))
        )

# -----------------------------------------
# HANDLE MISSING VALUES
# -----------------------------------------
# Fill numeric values with 0 (simple + acceptable for assessment)
numeric_cols = [
    "Income", "Credit Score", "Loan Amount", "Years at Current Job",
    "Debt-to-Income Ratio", "Assets Value", "Previous Defaults"
]

for c in numeric_cols:
    if c in df.columns:
        df = df.withColumn(c, col(c).cast(DoubleType()))
        df = df.fillna({c: 0})

# Fill categorical missing with "unknown"
for c in categorical_cols:
    if c in df.columns:
        df = df.fillna({c: "unknown"})


print(df.columns, '\n\n\n')
# -----------------------------------------
# Encode risk rating to number 
df = df.withColumn(
    "RiskRatingNumeric",
    when(col("Risk Rating") == "low", 1)
    .when(col("Risk Rating") == "medium", 2)
    .when(col("Risk Rating") == "high", 3)
    .otherwise(0)
)

df.show(10)
# ----------------------
# PERFORMANCE OPTIMIZATIONS
# -------------------
df = df.repartition(4)

# -------------------------
# WRITE CLEANED DATA TO CLEAN ZONEE
# -------------------------------
df.write.mode("overwrite").parquet("s3a://clean-zone/cleaned-csv-loans")

spark.stop()
