# ESIEE Paris — Data Engineering I — Assignment 2
## ETL Pipeline & Star Schema Data Warehouse

**Authors:** DIALLO Samba, DIOP Mouhamed  
**Date:** October 30, 2025  
**Academic Year:** 2025-2026  
**Program:** Data & Applications - Engineering (FD)  
**Course:** Data Engineering I

---

## Executive Summary

This assignment involved building a complete ETL (Extract, Transform, Load) pipeline to transform operational retail data from PostgreSQL into a star schema data warehouse optimized for analytical queries. The project successfully processed **42.4 million events**, **3 million users**, and **166K products** using Apache Spark.

**Key Achievement:** Reduced storage footprint from **4.2 GB (CSV)** to **0.4 GB (Parquet)** — a **90% compression** while maintaining full data integrity.

---

## Objectives

1. Extract 7 tables from PostgreSQL operational database
2. Build 6 dimension tables (user, age, brand, category, product, date)
3. Create fact table with 42.4M events
4. Implement data quality gates
5. Export to multiple formats (CSV, Parquet)
6. Optimize for analytical queries

---

## Data Inputs

### Source Data
- **Database:** PostgreSQL 17 (port 5432)
- **Host:** 127.0.0.1
- **Database name:** esiee_full
- **Schema:** retail
- **User:** esiee_reader (read-only)

### Input Paths
```
BASE_DIR = "/home/sable/de1-work/assignment2"

Source CSVs:
├── user.csv           (3,022,290 rows)
├── session.csv        (6,884,356 rows)
├── product.csv        (166,794 rows)
├── product_name.csv   (83 rows)
├── events.csv         (42,418,541 rows)
├── category.csv       (13 rows)
└── brand.csv          (3,444 rows)
```

### Output Paths
```
OUTPUT_BASE = "/home/sable/de1-work/assignment2/outputs/assignment2"

Outputs:
├── fact_events.csv/          (uncompressed CSV)
├── fact_events.csv.snappy/   (compressed CSV)
└── fact_events.parquet/      (columnar Parquet)
```

---

## Architecture & Design

### Star Schema Design

```
┌─────────────────────────────────────────────────┐
│                 FACT TABLE                       │
│              fact_events                         │
│  (42,418,541 rows)                              │
│                                                  │
│  • date_key       → dim_date                    │
│  • user_key       → dim_user                    │
│  • age_key        → dim_age                     │
│  • product_key    → dim_product                 │
│  • brand_key      → dim_brand                   │
│  • category_key   → dim_category                │
│  • session_id     (business key)                │
│  • event_time     (timestamp)                   │
│  • event_type     (view/cart/purchase/remove)   │
│  • price          (double, nullable)            │
└─────────────────────────────────────────────────┘
              │
              ├──────┬──────┬──────┬──────┬──────┐
              │      │      │      │      │      │
              ▼      ▼      ▼      ▼      ▼      ▼
      ┌─────────┐ ┌─────┐ ┌────────┐ ┌──────┐ ┌────────┐ ┌──────┐
      │dim_user │ │ age │ │product │ │brand │ │category│ │ date │
      │3.02M    │ │ 10  │ │166.7K  │ │3.4K  │ │  13    │ │  32  │
      └─────────┘ └─────┘ └────────┘ └──────┘ └────────┘ └──────┘
```

---

## Implementation Details

### ETL Pipeline Stages

1. **Extract:** Load 7 CSV files from PostgreSQL export
2. **Transform:** 
   - Create surrogate keys for dimensions
   - Build type-2 slowly changing dimensions (age groups)
   - Aggregate event metrics
3. **Load:** Write star schema to Parquet format

### Technology Stack

- **Apache Spark 4.0.1** - Distributed processing
- **Python 3.10.18** - Primary language
- **PostgreSQL 17** - Source database
- **Parquet** - Storage format

---

## Results

### Storage Efficiency

| Format | Size | Compression Ratio |
|--------|------|-------------------|
| CSV (uncompressed) | 4.2 GB | 1.0x |
| CSV (Snappy) | 1.2 GB | 3.5x |
| Parquet | 0.4 GB | 10.5x |

### Data Quality

- **Completeness:** 100% of source records processed
- **Accuracy:** All foreign key relationships validated
- **Consistency:** Star schema conforms to dimensional modeling best practices

---

## Deliverables

1. `assignment2_esiee.ipynb` - Complete notebook with executed code
2. `REPORT.md` - This report
3. `assignment2_genai.md` - AI usage documentation
4. Output files:
   - `fact_events.csv/`
   - `fact_events.csv.snappy/`
   - `fact_events.parquet/`
   - Dimension tables (6 files)

---

## Generative AI Usage

For details on how generative AI was used in this assignment, see `assignment2_genai.md`.

**Summary:** We used **Claude Sonnet 4.5** (via GitHub Copilot) for debugging, code optimization, and documentation assistance.

---

## Conclusion

The assignment successfully demonstrated the ability to:
- Design and implement a star schema data warehouse
- Process large-scale datasets (42M+ rows) with Apache Spark
- Optimize storage with columnar formats (Parquet)
- Apply data engineering best practices

**Authors:** DIALLO Samba, DIOP Mouhamed  
**Submission Date:** October 30, 2025
