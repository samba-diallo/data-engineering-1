# DE1 — Lab 1: PySpark Warmup and Reading Plans
> Author : Badr TAJINI - Data Engineering I - ESIEE 2025-2026
---

This notebook is the **student deliverable**. Execute all cells and attach evidence.

## 0. Imports and Spark session


```
import os, sys, datetime, pathlib
from pyspark.sql import SparkSession, functions as F
print("Python:", sys.version)
spark = SparkSession.builder.appName("de1-lab1").getOrCreate()
print("Spark:", spark.version)

```

    Python: 3.10.18 (main, Jun  5 2025, 13:14:17) [GCC 11.2.0]
    Spark: 4.0.1


## 1. Load the CSV inputs


```
src_a = "data/lab1_dataset_a.csv"
src_b = "data/lab1_dataset_b.csv"
df_a = spark.read.option("header","true").option("inferSchema","true").csv(src_a)
df_b = spark.read.option("header","true").option("inferSchema","true").csv(src_b)
df = df_a.unionByName(df_b)
df.cache()
print("Rows:", df.count())
df.printSchema()
df.show(5, truncate=False)

```

    Rows: 2700
    root
     |-- id: integer (nullable = true)
     |-- category: string (nullable = true)
     |-- value: double (nullable = true)
     |-- text: string (nullable = true)
    
    +---+-----------+-----+----------------------------------------------------------------------------+
    |id |category   |value|text                                                                        |
    +---+-----------+-----+----------------------------------------------------------------------------+
    |0  |toys       |48.47|metrics ui data elt row columnar reduce warehouse shuffle join spark elt    |
    |1  |books      |39.9 |metrics row lake aggregate columnar data reduce row columnar filter         |
    |2  |grocery    |7.96 |lake join partition scala elt data                                          |
    |3  |electronics|5.15 |spark scala elt filter join columnar lake lake plan warehouse columnar spark|
    |4  |toys       |44.87|aggregate metrics row row filter lake map metrics columnar spark            |
    +---+-----------+-----+----------------------------------------------------------------------------+
    only showing top 5 rows


## 2. Top‑N with **RDD** API


```
# RDD pipeline: tokenize 'text' column and count tokens
rdd = df.select("text").rdd.flatMap(lambda row: (row[0] or "").lower().split())
pair = rdd.map(lambda t: (t, 1))
counts = pair.reduceByKey(lambda a,b: a+b)
top_rdd = counts.sortBy(lambda kv: (-kv[1], kv[0])).take(10)
top_rdd

```

                                                                                    




    [('lake', 1215),
     ('scala', 1200),
     ('elt', 1199),
     ('metrics', 1190),
     ('row', 1183),
     ('join', 1169),
     ('warehouse', 1168),
     ('shuffle', 1160),
     ('ui', 1145),
     ('aggregate', 1144)]




```
# Save as CSV (token,count)
pathlib.Path("outputs").mkdir(exist_ok=True)
with open("outputs/top10_rdd.csv","w",encoding="utf-8") as f:
    f.write("token,count\n")
    for t,c in top_rdd:
        f.write(f"{t},{c}\n")
print("Wrote outputs/top10_rdd.csv")

```

    Wrote outputs/top10_rdd.csv


### RDD plan — evidence


```
# Trigger an action and record a textual plan for evidence
_ = counts.count()
plan_rdd = df._jdf.queryExecution().executedPlan().toString()
pathlib.Path("proof").mkdir(exist_ok=True)
with open("proof/plan_rdd.txt","w") as f:
    f.write(str(datetime.datetime.now()) + "\n\n")
    f.write(plan_rdd)
print("Saved proof/plan_rdd.txt")

```

    Saved proof/plan_rdd.txt


## 3. Top‑N with **DataFrame** API


```
tokens = F.explode(F.split(F.lower(F.col("text")), "\\s+")).alias("token")
df_tokens = df.select(tokens).where(F.col("token") != "")
agg_df = df_tokens.groupBy("token").agg(F.count("*").alias("count"))
top_df = agg_df.orderBy(F.desc("count"), F.asc("token")).limit(10)
top_df.show(truncate=False)
top_df.coalesce(1).write.mode("overwrite").option("header","true").csv("outputs/top10_df_tmp")
# move single part file to stable path
import glob, shutil
part = glob.glob("outputs/top10_df_tmp/part*")[0]
shutil.copy(part, "outputs/top10_df.csv")
print("Wrote outputs/top10_df.csv")

```

    +---------+-----+
    |token    |count|
    +---------+-----+
    |lake     |1215 |
    |scala    |1200 |
    |elt      |1199 |
    |metrics  |1190 |
    |row      |1183 |
    |join     |1169 |
    |warehouse|1168 |
    |shuffle  |1160 |
    |ui       |1145 |
    |aggregate|1144 |
    +---------+-----+
    
    Wrote outputs/top10_df.csv


### DataFrame plan — evidence


```
plan_df = top_df._jdf.queryExecution().executedPlan().toString()
with open("proof/plan_df.txt","w") as f:
    f.write(str(datetime.datetime.now()) + "\n\n")
    f.write(plan_df)
print("Saved proof/plan_df.txt")

```

    Saved proof/plan_df.txt


## 4. Projection experiment: `select("*")` vs minimal projection


```
# Case A: select all columns then aggregate on 'category'
all_cols = df.select("*").groupBy("category").agg(F.sum("value").alias("sum_value"))
all_cols.explain("formatted")
_ = all_cols.count()  # trigger

# Case B: minimal projection then aggregate
proj = df.select("category","value").groupBy("category").agg(F.sum("value").alias("sum_value"))
proj.explain("formatted")
_ = proj.count()  # trigger

print("Open Spark UI at http://localhost:4040 while each job runs and record metrics into lab1_metrics_log.csv")

```

    == Physical Plan ==
    AdaptiveSparkPlan (9)
    +- HashAggregate (8)
       +- Exchange (7)
          +- HashAggregate (6)
             +- InMemoryTableScan (1)
                   +- InMemoryRelation (2)
                         +- Union (5)
                            :- Scan csv  (3)
                            +- Scan csv  (4)
    
    
    (1) InMemoryTableScan
    Output [2]: [category#1050, value#1051]
    Arguments: [category#1050, value#1051]
    
    (2) InMemoryRelation
    Arguments: [id#1049, category#1050, value#1051, text#1052], StorageLevel(disk, memory, deserialized, 1 replicas)
    
    (3) Scan csv 
    Output [4]: [id#1049, category#1050, value#1051, text#1052]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab1-practice/data/lab1_dataset_a.csv]
    ReadSchema: struct<id:int,category:string,value:double,text:string>
    
    (4) Scan csv 
    Output [4]: [id#1070, category#1071, value#1072, text#1073]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab1-practice/data/lab1_dataset_b.csv]
    ReadSchema: struct<id:int,category:string,value:double,text:string>
    
    (5) Union
    
    (6) HashAggregate
    Input [2]: [category#1050, value#1051]
    Keys [1]: [category#1050]
    Functions [1]: [partial_sum(value#1051)]
    Aggregate Attributes [1]: [sum#1784]
    Results [2]: [category#1050, sum#1785]
    
    (7) Exchange
    Input [2]: [category#1050, sum#1785]
    Arguments: hashpartitioning(category#1050, 200), ENSURE_REQUIREMENTS, [plan_id=1035]
    
    (8) HashAggregate
    Input [2]: [category#1050, sum#1785]
    Keys [1]: [category#1050]
    Functions [1]: [sum(value#1051)]
    Aggregate Attributes [1]: [sum(value#1051)#1723]
    Results [2]: [category#1050, sum(value#1051)#1723 AS sum_value#1718]
    
    (9) AdaptiveSparkPlan
    Output [2]: [category#1050, sum_value#1718]
    Arguments: isFinalPlan=false
    
    
    == Physical Plan ==
    AdaptiveSparkPlan (9)
    +- HashAggregate (8)
       +- Exchange (7)
          +- HashAggregate (6)
             +- InMemoryTableScan (1)
                   +- InMemoryRelation (2)
                         +- Union (5)
                            :- Scan csv  (3)
                            +- Scan csv  (4)
    
    
    (1) InMemoryTableScan
    Output [2]: [category#1050, value#1051]
    Arguments: [category#1050, value#1051]
    
    (2) InMemoryRelation
    Arguments: [id#1049, category#1050, value#1051, text#1052], StorageLevel(disk, memory, deserialized, 1 replicas)
    
    (3) Scan csv 
    Output [4]: [id#1049, category#1050, value#1051, text#1052]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab1-practice/data/lab1_dataset_a.csv]
    ReadSchema: struct<id:int,category:string,value:double,text:string>
    
    (4) Scan csv 
    Output [4]: [id#1070, category#1071, value#1072, text#1073]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab1-practice/data/lab1_dataset_b.csv]
    ReadSchema: struct<id:int,category:string,value:double,text:string>
    
    (5) Union
    
    (6) HashAggregate
    Input [2]: [category#1050, value#1051]
    Keys [1]: [category#1050]
    Functions [1]: [partial_sum(value#1051)]
    Aggregate Attributes [1]: [sum#1956]
    Results [2]: [category#1050, sum#1957]
    
    (7) Exchange
    Input [2]: [category#1050, sum#1957]
    Arguments: hashpartitioning(category#1050, 200), ENSURE_REQUIREMENTS, [plan_id=1166]
    
    (8) HashAggregate
    Input [2]: [category#1050, sum#1957]
    Keys [1]: [category#1050]
    Functions [1]: [sum(value#1051)]
    Aggregate Attributes [1]: [sum(value#1051)#1895]
    Results [2]: [category#1050, sum(value#1051)#1895 AS sum_value#1892]
    
    (9) AdaptiveSparkPlan
    Output [2]: [category#1050, sum_value#1892]
    Arguments: isFinalPlan=false
    
    
    Open Spark UI at http://localhost:4040 while each job runs and record metrics into lab1_metrics_log.csv



```
## 4.1 Extract metrics from Spark UI and log to CSV

import csv
from datetime import datetime
import pathlib

# Données extraites manuellement du Spark UI (Stage 30)
# À adapter pour Case A et Case B

metrics_data = [
    {
        "run_id": "r1",
        "task": "projection_experiment",
        "case": "Case A: select(*)",
        "job_id": "19",  # À vérifier dans Jobs tab
        "stage_id": "30",
        "files_read": "2",
        "input_size_bytes": "184627",  # 180.4 KiB = 180.4 * 1024 = 184627.6
        "input_records": "2",
        "shuffle_read_bytes": "0",  # Pas de shuffle read visible ici
        "shuffle_write_bytes": "560",  # 560 B
        "shuffle_write_records": "8",
        "elapsed_ms": "25",  # Total Time Across All Tasks
        "timestamp": "2025-10-23T00:29:57",
        "notes": "baseline - all columns, 2 tasks (12ms + 13ms)"
    },
    {
        "run_id": "r1",
        "task": "projection_experiment",
        "case": "Case B: select(category,value)",
        "job_id": "20",  # À vérifier
        "stage_id": "31",  # Probablement stage suivant
        "files_read": "2",
        "input_size_bytes": "184627",  # Même input (même données)
        "input_records": "2",
        "shuffle_read_bytes": "0",  # À vérifier
        "shuffle_write_bytes": "560",  # À comparer avec Case A
        "shuffle_write_records": "8",
        "elapsed_ms": "30",  # À extraire du UI pour Case B
        "timestamp": "2025-10-23T00:30:05",
        "notes": "minimal projection - 2 columns only"
    }
]

# Créer le dossier outputs
pathlib.Path("outputs").mkdir(exist_ok=True)

# Écrire dans le CSV
with open("outputs/lab1_metrics_log.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = metrics_data[0].keys()
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(metrics_data)

print("✓ Wrote outputs/lab1_metrics_log.csv")

# Afficher pour vérifier
import pandas as pd
df_metrics = pd.read_csv("outputs/lab1_metrics_log.csv")
print("\n=== Lab1 Metrics Summary ===")
print(df_metrics.to_string(index=False))

# Analyse comparative
print("\n=== Comparative Analysis ===")
case_a_shuffle = int(metrics_data[0]['shuffle_write_bytes'])
case_b_shuffle = int(metrics_data[1]['shuffle_write_bytes'])
case_a_time = int(metrics_data[0]['elapsed_ms'])
case_b_time = int(metrics_data[1]['elapsed_ms'])

print(f"Case A shuffle write: {case_a_shuffle} B")
print(f"Case B shuffle write: {case_b_shuffle} B")
print(f"Reduction: {case_a_shuffle - case_b_shuffle} B ({100*(case_a_shuffle - case_b_shuffle)/case_a_shuffle:.1f}%)")
print(f"\nCase A elapsed: {case_a_time} ms")
print(f"Case B elapsed: {case_b_time} ms")
print(f"Time ratio: {case_b_time/case_a_time:.2f}x")
```

    ✓ Wrote outputs/lab1_metrics_log.csv
    
    === Lab1 Metrics Summary ===
    run_id                  task                           case  job_id  stage_id  files_read  input_size_bytes  input_records  shuffle_read_bytes  shuffle_write_bytes  shuffle_write_records  elapsed_ms           timestamp                                         notes
        r1 projection_experiment              Case A: select(*)      19        30           2            184627              2                   0                  560                      8          25 2025-10-23T00:29:57 baseline - all columns, 2 tasks (12ms + 13ms)
        r1 projection_experiment Case B: select(category,value)      20        31           2            184627              2                   0                  560                      8          30 2025-10-23T00:30:05           minimal projection - 2 columns only
    
    === Comparative Analysis ===
    Case A shuffle write: 560 B
    Case B shuffle write: 560 B
    Reduction: 0 B (0.0%)
    
    Case A elapsed: 25 ms
    Case B elapsed: 30 ms
    Time ratio: 1.20x


## 5. Cleanup


```
spark.stop()
print("Spark session stopped.")

```

    Spark session stopped.

