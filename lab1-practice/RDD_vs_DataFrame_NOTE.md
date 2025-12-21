# RDD_vs_DataFrame_NOTE.md

## DE1 Lab 1: PySpark Warmup and Reading Plans
**Student:** Samba DIALLO | **Date:** 2025-10-23 | **AI Assistant:** Claude Haiku 4.5

---

## Overview

This lab compares **RDD API** vs **DataFrame API** in Apache Spark through three implementations:
1. **Top-N word count with RDD** (tokenization, reduceByKey, collect)
2. **Top-N word count with DataFrame** (explode, groupBy, agg)
3. **Projection optimization experiment** (select(*) vs select(col1, col2))

---

## How Claude Haiku 4.5 Assisted

### 1. **Setup & Environment Issues** 
- **Problem:** FileNotFoundError for SPARK_HOME path (`/path/to/spark-4.0.0-bin-hadoop3`)
- **AI Solution:** Identified fake path, provided conda-based PySpark configuration
- **Result:** Verified Spark 4.0.1 installation, fixed SPARK_HOME environment variable

### 2. **CSV Path Resolution** 
- **Problem:** Spark couldn't find `data/lab1_dataset_a.csv`
- **AI Solution:** Provided two options (move files or use absolute paths)
- **Result:** Lab executes successfully with correct file paths

### 3. **Metrics Extraction from Spark UI** 
- **Problem:** Unclear how to extract Job ID, Stage ID, shuffle bytes from Spark UI
- **AI Solution:** Mapped official rubric columns to UI locations
- **Result:** Correctly populated `lab1_metrics_log.csv` with 14 fields

### 4. **Comparative Analysis** 
- **Problem:** How to interpret Case A vs Case B results
- **AI Solution:** Provided Python code for shuffle reduction and time ratios
- **Result:** Generated automated comparative analysis

### 5. **Query Plan Evidence** 
- **Problem:** Need to save Spark physical execution plans
- **AI Solution:** Provided extraction code with timestamps
- **Result:** Created `proof/plan_rdd.txt` and `proof/plan_df.txt`

### 6. **Git & Documentation** 
- **Problem:** How to structure multi-part deliverables
- **AI Solution:** Semantic commit messages and file organization
- **Result:** Clean commit history with proof artifacts

---

## Key Lab Findings

| Metric | Case A (select *) | Case B (select category, value) |
|--------|------------------|--------------------------------|
| **Shuffle Write** | 560 B / 8 records | 560 B / 8 records |
| **Elapsed Time** | 25 ms | 30 ms |
| **Stages** | 1/1 (2 skipped) | 1/1 (1 skipped) |
| **Locality** | PROCESS_LOCAL | PROCESS_LOCAL |

**Observation:** Both cases produced identical shuffle write size due to Catalyst optimizer.

---

## Deliverables

-  `DE1_Lab1_Notebook_EN.ipynb` — Complete notebook with 5 sections
-  `outputs/top10_rdd.csv` — RDD-based word counts
-  `outputs/top10_df.csv` — DataFrame-based word counts
-  `outputs/lab1_metrics_log.csv` — Spark UI metrics (14 fields)
-  `proof/plan_rdd.txt` — RDD physical execution plan
-  `proof/plan_df.txt` — DataFrame physical execution plan

---

## Conclusion

**Claude Haiku 4.5** accelerated the lab by:
1. Diagnosing environment setup issues immediately
2. Explaining Spark UI metric extraction (critical for performance analysis)
3. Automating comparative analysis and result interpretation
4. Ensuring deliverables matched official rubric expectations

**Lab Goal Achieved:** Demonstrated competency in both RDD and DataFrame APIs with objective performance metrics from Spark UI.

---

**Reference:** 
- Labs Annexe: Spark Guide de l'interface utilisateur EN
- Official Rubric: DE1 Lab1 Rubric EN
- Spark Version: 4.0.1 | Python: 3.10.18 | Env: conda de1-env
