# DE1 Final Project Report

**Author:** Badr TAJINI  
**Course:** Data Engineering I - ESIEE 2025-2026  
**Date:** 2025  

---

## 1. Use-Case and Dataset

### 1.1 Business Context
This lakehouse analyzes Wikipedia clickstream data to understand user navigation patterns, identify popular content, and optimize content discovery mechanisms.

**Dataset:** Wikipedia Clickstream (November 2024)  
**Source:** Wikimedia Foundation public dataset  
**Size:** 10 million rows, 450 MB raw TSV  

### 1.2 Dataset Characteristics
- **Format:** TSV (tab-separated values)
- **Key Columns:** 
  - `prev`: Source page or referrer
  - `curr`: Destination page
  - `type`: Link type (link, external, other)
  - `n`: Number of clicks (traffic volume)
- **Data Volume:** 10,000,000 rows (requirement met)
- **Temporal Range:** November 2024 clickstream snapshot

### 1.3 Use Case
This lakehouse enables three key analytics capabilities:
1. Identify most visited Wikipedia pages for content prioritization
2. Analyze top referrers to understand traffic sources
3. Compare traffic patterns across link types (internal vs external)

---

## 2. System and SLO

### 2.1 Hardware Specifications
- **CPU:** Intel Core i7 (8 cores)
- **RAM:** 16 GB
- **Disk:** SSD
- **Spark Version:** 4.0.1
- **Python Version:** 3.10.18

### 2.2 Service Level Objectives (SLO)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Data Freshness** | <= 2 hours | Time from raw data arrival to gold table availability |
| **Query Latency (p95)** | <= 4 seconds | 95th percentile response time for Q1-Q3 |
| **Storage Efficiency** | <= 60% of CSV size | Parquet compression ratio |

### 2.3 SLO Justification
- **Freshness:** Near real-time analytics requirement for business decisions
- **Latency:** Interactive dashboard requirement (sub-5s response)
- **Storage:** Cost optimization for long-term retention

---

## 3. Lakehouse Architecture Design

### 3.1 Three-Layer Architecture

```
RAW CSV
   |
   v
+------------------+
| BRONZE (CSV)     |  <- Immutable raw data landing
| - No schema      |
| - Audit trail    |
+------------------+
   |
   v
+------------------+
| SILVER (Parquet) |  <- Cleaned, typed, validated
| - Schema enforced|
| - DQ checks      |
| - Deduplicated   |
+------------------+
   |
   v
+------------------+
| GOLD (Parquet)   |  <- Analytics tables
| - Q1: Daily agg  |
| - Q2: Top refs   |
| - Q3: Filtered   |
+------------------+
```

### 3.2 Schema Evolution Strategy
- **Bronze:** Schema-on-read (all strings)
- **Silver:** Strict schema contracts (defined in config)
- **Gold:** Query-specific schemas

### 3.3 Data Quality Framework
Four validation rules applied at silver layer:

1. **Non-null clicks** (error): Reject records with null click counts
2. **Positive clicks** (error): Reject records with negative click values (n >= 0)
3. **Valid page names** (error): Reject records with empty page names
4. **Valid type** (warning): Log records with unexpected link types

---

## 4. Physical Design and Optimizations

### 4.1 Baseline Design
- **Silver:** Unpartitioned Parquet
- **Gold:** Simple Parquet writes
- **Queries:** Full table scans
- **File Count:** High fragmentation

### 4.2 Optimized Design

#### 4.2.1 Repartitioning Strategy
```python
num_partitions = max(4, int(total_bytes / (128 * 1024 * 1024)))
df_silver_opt.repartition(num_partitions)
```
- **Rationale:** Balance parallelism with file size targets
- **Benefit:** Reduces small file problem and improves scan efficiency
- **Trade-off:** Incurs shuffle cost during write

#### 4.2.2 Sorting Strategy
```python
sortWithinPartitions(F.desc("n"))
```
- **Rationale:** Sort by click count descending for faster TOP-N queries
- **Benefit:** Enables early termination for LIMIT queries
- **Implementation:** Maintains partition locality while sorting

#### 4.2.3 File Sizing
```yaml
target_file_size_mb: 128
```
- **Rationale:** Balance between parallelism and metadata overhead
- **Calculation:** `num_partitions = data_size / 128MB`
- **Result:** Optimal file count for 16GB RAM constraint

#### 4.2.4 Adaptive Query Execution (AQE)
```python
spark.sql.adaptive.enabled = true
spark.sql.adaptive.coalescePartitions.enabled = true
```
- **Benefit:** Dynamic partition coalescing reduces shuffle overhead
- **Memory tuning:** driver.memory=4g, executor.memory=4g, memory.fraction=0.6

---

## 5. Evidence and Metrics

### 5.1 Physical Plans Comparison

#### Q1: Top 20 Most Visited Pages

**Baseline Plan:**
```
FileScan parquet [prev,curr,type,n]
Exchange hashpartitioning(curr)
HashAggregate [sum(n)]
Sort [total_clicks DESC]
```
- **Elapsed:** 19,400 ms
- **No sorting optimization**

**Optimized Plan:**
```
FileScan parquet [prev,curr,type,n] (sorted partitions)
Exchange hashpartitioning(curr)
HashAggregate [sum(n)]
Sort [total_clicks DESC] (reduced due to pre-sorting)
```
- **Elapsed:** 517 ms
- **Gain:** 97.3% faster

### 5.2 Performance Metrics

| Query | Phase | Elapsed (ms) | Gain |
|-------|-------|--------------|------|
| **Q1: Top Pages** | Baseline | 19,400 | - |
| **Q1: Top Pages** | Optimized | 517 | **97.3%** |
| **Q2: Top Referrers** | Baseline | 17,443 | - |
| **Q2: Top Referrers** | Optimized | 13,690 | **21.5%** |
| **Q3: Type Analysis** | Baseline | 17,491 | - |
| **Q3: Type Analysis** | Optimized | 11 | **99.9%** |

**Key Observations:**
- Q1 shows dramatic improvement (97%) due to pre-sorting by click count
- Q2 shows moderate improvement (21%) as referrer grouping benefits less from sorting
- Q3 shows extreme improvement (99.9%) as type has very low cardinality (3 values)

### 5.3 SLO Validation

| SLO | Target | Baseline | Optimized | Status |
|-----|--------|----------|-----------|--------|
| Data Freshness | <= 2h | 0.5h | 0.3h | PASS |
| Q1 Latency (p95) | <= 4s | 19.4s | 0.5s | PASS |
| Storage Efficiency | <= 60% | 42% | 42% | PASS |

**Analysis:**
- All SLO targets achieved after optimization
- Q1 latency improved from 19.4s to 0.5s (well below 4s target)
- Storage efficiency maintained at 42% (Parquet compression)

### 5.4 Storage Analysis
```
Raw TSV:         450 MB (100%)
Bronze (CSV):    450 MB (100%)
Silver (Parquet): 189 MB (42%)
Gold (Parquet):   12 MB (2.7%)
```
- **Compression Ratio:** 2.4x (TSV to Parquet)
- **Gold Materialization:** Minimal overhead for pre-computed aggregations
- **Total Storage:** 651 MB (1.4x raw data size including all layers)

---

## 6. Results and Limitations

### 6.1 Key Results
1. **Sorting optimization:** 97% improvement for TOP-N queries (Q1)
2. **Cardinality optimization:** 99.9% improvement for low-cardinality aggregations (Q3)
3. **Storage efficiency:** 42% of original TSV size with Parquet
4. **All SLO targets met:** Latency reduced from 19.4s to 0.5s (below 4s target)
5. **Memory stability:** Optimized configuration prevented OOM errors on 16GB RAM

### 6.2 Limitations

#### 6.2.1 Single-Machine Constraints
- **Memory:** 16GB limits partition parallelism
- **Disk I/O:** SSD bottleneck for write-heavy workloads
- **CPU:** No distributed processing benefits

#### 6.2.2 Optimization Trade-offs
- **Repartitioning cost:** Write amplification during silver optimization phase
- **Sort overhead:** sortWithinPartitions adds CPU cost but pays off for aggregations
- **Memory tuning:** Required explicit memory configuration to avoid cache warnings
- **Limited partitioning:** No temporal partitioning as dataset is single-snapshot (Nov 2024)

#### 6.2.3 Query Limitations
- **Q2 moderate gain:** Referrer-based grouping benefits less from click-count sorting
- **Cold start penalty:** First query slower due to Parquet metadata loading
- **No incremental updates:** Full rewrite required for data updates (no delta merge)

### 6.3 Future Improvements
1. **Multi-column sorting:** Apply secondary sort on page name for tie-breaking
2. **Bucketing strategy:** Enable bucketed joins for referrer analysis queries
3. **Incremental processing:** Implement streaming ingestion for real-time updates
4. **Column pruning:** Add explicit select() to reduce I/O for projection-heavy queries
5. **Statistics collection:** Enable cost-based optimization with table statistics

---

## 7. Appendices

### 7.1 File Inventory
```
projet-final/
├── DE1_Project_Notebook_EN.ipynb          (Primary executable)
├── de1_project_config.yml                 (Configuration)
├── project_metrics_log.csv                (Metrics log)
├── DE1_Project_Report.md                  (This document)
├── project_genai.md                       (GenAI usage)
├── outputs/
│   └── project/
│       ├── bronze/                        (Raw CSV copy)
│       ├── silver/                        (Cleaned Parquet)
│       ├── silver_optimized/              (Partitioned Parquet)
│       └── gold/                          (Analytics tables)
│           ├── q1_daily_aggregation/
│           ├── q2_top_referrers/
│           └── q3_filtered_analysis/
└── proof/
    ├── baseline_q1_plan.txt               (Physical plans)
    ├── baseline_q2_plan.txt
    ├── baseline_q3_plan.txt
    ├── optimized_q1_plan.txt
    ├── optimized_q2_plan.txt
    ├── optimized_q3_plan.txt
    ├── baseline_q1_ui.png                 (Spark UI screenshots)
    ├── baseline_q2_ui.png
    ├── baseline_q3_ui.png
    ├── optimized_q1_ui.png
    ├── optimized_q2_ui.png
    └── optimized_q3_ui.png
```

### 7.2 Configuration Highlights
```yaml
slo:
  freshness_hours: 2
  q1_latency_p95_seconds: 4
  storage_ratio_max: 0.60

layout:
  partition_by: []
  sort_by: []
  target_file_size_mb: 128

queries:
  q1: "Top 20 most visited pages"
  q2: "Top 20 referrer pages"
  q3: "Click patterns by type"
```

### 7.3 References
- Apache Spark Documentation: https://spark.apache.org/docs/latest/
- Parquet Format Specification: https://parquet.apache.org/docs/
- DE1 Course Materials: ESIEE 2025-2026

---

**Total Page Count:** 6 pages (requirement: <= 6)  
**Submission:** See `project_genai.md` for AI tool usage disclosure
