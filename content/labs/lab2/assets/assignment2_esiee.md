# Assignment 2: Data Engineering with PySpark

## Overview
This assignment focuses on building a data engineering pipeline using PySpark to process and analyze user activity data.

## Objectives
- Set up PySpark environment
- Load and explore data
- Perform data transformations
- Analyze user behavior patterns
- Export processed data

## Part 1: Environment Setup


```python
# Install required packages
!pip install pyspark pandas numpy matplotlib seaborn
```

    Requirement already satisfied: pyspark in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (4.0.1)
    Requirement already satisfied: pandas in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (2.3.3)
    Requirement already satisfied: numpy in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (2.2.6)
    Requirement already satisfied: matplotlib in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (3.10.8)
    Requirement already satisfied: seaborn in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (0.13.2)
    Requirement already satisfied: py4j==0.10.9.9 in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (from pyspark) (0.10.9.9)
    Requirement already satisfied: python-dateutil>=2.8.2 in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (from pandas) (2.9.0.post0)
    Requirement already satisfied: pytz>=2020.1 in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (from pandas) (2025.2)
    Requirement already satisfied: tzdata>=2022.7 in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (from pandas) (2025.2)
    Requirement already satisfied: contourpy>=1.0.1 in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (from matplotlib) (1.3.2)
    Requirement already satisfied: cycler>=0.10 in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (from matplotlib) (0.12.1)
    Requirement already satisfied: fonttools>=4.22.0 in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (from matplotlib) (4.60.1)
    Requirement already satisfied: kiwisolver>=1.3.1 in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (from matplotlib) (1.4.9)
    Requirement already satisfied: packaging>=20.0 in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (from matplotlib) (25.0)
    Requirement already satisfied: pillow>=8 in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (from matplotlib) (12.0.0)
    Requirement already satisfied: pyparsing>=3 in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (from matplotlib) (3.2.5)
    Requirement already satisfied: six>=1.5 in /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages (from python-dateutil>=2.8.2->pandas) (1.17.0)



```python
# Import necessary libraries
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("Libraries imported successfully")
```

    Libraries imported successfully



```python
# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Assignment2_DataEngineering") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

print("Spark session created successfully")
print(f"Spark version: {spark.version}")
```

    WARNING: Using incubator modules: jdk.incubator.vector
    Using Spark's default log4j profile: org/apache/spark/log4j2-defaults.properties
    25/12/28 19:16:35 WARN Utils: Your hostname, sable-ThinkPad-X1-Yoga-3rd, resolves to a loopback address: 127.0.1.1; using 10.192.33.105 instead (on interface wlp2s0)
    25/12/28 19:16:35 WARN Utils: Set SPARK_LOCAL_IP if you need to bind to another address
    Using Spark's default log4j profile: org/apache/spark/log4j2-defaults.properties
    Setting default log level to "WARN".
    To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
    25/12/28 19:16:35 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable


    Spark session created successfully
    Spark version: 4.0.1


## Part 2: Data Loading and Exploration


```python
# Define schema for user activity data
schema = StructType([
    StructField("user_id", IntegerType(), False),
    StructField("username", StringType(), False),
    StructField("action", StringType(), False),
    StructField("timestamp", TimestampType(), False),
    StructField("device", StringType(), True),
    StructField("location", StringType(), True),
    StructField("duration_seconds", IntegerType(), True)
])

print("Schema defined")
```

    Schema defined



```python
# Load data from CSV file
print("Loading data...")
df = spark.read.csv(
    "data/user_activity.csv",
    header=True,
    schema=schema
)

print("Data loaded successfully")
print(f"Total records: {df.count()}")
```

    Loading data...


    25/12/28 19:16:40 WARN FileStreamSink: Assume no metadata directory. Error while looking for metadata directory in the path: data/user_activity.csv.
    java.io.FileNotFoundException: File data/user_activity.csv does not exist
    	at org.apache.hadoop.fs.RawLocalFileSystem.deprecatedGetFileStatus(RawLocalFileSystem.java:917)
    	at org.apache.hadoop.fs.RawLocalFileSystem.getFileLinkStatusInternal(RawLocalFileSystem.java:1238)
    	at org.apache.hadoop.fs.RawLocalFileSystem.getFileStatus(RawLocalFileSystem.java:907)
    	at org.apache.hadoop.fs.FilterFileSystem.getFileStatus(FilterFileSystem.java:462)
    	at org.apache.spark.sql.execution.streaming.FileStreamSink$.hasMetadata(FileStreamSink.scala:56)
    	at org.apache.spark.sql.execution.datasources.DataSource.resolveRelation(DataSource.scala:381)
    	at org.apache.spark.sql.catalyst.analysis.ResolveDataSource.org$apache$spark$sql$catalyst$analysis$ResolveDataSource$$loadV1BatchSource(ResolveDataSource.scala:143)
    	at org.apache.spark.sql.catalyst.analysis.ResolveDataSource$$anonfun$apply$1.$anonfun$applyOrElse$2(ResolveDataSource.scala:61)
    	at scala.Option.getOrElse(Option.scala:201)
    	at org.apache.spark.sql.catalyst.analysis.ResolveDataSource$$anonfun$apply$1.applyOrElse(ResolveDataSource.scala:61)
    	at org.apache.spark.sql.catalyst.analysis.ResolveDataSource$$anonfun$apply$1.applyOrElse(ResolveDataSource.scala:45)
    	at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.$anonfun$resolveOperatorsUpWithPruning$3(AnalysisHelper.scala:139)
    	at org.apache.spark.sql.catalyst.trees.CurrentOrigin$.withOrigin(origin.scala:86)
    	at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.$anonfun$resolveOperatorsUpWithPruning$1(AnalysisHelper.scala:139)
    	at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper$.allowInvokingTransformsInAnalyzer(AnalysisHelper.scala:416)
    	at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.resolveOperatorsUpWithPruning(AnalysisHelper.scala:135)
    	at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.resolveOperatorsUpWithPruning$(AnalysisHelper.scala:131)
    	at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.resolveOperatorsUpWithPruning(LogicalPlan.scala:37)
    	at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.resolveOperatorsUp(AnalysisHelper.scala:112)
    	at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.resolveOperatorsUp$(AnalysisHelper.scala:111)
    	at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.resolveOperatorsUp(LogicalPlan.scala:37)
    	at org.apache.spark.sql.catalyst.analysis.ResolveDataSource.apply(ResolveDataSource.scala:45)
    	at org.apache.spark.sql.catalyst.analysis.ResolveDataSource.apply(ResolveDataSource.scala:43)
    	at org.apache.spark.sql.catalyst.rules.RuleExecutor.$anonfun$execute$2(RuleExecutor.scala:242)
    	at scala.collection.LinearSeqOps.foldLeft(LinearSeq.scala:183)
    	at scala.collection.LinearSeqOps.foldLeft$(LinearSeq.scala:179)
    	at scala.collection.immutable.List.foldLeft(List.scala:79)
    	at org.apache.spark.sql.catalyst.rules.RuleExecutor.$anonfun$execute$1(RuleExecutor.scala:239)
    	at org.apache.spark.sql.catalyst.rules.RuleExecutor.$anonfun$execute$1$adapted(RuleExecutor.scala:231)
    	at scala.collection.immutable.List.foreach(List.scala:334)
    	at org.apache.spark.sql.catalyst.rules.RuleExecutor.execute(RuleExecutor.scala:231)
    	at org.apache.spark.sql.catalyst.analysis.Analyzer.org$apache$spark$sql$catalyst$analysis$Analyzer$$executeSameContext(Analyzer.scala:340)
    	at org.apache.spark.sql.catalyst.analysis.Analyzer.$anonfun$execute$1(Analyzer.scala:336)
    	at org.apache.spark.sql.catalyst.analysis.AnalysisContext$.withNewAnalysisContext(Analyzer.scala:234)
    	at org.apache.spark.sql.catalyst.analysis.Analyzer.execute(Analyzer.scala:336)
    	at org.apache.spark.sql.catalyst.analysis.Analyzer.execute(Analyzer.scala:299)
    	at org.apache.spark.sql.catalyst.rules.RuleExecutor.$anonfun$executeAndTrack$1(RuleExecutor.scala:201)
    	at org.apache.spark.sql.catalyst.QueryPlanningTracker$.withTracker(QueryPlanningTracker.scala:89)
    	at org.apache.spark.sql.catalyst.rules.RuleExecutor.executeAndTrack(RuleExecutor.scala:201)
    	at org.apache.spark.sql.catalyst.analysis.resolver.HybridAnalyzer.resolveInFixedPoint(HybridAnalyzer.scala:190)
    	at org.apache.spark.sql.catalyst.analysis.resolver.HybridAnalyzer.$anonfun$apply$1(HybridAnalyzer.scala:76)
    	at org.apache.spark.sql.catalyst.analysis.resolver.HybridAnalyzer.withTrackedAnalyzerBridgeState(HybridAnalyzer.scala:111)
    	at org.apache.spark.sql.catalyst.analysis.resolver.HybridAnalyzer.apply(HybridAnalyzer.scala:71)
    	at org.apache.spark.sql.catalyst.analysis.Analyzer.$anonfun$executeAndCheck$1(Analyzer.scala:330)
    	at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper$.markInAnalyzer(AnalysisHelper.scala:423)
    	at org.apache.spark.sql.catalyst.analysis.Analyzer.executeAndCheck(Analyzer.scala:330)
    	at org.apache.spark.sql.execution.QueryExecution.$anonfun$lazyAnalyzed$2(QueryExecution.scala:110)
    	at org.apache.spark.sql.catalyst.QueryPlanningTracker.measurePhase(QueryPlanningTracker.scala:148)
    	at org.apache.spark.sql.execution.QueryExecution.$anonfun$executePhase$2(QueryExecution.scala:278)
    	at org.apache.spark.sql.execution.QueryExecution$.withInternalError(QueryExecution.scala:654)
    	at org.apache.spark.sql.execution.QueryExecution.$anonfun$executePhase$1(QueryExecution.scala:278)
    	at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:804)
    	at org.apache.spark.sql.execution.QueryExecution.executePhase(QueryExecution.scala:277)
    	at org.apache.spark.sql.execution.QueryExecution.$anonfun$lazyAnalyzed$1(QueryExecution.scala:110)
    	at scala.util.Try$.apply(Try.scala:217)
    	at org.apache.spark.util.Utils$.doTryWithCallerStacktrace(Utils.scala:1378)
    	at org.apache.spark.util.LazyTry.tryT$lzycompute(LazyTry.scala:46)
    	at org.apache.spark.util.LazyTry.tryT(LazyTry.scala:46)
    	at org.apache.spark.util.LazyTry.get(LazyTry.scala:58)
    	at org.apache.spark.sql.execution.QueryExecution.analyzed(QueryExecution.scala:121)
    	at org.apache.spark.sql.execution.QueryExecution.assertAnalyzed(QueryExecution.scala:80)
    	at org.apache.spark.sql.classic.Dataset$.$anonfun$ofRows$1(Dataset.scala:115)
    	at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:804)
    	at org.apache.spark.sql.classic.Dataset$.ofRows(Dataset.scala:113)
    	at org.apache.spark.sql.classic.DataFrameReader.load(DataFrameReader.scala:109)
    	at org.apache.spark.sql.classic.DataFrameReader.load(DataFrameReader.scala:58)
    	at org.apache.spark.sql.DataFrameReader.csv(DataFrameReader.scala:392)
    	at org.apache.spark.sql.classic.DataFrameReader.csv(DataFrameReader.scala:259)
    	at org.apache.spark.sql.classic.DataFrameReader.csv(DataFrameReader.scala:58)
    	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
    	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
    	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
    	at java.base/java.lang.reflect.Method.invoke(Method.java:569)
    	at py4j.reflection.MethodInvoker.invoke(MethodInvoker.java:244)
    	at py4j.reflection.ReflectionEngine.invoke(ReflectionEngine.java:374)
    	at py4j.Gateway.invoke(Gateway.java:282)
    	at py4j.commands.AbstractCommand.invokeMethod(AbstractCommand.java:132)
    	at py4j.commands.CallCommand.execute(CallCommand.java:79)
    	at py4j.ClientServerConnection.waitForCommands(ClientServerConnection.java:184)
    	at py4j.ClientServerConnection.run(ClientServerConnection.java:108)
    	at java.base/java.lang.Thread.run(Thread.java:840)



    ---------------------------------------------------------------------------

    AnalysisException                         Traceback (most recent call last)

    Cell In[5], line 3
          1 # Load data from CSV file
          2 print("Loading data...")
    ----> 3 df = spark.read.csv(
          4     "data/user_activity.csv",
          5     header=True,
          6     schema=schema
          7 )
          9 print("Data loaded successfully")
         10 print(f"Total records: {df.count()}")


    File ~/miniconda3/envs/de1-env/lib/python3.10/site-packages/pyspark/sql/readwriter.py:838, in DataFrameReader.csv(self, path, schema, sep, encoding, quote, escape, comment, header, inferSchema, ignoreLeadingWhiteSpace, ignoreTrailingWhiteSpace, nullValue, nanValue, positiveInf, negativeInf, dateFormat, timestampFormat, maxColumns, maxCharsPerColumn, maxMalformedLogPerPartition, mode, columnNameOfCorruptRecord, multiLine, charToEscapeQuoteEscaping, samplingRatio, enforceSchema, emptyValue, locale, lineSep, pathGlobFilter, recursiveFileLookup, modifiedBefore, modifiedAfter, unescapedQuoteHandling)
        836 if type(path) == list:
        837     assert self._spark._sc._jvm is not None
    --> 838     return self._df(self._jreader.csv(self._spark._sc._jvm.PythonUtils.toSeq(path)))
        840 if not is_remote_only():
        841     from pyspark.core.rdd import RDD  # noqa: F401


    File ~/miniconda3/envs/de1-env/lib/python3.10/site-packages/py4j/java_gateway.py:1362, in JavaMember.__call__(self, *args)
       1356 command = proto.CALL_COMMAND_NAME +\
       1357     self.command_header +\
       1358     args_command +\
       1359     proto.END_COMMAND_PART
       1361 answer = self.gateway_client.send_command(command)
    -> 1362 return_value = get_return_value(
       1363     answer, self.gateway_client, self.target_id, self.name)
       1365 for temp_arg in temp_args:
       1366     if hasattr(temp_arg, "_detach"):


    File ~/miniconda3/envs/de1-env/lib/python3.10/site-packages/pyspark/errors/exceptions/captured.py:288, in capture_sql_exception.<locals>.deco(*a, **kw)
        284 converted = convert_exception(e.java_exception)
        285 if not isinstance(converted, UnknownException):
        286     # Hide where the exception came from that shows a non-Pythonic
        287     # JVM exception message.
    --> 288     raise converted from None
        289 else:
        290     raise


    AnalysisException: [PATH_NOT_FOUND] Path does not exist: file:/home/sable/Documents/data engineering1/lab2-practice/data/user_activity.csv. SQLSTATE: 42K03



```python
# Display first few records
print("Sample data:")
df.show(10, truncate=False)
```


```python
# Display schema
print("Data schema:")
df.printSchema()
```


```python
# Basic statistics
print("Basic statistics:")
df.describe().show()
```

## Part 3: Data Quality Checks


```python
# Check for null values
print("Checking for null values...")
null_counts = df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns])
null_counts.show()
```


```python
# Check for duplicate records
print("Checking for duplicates...")
total_records = df.count()
distinct_records = df.distinct().count()
duplicate_count = total_records - distinct_records

print(f"Total records: {total_records}")
print(f"Distinct records: {distinct_records}")
print(f"Duplicate records: {duplicate_count}")

if duplicate_count == 0:
    print("No duplicates found")
else:
    print(f"Found {duplicate_count} duplicate records")
```

## Part 4: Data Transformations


```python
# Extract date and time components
print("Extracting date/time components...")
df_transformed = df.withColumn("date", to_date(col("timestamp"))) \
    .withColumn("hour", hour(col("timestamp"))) \
    .withColumn("day_of_week", dayofweek(col("timestamp"))) \
    .withColumn("month", month(col("timestamp")))

print("Date/time components extracted")
df_transformed.show(5)
```


```python
# Categorize duration into time buckets
print("Categorizing durations...")
df_transformed = df_transformed.withColumn(
    "duration_category",
    when(col("duration_seconds") < 60, "short")
    .when((col("duration_seconds") >= 60) & (col("duration_seconds") < 300), "medium")
    .otherwise("long")
)

print("Duration categories created")
df_transformed.groupBy("duration_category").count().show()
```

## Part 5: Data Analysis


```python
# User activity analysis
print("Analyzing user activity...")
user_stats = df_transformed.groupBy("user_id", "username").agg(
    count("*").alias("total_actions"),
    sum("duration_seconds").alias("total_duration"),
    avg("duration_seconds").alias("avg_duration"),
    countDistinct("action").alias("unique_actions"),
    countDistinct("device").alias("unique_devices")
).orderBy(col("total_actions").desc())

print("Top 10 most active users:")
user_stats.show(10)
```


```python
# Action type analysis
print("Analyzing action types...")
action_stats = df_transformed.groupBy("action").agg(
    count("*").alias("count"),
    avg("duration_seconds").alias("avg_duration")
).orderBy(col("count").desc())

print("Action statistics:")
action_stats.show()
```


```python
# Device usage analysis
print("Analyzing device usage...")
device_stats = df_transformed.groupBy("device").agg(
    count("*").alias("usage_count"),
    countDistinct("user_id").alias("unique_users")
).orderBy(col("usage_count").desc())

print("Device statistics:")
device_stats.show()
```


```python
# Location analysis
print("Analyzing locations...")
location_stats = df_transformed.groupBy("location").agg(
    count("*").alias("activity_count"),
    countDistinct("user_id").alias("unique_users")
).orderBy(col("activity_count").desc())

print("Top locations:")
location_stats.show(10)
```


```python
# Hourly activity pattern
print("Analyzing hourly patterns...")
hourly_stats = df_transformed.groupBy("hour").agg(
    count("*").alias("activity_count")
).orderBy("hour")

print("Hourly activity distribution:")
hourly_stats.show(24)
```

## Part 6: Advanced Analytics


```python
# User engagement score calculation
print("Calculating user engagement scores...")
engagement_df = df_transformed.groupBy("user_id", "username").agg(
    count("*").alias("activity_count"),
    sum("duration_seconds").alias("total_time"),
    countDistinct("date").alias("active_days")
)

# Calculate engagement score (normalized)
engagement_df = engagement_df.withColumn(
    "engagement_score",
    (col("activity_count") * 0.4 + col("total_time") / 60 * 0.3 + col("active_days") * 10 * 0.3)
).orderBy(col("engagement_score").desc())

print("Top engaged users:")
engagement_df.show(10)
```


```python
# Peak activity times
print("Identifying peak activity times...")
peak_times = df_transformed.groupBy("hour", "day_of_week").agg(
    count("*").alias("activity_count")
).orderBy(col("activity_count").desc())

print("Peak activity times:")
peak_times.show(10)
```

## Part 7: Data Visualization


```python
# Convert to Pandas for visualization
print("Preparing data for visualization...")
hourly_pd = hourly_stats.toPandas()
action_pd = action_stats.toPandas()
device_pd = device_stats.toPandas()

print("Data converted to Pandas")
```


```python
# Hourly activity plot
plt.figure(figsize=(12, 6))
plt.plot(hourly_pd['hour'], hourly_pd['activity_count'], marker='o', linewidth=2)
plt.title('User Activity by Hour of Day')
plt.xlabel('Hour')
plt.ylabel('Activity Count')
plt.grid(True, alpha=0.3)
plt.xticks(range(24))
plt.tight_layout()
plt.show()

print("Hourly activity plot created")
```


```python
# Action type distribution
plt.figure(figsize=(10, 6))
plt.bar(action_pd['action'], action_pd['count'])
plt.title('Activity Distribution by Action Type')
plt.xlabel('Action')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

print("Action distribution plot created")
```


```python
# Device usage pie chart
plt.figure(figsize=(8, 8))
plt.pie(device_pd['usage_count'], labels=device_pd['device'], autopct='%1.1f%%', startangle=90)
plt.title('Device Usage Distribution')
plt.axis('equal')
plt.tight_layout()
plt.show()

print("Device distribution plot created")
```

## Part 8: Data Export


```python
# Export processed data
print("Exporting processed data...")

# Export user statistics
user_stats.write.mode("overwrite").parquet("output/user_statistics")
print("User statistics exported")

# Export action statistics
action_stats.write.mode("overwrite").csv("output/action_statistics", header=True)
print("Action statistics exported")

# Export engagement scores
engagement_df.write.mode("overwrite").parquet("output/engagement_scores")
print("Engagement scores exported")
```

## Part 9: Summary and Conclusions


```python
# Generate summary report
print("=" * 50)
print("ASSIGNMENT 2 SUMMARY REPORT")
print("=" * 50)

total_users = df_transformed.select("user_id").distinct().count()
total_activities = df_transformed.count()
date_range = df_transformed.agg(
    min("date").alias("start_date"),
    max("date").alias("end_date")
).collect()[0]

print(f"\nData Overview:")
print(f"Total Users: {total_users}")
print(f"Total Activities: {total_activities}")
print(f"Date Range: {date_range['start_date']} to {date_range['end_date']}")

print(f"\nKey Metrics:")
print(f"Average activities per user: {total_activities / total_users:.2f}")

top_action = action_stats.first()
print(f"Most common action: {top_action['action']} ({top_action['count']} times)")

top_device = device_stats.first()
print(f"Most used device: {top_device['device']} ({top_device['usage_count']} times)")

print("\nProcessing completed successfully!")
print("=" * 50)
```


```python
# Stop Spark session
spark.stop()
print("Spark session stopped")
```
