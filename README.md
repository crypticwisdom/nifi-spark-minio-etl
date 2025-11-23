# Doumentation
...


# **📘 Data Ingestion Layer — Apache NiFi (Short Overview)**

For the ingestion stage of this ETL pipeline, I used **Apache NiFi** to move raw CSV files into the data lake and convert them into **Parquet** before storage. NiFi was chosen to provide a clean separation between ingestion and transformation, ensuring a modular and operationally reliable pipeline.

### **Why NiFi Instead of Ingesting Directly with Spark**

* **Dedicated ingestion tool:** NiFi handles file detection, movement, retries, and provenance more effectively than Spark.
* **Operational visibility:** NiFi’s UI provides real-time tracking of each file and clear debugging if errors occur.
* **Pre-processing advantage:** Converting CSV → Parquet at the ingestion layer improves downstream Spark performance and reduces storage footprint.
* **Loose coupling:** Decouples ingestion from transformation, following best-practice pipeline design.

---

# **NiFi Flow Summary**

The ingestion pipeline follows a simple but effective flow:

```
ListFile → FetchFile → ConvertRecord → PutS3Object
```

### **Processor Breakdown**

* **ListFile**
  Detects new CSV files placed in the ingestion directory mounted at `/data/input`.

* **FetchFile**
  Retrieves the file content identified by ListFile.

* **ConvertRecord (CSV → Parquet)**
  Uses `CSVReader` and `ParquetRecordSetWriter` to convert raw CSV into optimized Parquet format.

* **PutS3Object (MinIO Upload)**
  Stores the transformed Parquet file in the MinIO **raw-parquet** bucket.
  `Object Key: ${filename:replace('.csv', '.parquet')}` ensures correct naming.

---

# **Result**

NiFi reliably ingests raw CSV files, performs lightweight pre-processing, and writes clean Parquet files into the data lake, providing a structured and efficient foundation for Spark transformations.




Below is a **clean, professional, concise** documentation you can include in your project’s README.
It covers:

* Architecture overview
* Why you chose this approach
* How to set up & run the environment
* NiFi flow (including exporting/importing the XML template)
* Spark transformation stage
* Brief description of the transactional dataset
* Why Parquet format was used

It is intentionally short, direct, and “assessment-ready”.

---

# 📘 **ETL Pipeline Documentation (NiFi → MinIO → Spark Processing)**

## 1. **Overview**

This project implements a simple but production-aligned ETL pipeline using:

* **Apache NiFi** → ingestion & file orchestration
* **MinIO (S3-compatible storage)** → staging and clean data zones
* **Apache Spark** → data cleaning, normalization, and transformation
* **Docker Compose** → environment orchestration

The goal is to ingest raw CSV files, convert them into an efficient columnar format (Parquet), and run downstream transformations that prepare the dataset for analytics or modeling.

---

## 2. **Why This Architecture Was Chosen**

### **Why NiFi for ingestion**

NiFi provides a flow-based, low-overhead ingestion layer with:

* Visual drag-and-drop dataflow configuration
* Built-in processors for CSV handling
* Native integration with S3-compatible storage (MinIO)
* Backpressure, retries, provenance tracking
* Easy file routing and extension management

Instead of manually loading files with Spark, NiFi provides a **controlled, trackable, and auditable** ingestion pipeline that aligns with real-world data engineering best practices.

### **Why Spark for processing**

Spark is used because:

* It handles semi-structured financial/transactional data efficiently
* Supports scalable file-based ETL processing
* Provides built-in column operations for cleaning and transformation
* Integrates seamlessly with MinIO through the S3A connector

### **Why Parquet over CSV**

Parquet was chosen over CSV because:

* Columnar format → optimized for analytics
* Highly compressed → reduces MinIO storage cost
* Supports schema evolution
* Faster read performance
* Better for Spark-based processing

CSV is ideal for ingestion, but Parquet is the preferred format for transformation and downstream consumption.

---

## 3. **Dataset Summary (Transactional / Credit-Risk Data)**

The dataset represents **loan and financial risk assessment data**.
Each row contains attributes such as:

* Customer demographics (Age, Gender, Marital Status)
* Financial behavior (Income, Credit Score, Assets)
* Loan details (Loan Amount, Purpose, Employment Status, DTI Ratio)
* Historical indicators (Payment History, Previous Defaults)
* Risk Rating (low, medium, high)

The pipeline cleans, normalizes, and prepares this data so it can be used for:

* Risk scoring
* Creditworthiness analysis
* Exploratory analytics
* Model development

---

## 4. **Running the Project (Docker Compose)**

### **1. Clone the repository**

```
git clone <your repository>
cd <project-folder>
```

### **2. Build and start the environment**

```
docker compose build
docker compose up -d
```

### **3. Access the services**

| Service         | URL                                            |
| --------------- | ---------------------------------------------- |
| NiFi UI         | [http://localhost:8443](http://localhost:8443) |
| Spark Master UI | [http://localhost:8080](http://localhost:8080) |
| MinIO Console   | [http://localhost:9001](http://localhost:9001) |

### **4. Upload CSVs for ingestion**

Place CSV files into:

```
./data/input/
```

NiFi automatically picks them up and writes the processed Parquet files to MinIO.

---

## 5. **NiFi Flow**

### **Processors Used**

* **GetFile** → Reads CSVs from local mounted directory
* **UpdateAttribute** → Renames extension to `.parquet`
* **ConvertRecord** → Converts CSV → Parquet
* **PutS3Object** → Writes parquet data into MinIO bucket (`raw-zone/`)

### **NiFi Template**

You can import the NiFi flow template (.xml) manually:

**NiFi → Operate Palette → Upload Template → Choose XML → Add to Canvas**

This ensures the ingestion flow is fully reproducible when shared through GitHub.

> Store your template under:
> `nifi/templates/ingestion-flow.xml`

---

## 6. **Spark Processing Stage**

### **How to run a Spark job**

Enter the PySpark client container:

```
docker exec -it pyspark-client bash
```

Run the ETL script:

```
spark-submit \
  --master spark://spark-master:7077 \
  process-csv.py
```

### **What the Spark job does**

* Reads Parquet/CSV from MinIO through S3A
* Trims whitespace and standardizes text fields
* Normalizes categorical values (lowercase, underscores)
* Converts numeric fields to proper types
* Handles missing values
* Encodes risk rating into numeric values
* Writes cleaned dataset into:
  `s3a://clean-zone/cleaned-csv-loans/`

Transforms the dataset into a clean, analytics-ready format.

---

## 7. **Project Structure**

```
project/
│
├── docker-compose.yml
├── spark-scripts/
│   ├── Dockerfile
│   └── spark-scripts/
│        └── process-csv.py
│
├── nifi/
│   └── templates/
│        └── ingestion-flow.xml
│
├── data/
│   └── input/          # Files NiFi ingests
│
└── minio/
    └── minio_data/
```

---

## 8. **Conclusion**

This ETL pipeline demonstrates a realistic, scalable approach to handling financial/credit-risk transactional data.
It separates ingestion, storage, and processing layers — closely matching modern data engineering practices used in production environments.

NiFi handles the ingestion layer, Spark performs scalable transformations, and MinIO provides a flexible data lake environment.
The decision to use Parquet ensures efficient downstream computation, lower storage cost, and enhanced performance for big-data processing.
