# DE1 — Lab 3: Physical Representations and Batch II Costs
> Author : Badr TAJINI - Data Engineering I - ESIEE 2025-2026
---

Execute all cells. Capture plans and Spark UI evidence.

## 0. Setup and explicit schema


```python
from pyspark.sql import SparkSession, functions as F, types as T
spark = SparkSession.builder.appName("de1-lab3").getOrCreate()

clicks_schema = T.StructType([
    T.StructField("prev_title", T.StringType(), True),
    T.StructField("curr_title", T.StringType(), True),
    T.StructField("type", T.StringType(), True),
    T.StructField("n", T.IntegerType(), True),
    T.StructField("ts", T.TimestampType(), True),
])
dim_schema = T.StructType([
    T.StructField("curr_title", T.StringType(), True),
    T.StructField("curr_category", T.StringType(), True),
])

```

    WARNING: Using incubator modules: jdk.incubator.vector
    Using Spark's default log4j profile: org/apache/spark/log4j2-defaults.properties
    25/12/20 14:17:49 WARN Utils: Your hostname, sable-ThinkPad-X1-Yoga-3rd, resolves to a loopback address: 127.0.1.1; using 10.192.33.105 instead (on interface wlp2s0)
    25/12/20 14:17:49 WARN Utils: Set SPARK_LOCAL_IP if you need to bind to another address
    Using Spark's default log4j profile: org/apache/spark/log4j2-defaults.properties
    Setting default log level to "WARN".
    To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
    25/12/20 14:17:53 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
    25/12/20 14:17:56 WARN Utils: Service 'SparkUI' could not bind on port 4040. Attempting port 4041.


## 1. Ingest monthly CSVs (row format baseline)


```python
base = "/home/sable/Documents/data engineering1/lab3-practice/data/"
paths = [f"{base}lab3_clicks_2025-05.csv", f"{base}lab3_clicks_2025-06.csv", f"{base}lab3_clicks_2025-07.csv"]
row_df = (spark.read.schema(clicks_schema).option("header","true").csv(paths)
            .withColumn("year", F.year("ts")).withColumn("month", F.month("ts")))
row_df.cache()
print("Rows:", row_df.count())
row_df.printSchema()
row_df.show(5, truncate=False)

```

                                                                                    

    Rows: 15000
    root
     |-- prev_title: string (nullable = true)
     |-- curr_title: string (nullable = true)
     |-- type: string (nullable = true)
     |-- n: integer (nullable = true)
     |-- ts: timestamp (nullable = true)
     |-- year: integer (nullable = true)
     |-- month: integer (nullable = true)
    
    +-----------------------------+--------------+----+---+-------------------+----+-----+
    |prev_title                   |curr_title    |type|n  |ts                 |year|month|
    +-----------------------------+--------------+----+---+-------------------+----+-----+
    |ETL                          |PySpark       |link|431|2025-06-01 02:57:00|2025|6    |
    |Data_engineering             |Broadcast_join|link|347|2025-06-15 13:40:00|2025|6    |
    |Python_(programming_language)|MapReduce     |link|39 |2025-06-07 15:14:00|2025|6    |
    |ETL                          |Data_warehouse|link|401|2025-06-07 04:59:00|2025|6    |
    |Python_(programming_language)|Dataframe     |link|155|2025-06-06 06:40:00|2025|6    |
    +-----------------------------+--------------+----+---+-------------------+----+-----+
    only showing top 5 rows


### Evidence: row representation plan


```python
# Query Q1: top transitions per month for 'link'
q1_row = (row_df.filter(F.col("type")=="link")
           .groupBy("year","month","prev_title","curr_title")
           .agg(F.sum("n").alias("n"))
           .orderBy(F.desc("n"))
           .limit(50))
q1_row.explain("formatted")

import pathlib, datetime as _dt
pathlib.Path("proof").mkdir(exist_ok=True)
with open("proof/plan_row.txt","w") as f:
    f.write(str(_dt.datetime.now())+"\n")
    f.write(q1_row._jdf.queryExecution().executedPlan().toString())
print("Saved proof/plan_row.txt")

```

    == Physical Plan ==
    AdaptiveSparkPlan (11)
    +- TakeOrderedAndProject (10)
       +- HashAggregate (9)
          +- Exchange (8)
             +- HashAggregate (7)
                +- Project (6)
                   +- Filter (5)
                      +- InMemoryTableScan (1)
                            +- InMemoryRelation (2)
                                  +- * Project (4)
                                     +- Scan csv  (3)
    
    
    (1) InMemoryTableScan
    Output [6]: [curr_title#1, month#7, n#3, prev_title#0, type#2, year#6]
    Arguments: [curr_title#1, month#7, n#3, prev_title#0, type#2, year#6], [isnotnull(type#2), (type#2 = link)]
    
    (2) InMemoryRelation
    Arguments: [prev_title#0, curr_title#1, type#2, n#3, ts#4, year#6, month#7], StorageLevel(disk, memory, deserialized, 1 replicas)
    
    (3) Scan csv 
    Output [5]: [prev_title#0, curr_title#1, type#2, n#3, ts#4]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab3-practice/data/lab3_clicks_2025-05.csv, ... 2 entries]
    ReadSchema: struct<prev_title:string,curr_title:string,type:string,n:int,ts:timestamp>
    
    (4) Project [codegen id : 1]
    Output [7]: [prev_title#0, curr_title#1, type#2, n#3, ts#4, year(cast(ts#4 as date)) AS year#6, month(cast(ts#4 as date)) AS month#7]
    Input [5]: [prev_title#0, curr_title#1, type#2, n#3, ts#4]
    
    (5) Filter
    Input [6]: [curr_title#1, month#7, n#3, prev_title#0, type#2, year#6]
    Condition : (isnotnull(type#2) AND (type#2 = link))
    
    (6) Project
    Output [5]: [prev_title#0, curr_title#1, n#3, year#6, month#7]
    Input [6]: [curr_title#1, month#7, n#3, prev_title#0, type#2, year#6]
    
    (7) HashAggregate
    Input [5]: [prev_title#0, curr_title#1, n#3, year#6, month#7]
    Keys [4]: [year#6, month#7, prev_title#0, curr_title#1]
    Functions [1]: [partial_sum(n#3)]
    Aggregate Attributes [1]: [sum#510L]
    Results [5]: [year#6, month#7, prev_title#0, curr_title#1, sum#511L]
    
    (8) Exchange
    Input [5]: [year#6, month#7, prev_title#0, curr_title#1, sum#511L]
    Arguments: hashpartitioning(year#6, month#7, prev_title#0, curr_title#1, 200), ENSURE_REQUIREMENTS, [plan_id=85]
    
    (9) HashAggregate
    Input [5]: [year#6, month#7, prev_title#0, curr_title#1, sum#511L]
    Keys [4]: [year#6, month#7, prev_title#0, curr_title#1]
    Functions [1]: [sum(n#3)]
    Aggregate Attributes [1]: [sum(n#3)#404L]
    Results [5]: [year#6, month#7, prev_title#0, curr_title#1, sum(n#3)#404L AS n#396L]
    
    (10) TakeOrderedAndProject
    Input [5]: [year#6, month#7, prev_title#0, curr_title#1, n#396L]
    Arguments: 50, [n#396L DESC NULLS LAST], [year#6, month#7, prev_title#0, curr_title#1, n#396L]
    
    (11) AdaptiveSparkPlan
    Output [5]: [year#6, month#7, prev_title#0, curr_title#1, n#396L]
    Arguments: isFinalPlan=false
    
    
    Saved proof/plan_row.txt


## 2. Column representation: Parquet with partitioning and optional sort


```python
col_base = "outputs/lab3/columnar"

# Write columnar
(row_df
 .write.mode("overwrite")
 .partitionBy("year","month")
 .parquet(f"{col_base}/clicks_parquet"))

# Re-read columnar (Spark infère le schéma depuis Parquet)
col_df = spark.read.parquet(f"{col_base}/clicks_parquet")
col_df.cache()
print("Columnar rows:", col_df.count())
```

    Columnar rows: 15000


### Evidence: column representation plan


```python
q1_col = (col_df.filter(F.col("type")=="link")
           .groupBy("year","month","prev_title","curr_title")
           .agg(F.sum("n").alias("n"))
           .orderBy(F.desc("n"))
           .limit(50))
q1_col.explain("formatted")
with open("proof/plan_column.txt","w") as f:
    from datetime import datetime as _dt
    f.write(str(_dt.now())+"\n")
    f.write(q1_col._jdf.queryExecution().executedPlan().toString())
print("Saved proof/plan_column.txt")

```

    == Physical Plan ==
    AdaptiveSparkPlan (11)
    +- TakeOrderedAndProject (10)
       +- HashAggregate (9)
          +- Exchange (8)
             +- HashAggregate (7)
                +- Project (6)
                   +- Filter (5)
                      +- InMemoryTableScan (1)
                            +- InMemoryRelation (2)
                                  +- * ColumnarToRow (4)
                                     +- Scan parquet  (3)
    
    
    (1) InMemoryTableScan
    Output [6]: [curr_title#793, month#798, n#795, prev_title#792, type#794, year#797]
    Arguments: [curr_title#793, month#798, n#795, prev_title#792, type#794, year#797], [isnotnull(type#794), (type#794 = link)]
    
    (2) InMemoryRelation
    Arguments: [prev_title#792, curr_title#793, type#794, n#795, ts#796, year#797, month#798], StorageLevel(disk, memory, deserialized, 1 replicas)
    
    (3) Scan parquet 
    Output [7]: [prev_title#792, curr_title#793, type#794, n#795, ts#796, year#797, month#798]
    Batched: true
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab3-practice/outputs/lab3/columnar/clicks_parquet]
    ReadSchema: struct<prev_title:string,curr_title:string,type:string,n:int,ts:timestamp>
    
    (4) ColumnarToRow [codegen id : 1]
    Input [7]: [prev_title#792, curr_title#793, type#794, n#795, ts#796, year#797, month#798]
    
    (5) Filter
    Input [6]: [curr_title#793, month#798, n#795, prev_title#792, type#794, year#797]
    Condition : (isnotnull(type#794) AND (type#794 = link))
    
    (6) Project
    Output [5]: [prev_title#792, curr_title#793, n#795, year#797, month#798]
    Input [6]: [curr_title#793, month#798, n#795, prev_title#792, type#794, year#797]
    
    (7) HashAggregate
    Input [5]: [prev_title#792, curr_title#793, n#795, year#797, month#798]
    Keys [4]: [year#797, month#798, prev_title#792, curr_title#793]
    Functions [1]: [partial_sum(n#795)]
    Aggregate Attributes [1]: [sum#1135L]
    Results [5]: [year#797, month#798, prev_title#792, curr_title#793, sum#1136L]
    
    (8) Exchange
    Input [5]: [year#797, month#798, prev_title#792, curr_title#793, sum#1136L]
    Arguments: hashpartitioning(year#797, month#798, prev_title#792, curr_title#793, 200), ENSURE_REQUIREMENTS, [plan_id=202]
    
    (9) HashAggregate
    Input [5]: [year#797, month#798, prev_title#792, curr_title#793, sum#1136L]
    Keys [4]: [year#797, month#798, prev_title#792, curr_title#793]
    Functions [1]: [sum(n#795)]
    Aggregate Attributes [1]: [sum(n#795)#1029L]
    Results [5]: [year#797, month#798, prev_title#792, curr_title#793, sum(n#795)#1029L AS n#1021L]
    
    (10) TakeOrderedAndProject
    Input [5]: [year#797, month#798, prev_title#792, curr_title#793, n#1021L]
    Arguments: 50, [n#1021L DESC NULLS LAST], [year#797, month#798, prev_title#792, curr_title#793, n#1021L]
    
    (11) AdaptiveSparkPlan
    Output [5]: [year#797, month#798, prev_title#792, curr_title#793, n#1021L]
    Arguments: isFinalPlan=false
    
    
    Saved proof/plan_column.txt


## 3. Join strategy: normal vs broadcast


```python
dim = spark.read.schema(dim_schema).option("header","true").csv("data/lab3_dim_curr_category.csv")
# Non‑broadcast join
j1 = (col_df.join(dim, "curr_title", "left")
      .groupBy("curr_category")
      .agg(F.sum("n").alias("total_n"))
      .orderBy(F.desc("total_n")))
j1.explain("formatted")

# Broadcast join
from pyspark.sql.functions import broadcast
j2 = (col_df.join(broadcast(dim), "curr_title", "left")
      .groupBy("curr_category")
      .agg(F.sum("n").alias("total_n"))
      .orderBy(F.desc("total_n")))
j2.explain("formatted")

# Save one plan for evidence
with open("proof/plan_broadcast.txt","w") as f:
    from datetime import datetime as _dt
    f.write(str(_dt.now())+"\n")
    f.write(j2._jdf.queryExecution().executedPlan().toString())
print("Saved proof/plan_broadcast.txt")

```

    == Physical Plan ==
    AdaptiveSparkPlan (15)
    +- Sort (14)
       +- Exchange (13)
          +- HashAggregate (12)
             +- Exchange (11)
                +- HashAggregate (10)
                   +- Project (9)
                      +- BroadcastHashJoin LeftOuter BuildRight (8)
                         :- InMemoryTableScan (1)
                         :     +- InMemoryRelation (2)
                         :           +- * ColumnarToRow (4)
                         :              +- Scan parquet  (3)
                         +- BroadcastExchange (7)
                            +- Filter (6)
                               +- Scan csv  (5)
    
    
    (1) InMemoryTableScan
    Output [2]: [curr_title#793, n#795]
    Arguments: [curr_title#793, n#795]
    
    (2) InMemoryRelation
    Arguments: [prev_title#792, curr_title#793, type#794, n#795, ts#796, year#797, month#798], StorageLevel(disk, memory, deserialized, 1 replicas)
    
    (3) Scan parquet 
    Output [7]: [prev_title#792, curr_title#793, type#794, n#795, ts#796, year#797, month#798]
    Batched: true
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab3-practice/outputs/lab3/columnar/clicks_parquet]
    ReadSchema: struct<prev_title:string,curr_title:string,type:string,n:int,ts:timestamp>
    
    (4) ColumnarToRow [codegen id : 1]
    Input [7]: [prev_title#792, curr_title#793, type#794, n#795, ts#796, year#797, month#798]
    
    (5) Scan csv 
    Output [2]: [curr_title#1137, curr_category#1138]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab3-practice/data/lab3_dim_curr_category.csv]
    PushedFilters: [IsNotNull(curr_title)]
    ReadSchema: struct<curr_title:string,curr_category:string>
    
    (6) Filter
    Input [2]: [curr_title#1137, curr_category#1138]
    Condition : isnotnull(curr_title#1137)
    
    (7) BroadcastExchange
    Input [2]: [curr_title#1137, curr_category#1138]
    Arguments: HashedRelationBroadcastMode(List(input[0, string, false]),false), [plan_id=241]
    
    (8) BroadcastHashJoin
    Left keys [1]: [curr_title#793]
    Right keys [1]: [curr_title#1137]
    Join type: LeftOuter
    Join condition: None
    
    (9) Project
    Output [2]: [n#795, curr_category#1138]
    Input [4]: [curr_title#793, n#795, curr_title#1137, curr_category#1138]
    
    (10) HashAggregate
    Input [2]: [n#795, curr_category#1138]
    Keys [1]: [curr_category#1138]
    Functions [1]: [partial_sum(n#795)]
    Aggregate Attributes [1]: [sum#1255L]
    Results [2]: [curr_category#1138, sum#1256L]
    
    (11) Exchange
    Input [2]: [curr_category#1138, sum#1256L]
    Arguments: hashpartitioning(curr_category#1138, 200), ENSURE_REQUIREMENTS, [plan_id=246]
    
    (12) HashAggregate
    Input [2]: [curr_category#1138, sum#1256L]
    Keys [1]: [curr_category#1138]
    Functions [1]: [sum(n#795)]
    Aggregate Attributes [1]: [sum(n#795)#1149L]
    Results [2]: [curr_category#1138, sum(n#795)#1149L AS total_n#1140L]
    
    (13) Exchange
    Input [2]: [curr_category#1138, total_n#1140L]
    Arguments: rangepartitioning(total_n#1140L DESC NULLS LAST, 200), ENSURE_REQUIREMENTS, [plan_id=249]
    
    (14) Sort
    Input [2]: [curr_category#1138, total_n#1140L]
    Arguments: [total_n#1140L DESC NULLS LAST], true, 0
    
    (15) AdaptiveSparkPlan
    Output [2]: [curr_category#1138, total_n#1140L]
    Arguments: isFinalPlan=false
    
    
    == Physical Plan ==
    AdaptiveSparkPlan (15)
    +- Sort (14)
       +- Exchange (13)
          +- HashAggregate (12)
             +- Exchange (11)
                +- HashAggregate (10)
                   +- Project (9)
                      +- BroadcastHashJoin LeftOuter BuildRight (8)
                         :- InMemoryTableScan (1)
                         :     +- InMemoryRelation (2)
                         :           +- * ColumnarToRow (4)
                         :              +- Scan parquet  (3)
                         +- BroadcastExchange (7)
                            +- Filter (6)
                               +- Scan csv  (5)
    
    
    (1) InMemoryTableScan
    Output [2]: [curr_title#793, n#795]
    Arguments: [curr_title#793, n#795]
    
    (2) InMemoryRelation
    Arguments: [prev_title#792, curr_title#793, type#794, n#795, ts#796, year#797, month#798], StorageLevel(disk, memory, deserialized, 1 replicas)
    
    (3) Scan parquet 
    Output [7]: [prev_title#792, curr_title#793, type#794, n#795, ts#796, year#797, month#798]
    Batched: true
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab3-practice/outputs/lab3/columnar/clicks_parquet]
    ReadSchema: struct<prev_title:string,curr_title:string,type:string,n:int,ts:timestamp>
    
    (4) ColumnarToRow [codegen id : 1]
    Input [7]: [prev_title#792, curr_title#793, type#794, n#795, ts#796, year#797, month#798]
    
    (5) Scan csv 
    Output [2]: [curr_title#1137, curr_category#1138]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab3-practice/data/lab3_dim_curr_category.csv]
    PushedFilters: [IsNotNull(curr_title)]
    ReadSchema: struct<curr_title:string,curr_category:string>
    
    (6) Filter
    Input [2]: [curr_title#1137, curr_category#1138]
    Condition : isnotnull(curr_title#1137)
    
    (7) BroadcastExchange
    Input [2]: [curr_title#1137, curr_category#1138]
    Arguments: HashedRelationBroadcastMode(List(input[0, string, false]),false), [plan_id=287]
    
    (8) BroadcastHashJoin
    Left keys [1]: [curr_title#793]
    Right keys [1]: [curr_title#1137]
    Join type: LeftOuter
    Join condition: None
    
    (9) Project
    Output [2]: [n#795, curr_category#1138]
    Input [4]: [curr_title#793, n#795, curr_title#1137, curr_category#1138]
    
    (10) HashAggregate
    Input [2]: [n#795, curr_category#1138]
    Keys [1]: [curr_category#1138]
    Functions [1]: [partial_sum(n#795)]
    Aggregate Attributes [1]: [sum#1372L]
    Results [2]: [curr_category#1138, sum#1373L]
    
    (11) Exchange
    Input [2]: [curr_category#1138, sum#1373L]
    Arguments: hashpartitioning(curr_category#1138, 200), ENSURE_REQUIREMENTS, [plan_id=292]
    
    (12) HashAggregate
    Input [2]: [curr_category#1138, sum#1373L]
    Keys [1]: [curr_category#1138]
    Functions [1]: [sum(n#795)]
    Aggregate Attributes [1]: [sum(n#795)#1266L]
    Results [2]: [curr_category#1138, sum(n#795)#1266L AS total_n#1257L]
    
    (13) Exchange
    Input [2]: [curr_category#1138, total_n#1257L]
    Arguments: rangepartitioning(total_n#1257L DESC NULLS LAST, 200), ENSURE_REQUIREMENTS, [plan_id=295]
    
    (14) Sort
    Input [2]: [curr_category#1138, total_n#1257L]
    Arguments: [total_n#1257L DESC NULLS LAST], true, 0
    
    (15) AdaptiveSparkPlan
    Output [2]: [curr_category#1138, total_n#1257L]
    Arguments: isFinalPlan=false
    
    
    Saved proof/plan_broadcast.txt


## 4. Additional queries for metrics


```python
# Q2: daily GMV‑like metric (sum of n) for a specific title window
q2_row = (row_df.filter((F.col("type")=="link") & F.col("curr_title").isin("Apache_Spark","PySpark"))
           .groupBy("year","month","curr_title").agg(F.sum("n").alias("n")).orderBy("year","month","curr_title"))
q2_col = (col_df.filter((F.col("type")=="link") & F.col("curr_title").isin("Apache_Spark","PySpark"))
           .groupBy("year","month","curr_title").agg(F.sum("n").alias("n")).orderBy("year","month","curr_title"))

# Trigger
_ = q2_row.count(); _ = q2_col.count()

# Q3: heavy cardinality grouping
q3_row = row_df.groupBy("prev_title","curr_title").agg(F.sum("n").alias("n")).orderBy(F.desc("n")).limit(100)
q3_col = col_df.groupBy("prev_title","curr_title").agg(F.sum("n").alias("n")).orderBy(F.desc("n")).limit(100)
_ = q3_row.count(); _ = q3_col.count()

print("Open Spark UI at http://localhost:4040 while each job runs and record metrics into lab3_metrics_log.csv")

```

    Open Spark UI at http://localhost:4040 while each job runs and record metrics into lab3_metrics_log.csv


## 5. Save sample outputs


```python
import pathlib, pandas as pd
pathlib.Path("outputs/lab3").mkdir(parents=True, exist_ok=True)
q1_row.limit(10).toPandas().to_csv("outputs/lab3/q1_row_top10.csv", index=False)
q1_col.limit(10).toPandas().to_csv("outputs/lab3/q1_col_top10.csv", index=False)
j2.limit(20).toPandas().to_csv("outputs/lab3/j2_broadcast_sample.csv", index=False)
print("Saved sample outputs in outputs/lab3/")

```

    Saved sample outputs in outputs/lab3/


## 6. Cleanup


```python
spark.stop()
print("Spark session stopped.")

```

    Spark session stopped.

