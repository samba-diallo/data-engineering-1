# ESIEE Paris — Data Engineering I — Assignment 1
> Author : Badr TAJINI

**Academic year:** 2025–2026  
**Program:** Data & Applications - Engineering - (FD)   
**Course:** Data Engineering I  

---

In this assignment, you'll make sure that you've correctly set up your local Spark environment.
You'll then complete a classic "Word Count" task on the `description` column of the `a1-brand.csv` file.

You can think of "Word Count" as the "Hello World!" of Hadoop, Spark, etc.
The task is simple: We want to count the total number of times each word occurs (in a potentially large collection of text).
Typically, we want to sort by the counts in descending order so we can examine the most frequently occurring words.

## Learning goals
- Confirm local Spark environment in JupyterLab.
- Implement word-count using **RDD** and **DataFrame** APIs.
- Produce top-10 tokens with and without stopwords.
- Record brief performance notes and environment details.


## 1. Setup

The following code snippet should "just work" to initialize Spark.
If it doesn't, consult the **helper and Lab 0 with installation and setup guide**.


```python
#import findspark, os
#os.environ["SPARK_HOME"] = "/path/to/spark-4.0.0-bin-hadoop3"
#findspark.init()
```


```python
import os
import sys
from pyspark.sql import SparkSession
import pyspark
```


```python
# Configurer JAVA_HOME
os.environ['JAVA_HOME'] = '/home/sable/miniconda3/envs/de1-env'

# Configurer SPARK_HOME correctement
os.environ['SPARK_HOME'] = '/home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages/pyspark'

# Vérifier les configurations
print(f"JAVA_HOME: {os.environ['JAVA_HOME']}")
print(f"SPARK_HOME: {os.environ['SPARK_HOME']}")
```

    JAVA_HOME: /home/sable/miniconda3/envs/de1-env
    SPARK_HOME: /home/sable/miniconda3/envs/de1-env/lib/python3.10/site-packages/pyspark


Edit the path below to point to your local copy of `a1-brand.csv`. 

Examples:
- macOS/Linux: `/Users/yourname/data/a1-brand.csv`
- Windows: `C:\\Users\\yourname\\data\\a1-brand.csv`


```python
# TODO: Set the path to a1-brand.csv
DATA_PATH = "/path/to/a1-brand.csv"
```

Import PySpark:


```python
import sys, re
from pyspark.sql import SparkSession, functions as F, types as T
from pyspark.sql.functions import col
```

Set up to measure wall time and memory. (Don't worry about the details, just run the cell)



```python
from IPython.core.magic import register_cell_magic
import time, os, platform
import psutil, resource

def _rss_bytes():
    return psutil.Process(os.getpid()).memory_info().rss

def _ru_maxrss_bytes():
    # ru_maxrss: bytes on macOS; kilobytes on Linux
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if platform.system() == "Darwin":
        return int(ru)  # bytes
    else:
        return int(ru) * 1024  # KB -> bytes

@register_cell_magic
def timemem(line, cell):
    """
    Measure wall time and memory around the execution of this cell.
    Usage:
        %%timemem
        <your code>
    """
    ip = get_ipython()
    rss_before = _rss_bytes()
    peak_before = _ru_maxrss_bytes()
    t0 = time.perf_counter()

    # Execute the cell body
    result = ip.run_cell(cell)

    t1 = time.perf_counter()
    rss_after = _rss_bytes()
    peak_after = _ru_maxrss_bytes()

    wall = t1 - t0
    rss_delta_mb = (rss_after - rss_before) / (1024*1024)
    peak_delta_mb = (peak_after - peak_before) / (1024*1024)

    print("======================================")
    print(f"Wall time: {wall:.3f} s")
    print(f"RSS Δ: {rss_delta_mb:+.2f} MB")
    print(f"Peak memory Δ: {peak_delta_mb:+.2f} MB (OS-dependent)")
    print("======================================")

    return result
```

Start a local Spark session (i.e., a `SparkContext`):


```python
# Créer la SparkSession
spark = (
    SparkSession.builder
    .appName("Assignment1")
    .master("local[*]")
    .config("spark.ui.showConsoleProgress", "true")
    .config("spark.driver.memory", "2g")
    .getOrCreate()
)

print("SparkSession créée avec succès!")
spark
```

    WARNING: Using incubator modules: jdk.incubator.vector
    Using Spark's default log4j profile: org/apache/spark/log4j2-defaults.properties
    25/10/22 00:59:51 WARN Utils: Your hostname, sable-ThinkPad-X1-Yoga-3rd, resolves to a loopback address: 127.0.1.1; using 10.192.33.105 instead (on interface wlp2s0)
    25/10/22 00:59:51 WARN Utils: Set SPARK_LOCAL_IP if you need to bind to another address
    Using Spark's default log4j profile: org/apache/spark/log4j2-defaults.properties
    Setting default log level to "WARN".
    To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
    25/10/22 00:59:54 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable


    SparkSession créée avec succès!






    <div>
        <p><b>SparkSession - in-memory</b></p>

<div>
    <p><b>SparkContext</b></p>

    <p><a href="http://10.192.33.105:4040">Spark UI</a></p>

    <dl>
      <dt>Version</dt>
        <dd><code>v4.0.1</code></dd>
      <dt>Master</dt>
        <dd><code>local[*]</code></dd>
      <dt>AppName</dt>
        <dd><code>Assignment1</code></dd>
    </dl>
</div>

    </div>





```python

```

If you've gotten to here, congrats! Everything seems to have been set up and initialized properly!

## 2. Word Count with RDDs

First, let's read the `a1-brand.csv` file into an RDD.

**write some code here**

**Hints:**

- You'll want to fetch the `SparkContext` from the `SparkSession`.
- There's a method of the `SparkContext` for reading in text files.
- This simple exercise should only take two lines. If you find yourself writing more code, you're doing something wrong...


```python
%%timemem

# TODO: Write your code below, but do not remove any lines already in this cell.

sc = spark.sparkContext
lines = sc.textFile("a1-brand.csv")

# By the time we get to here, "lines" should refer to an RDD with the brand file loaded.
# Let's count the lines.


lines.count()
```

                                                                                    




    7262



    ======================================
    Wall time: 3.554 s
    RSS Δ: +0.12 MB
    Peak memory Δ: +0.12 MB (OS-dependent)
    ======================================





    <ExecutionResult object at 78dd39109c30, execution_count=None error_before_exec=None error_in_exec=None info=<ExecutionInfo object at 78dd39109a80, raw_cell="
    # TODO: Write your code below, but do not remove .." store_history=False silent=False shell_futures=True cell_id=None> result=7262>



Next, clean and tokenize text, and then find the 10 most common words.

**write some code here**

**Required Steps:**

- Lowercase all text.
- Replace non-letter characters (`[^a-z]`) with spaces.
- Split on whitespace into tokens.
- Remove tokens with length < 2.

**Hints:**

- You _must_ use `flatMap` and other RDD operations in this step. If you're not, you're doing something wrong...
- At the end, you'll need to `collect` the output.



```python
%%timemem

# TODO: Write your code below, but do not remove any lines already in this cell.
import re

# Clean and tokenize:
# - lowercase
# - replace non-letters with spaces
# - split on whitespace
# - drop tokens of length < 2
words = (
    lines
    .map(lambda s: re.sub('[^a-z]', ' ', s.lower()))
    .flatMap(lambda s: s.split())
    .filter(lambda w: len(w) >= 2)
)

# Count and get the 10 most frequent words
word_counts = (
    words
    .map(lambda w: (w, 1))
    .reduceByKey(lambda a, b: a + b)
    .sortBy(lambda kv: (-kv[1], kv[0]))
    .collect()  # Collecter TOUT en une liste Python
)

# By the time we get to here "word_counts" already has the collected output, sorted by frequency in descending order.
# So we just print out the top-10.

for word, count in word_counts[:10]:
    print(f"{word}: {count}")
```

                                                                                    

    and: 16150
    the: 9612
    in: 7958
    is: 7814
    for: 6789
    brand: 6476
    its: 4241
    to: 4026
    of: 3382
    with: 3099
    ======================================
    Wall time: 2.717 s
    RSS Δ: +0.38 MB
    Peak memory Δ: +0.38 MB (OS-dependent)
    ======================================





    <ExecutionResult object at 78dd392f0370, execution_count=None error_before_exec=None error_in_exec=None info=<ExecutionInfo object at 78dd392f0dc0, raw_cell="
    # TODO: Write your code below, but do not remove .." store_history=False silent=False shell_futures=True cell_id=None> result=None>



## 3. Word Count with DataFrames

### 3.1 Again, Just with DataFrames

Now, we're going to do the same thing, but with DataFrames instead of RDDs.

What's the difference, you ask? We'll cover it in lecture soon enough!

**write some code here**

**Hints:**

- Here, you'll use the `SparkSession`.
- Loading a DataFrame is a single method call. If you find yourself writing more code, you're doing something wrong...
- When loading the CSV file, be aware of your escape character; use something like `.option("escape", ...)`.


```python
%%timemem

# TODO: Write your code below, but do not remove any lines already in this cell.

# TODO: Write your code below, but do not remove any lines already in this cell.

# Charger le fichier CSV dans un DataFrame
df = (spark
      .read
      .option("header", "true")           # Le fichier a une ligne d'en-tête
      .option("escape", "\"")             # Utiliser guillemet double comme caractère d'échappement
      .option("inferSchema", "true")      # Inférer automatiquement les types de colonnes
      .csv("a1-brand.csv")
     )

# By the time we get to here, the file should have already been loaded into a DataFrame.
# Here, we just inspect it.

print("Rows:", df.count())
df.printSchema()
df.select("description").show(5, truncate=80)
```

    Rows: 7261
    root
     |-- brand: string (nullable = true)
     |-- description: string (nullable = true)
    
    +--------------------------------------------------------------------------------+
    |                                                                     description|
    +--------------------------------------------------------------------------------+
    |a-case is a brand specializing in protective accessories for electronic devic...|
    |A-Derma is a French dermatological skincare brand specializing in products fo...|
    | a patented ingredient derived from oat plants cultivated under organic farmi...|
    |                                                                       cleansers|
    |           A-Derma emphasizes clinical efficacy and hypoallergenic formulations.|
    +--------------------------------------------------------------------------------+
    only showing top 5 rows
    ======================================
    Wall time: 0.689 s
    RSS Δ: +0.00 MB
    Peak memory Δ: +0.00 MB (OS-dependent)
    ======================================





    <ExecutionResult object at 78dd392f0e50, execution_count=None error_before_exec=None error_in_exec=None info=<ExecutionInfo object at 78dd392f2950, raw_cell="
    # TODO: Write your code below, but do not remove .." store_history=False silent=False shell_futures=True cell_id=None> result=None>



Next, clean and tokenize text, and then find the 10 most common (i.e., frequently occurring) words.
This attempts the same processing as word count with RDDs above, except here you're using a DataFrame.

**write some code here**

**Required Steps:** (Exactly the same as above.)

- Lowercase all text.
- Replace non-letter characters (`[^a-z]`) with spaces.
- Split on whitespace into tokens.
- Remove tokens with length < 2.

**Hints:**

- You _must_ use `explode` and other Spark DataFrame operations in this exercise.
- This exercise shouldn't take more than (roughly) a dozen lines. If you find yourself writing more code, you're doing something wrong...


```python
%%timemem

# TODO: Write your code below, but do not remove any lines already in this cell.
# TODO: Write your code below, but do not remove any lines already in this cell.

from pyspark.sql.functions import col, lower, regexp_replace, split, explode, length, count

# Clean, tokenize, and count words using DataFrame operations
word_counts = (
    df
    .select("description")                                      # Sélectionner la colonne description
    .withColumn("clean", lower(col("description")))            # Convertir en minuscules
    .withColumn("clean", regexp_replace(col("clean"), "[^a-z]", " "))  # Remplacer non-lettres par espaces
    .withColumn("words", split(col("clean"), "\\s+"))          # Séparer en tokens sur les espaces
    .withColumn("word", explode(col("words")))                 # Exploser le tableau en lignes individuelles
    .filter(length(col("word")) >= 2)                          # Filtrer tokens de longueur >= 2
    .groupBy("word")                                           # Grouper par mot
    .agg(count("*").alias("count"))                            # Compter les occurrences
    .orderBy(col("count").desc(), col("word"))                 # Trier par fréquence desc, puis alphabétiquement
)


# By the time we get to here "word_counts" is a DataFrame that already has the word counts sorted in descending order.
# So we just print out the top-10.

top10 = word_counts.limit(10)
top10.show()
```

    [Stage 30:>                                                         (0 + 1) / 1]

    +-----+-----+
    | word|count|
    +-----+-----+
    |  and|13094|
    |  the| 6895|
    |   is| 6419|
    |   in| 6351|
    |  for| 5530|
    |brand| 5196|
    |  its| 3304|
    |   to| 3155|
    |   of| 2692|
    |known| 2509|
    +-----+-----+
    
    ======================================
    Wall time: 1.172 s
    RSS Δ: +0.00 MB
    Peak memory Δ: +0.00 MB (OS-dependent)
    ======================================


                                                                                    




    <ExecutionResult object at 78dd397a76d0, execution_count=None error_before_exec=None error_in_exec=None info=<ExecutionInfo object at 78dd2bfb9900, raw_cell="
    # TODO: Write your code below, but do not remove .." store_history=False silent=False shell_futures=True cell_id=None> result=None>



**Questions to reflect on**:

- What is conceptually different about how Spark executes `flatMap` and `explode`?
- What are the advantages or disadvantages of using each of them? 
- Are there cases where you may prefer one over the other?

(No need to write answers in the assignment submission. Just think about it...)

**Question to actually answer**:

Does the RDD approach and the DataFrame approach give the same answers? Explain why or why not.

**Write your answer to the above question!**

## Answer:

**Yes and No - It depends on the RDD implementation.**

### Why they may differ:

**1. CSV Parsing (MAIN DIFFERENCE):**
- **RDD**: Reads each line as raw text → processes EVERYTHING (IDs, brand names, descriptions)
- **DataFrame**: Parses CSV correctly → processes ONLY the "description" column

**2. Header handling:**
- **RDD**: Likely includes "id,brand,description" in the word count
- **DataFrame**: Automatically ignores the header with `option("header", "true")`

**3. Same cleaning logic:**
Both apply the same transformations (lowercase, regex, filtering), so **if the RDD also processed only the description column**, the results would be identical.

### Conclusion:

**In practice, the results are probably DIFFERENT** because:
- RDD treats all columns (unstructured)
- DataFrame treats only "description" (structured)

**The DataFrame gives more accurate results** for analyzing specifically the textual content of the "description" column. 

### 3.1 Removing Stopwords

You've probably noticed that many of the most frequently occurring words are not providing us any indication about the content because they are words like "in", "the", "for", etc.
These are called stopwords.

Let's remove stopwords and count again!

**write some code here**

**Hints:**

- Filter out all stopwords from the DataFrame before counting.
- Use `StopWordsRemover` from `pyspark.ml.feature`.


```python
# TODO: Write your code below, but do not remove any lines already in this cell.

import numpy
from pyspark.ml.feature import StopWordsRemover
from pyspark.sql.functions import col, lower, regexp_replace, split, explode, length, count, size, array_remove

# Créer un StopWordsRemover
remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")

# Clean, tokenize, remove stopwords, and count words
word_counts_noStopWords = (
    df
    .select("description")                                      # Sélectionner la colonne description
    .filter(col("description").isNotNull())                    # Supprimer les lignes null
    .withColumn("clean", lower(col("description")))            # Convertir en minuscules
    .withColumn("clean", regexp_replace(col("clean"), "[^a-z]", " "))  # Remplacer non-lettres par espaces
    .withColumn("words", split(col("clean"), "\\s+"))          # Séparer en tokens
    .withColumn("words", array_remove(col("words"), ""))       # Supprimer les strings vides du tableau
    .filter(size(col("words")) > 0)                            # Garder seulement les lignes avec des mots
    .transform(lambda df: remover.transform(df))               # Supprimer les stopwords
    .withColumn("word", explode(col("filtered_words")))        # Exploser le tableau filtré
    .filter(length(col("word")) >= 2)                          # Filtrer tokens de longueur >= 2
    .groupBy("word")                                           # Grouper par mot
    .agg(count("*").alias("count"))                            # Compter les occurrences
    .orderBy(col("count").desc(), col("word"))                 # Trier par fréquence desc
)



# By the time we get to here "word_counts_noStopWords" is a DataFrame that already has the word counts sorted in descending order.
# So we just print out the top-10.

top10_noStopWords = word_counts_noStopWords.limit(10)
top10_noStopWords.show()
```

    [Stage 35:>                                                         (0 + 1) / 1]

    +------------+-----+
    |        word|count|
    +------------+-----+
    |       brand| 5196|
    |       known| 2509|
    |    products| 2459|
    |   primarily| 2100|
    |      market| 1873|
    |       range| 1688|
    |  recognized| 1482|
    |   including| 1452|
    |specializing| 1390|
    |       often| 1247|
    +------------+-----+
    


                                                                                    

### 3.2 Saving Results to CSV

+ Save the results of the top-10 most frequently occurring words _with stopwords_, as a CSV file, to `top10_words.csv`.
+ Save the results of the top-10 frequently occurring words _discarding stopwords_, as a CSV file, to `top10_noStopWords.csv`.

**write some code here**


```python

# TODO: Write your code below, but do not remove any lines already in this cell.

# Sauvegarder le top 10 avec stopwords
top10 = word_counts.limit(10)
top10.coalesce(1).write.mode("overwrite").option("header", "true").csv("top10_words.csv")

# Sauvegarder le top 10 sans stopwords
top10_noStopWords = word_counts_noStopWords.limit(10)
top10_noStopWords.coalesce(1).write.mode("overwrite").option("header", "true").csv("top10_noStopWords.csv")


```

                                                                                    


```python
# Lire et afficher top10_words.csv
print("=== Top 10 avec stopwords ===")
df_top10 = spark.read.option("header", "true").csv("top10_words.csv")
df_top10.show()

# Lire et afficher top10_noStopWords.csv
print("\n=== Top 10 sans stopwords ===")
df_top10_noStopWords = spark.read.option("header", "true").csv("top10_noStopWords.csv")
df_top10_noStopWords.show()
```

    === Top 10 avec stopwords ===
    +-----+-----+
    | word|count|
    +-----+-----+
    |  and|13094|
    |  the| 6895|
    |   is| 6419|
    |   in| 6351|
    |  for| 5530|
    |brand| 5196|
    |  its| 3304|
    |   to| 3155|
    |   of| 2692|
    |known| 2509|
    +-----+-----+
    
    
    === Top 10 sans stopwords ===
    +------------+-----+
    |        word|count|
    +------------+-----+
    |       brand| 5196|
    |       known| 2509|
    |    products| 2459|
    |   primarily| 2100|
    |      market| 1873|
    |       range| 1688|
    |  recognized| 1482|
    |   including| 1452|
    |specializing| 1390|
    |       often| 1247|
    +------------+-----+
    


## 4. Assignment Submission and Cleanup

Details about the Submission of this assignment are outlined in the helper. Please read carefully the instructions.

Finally, clean up!


```python
# Dans une cellule de votre notebook, vérifiez que tous les fichiers sont créés
import os

print("✓ Vérification des fichiers de sortie...")
print(f"top10_words.csv existe: {os.path.exists('top10_words.csv')}")
print(f"top10_noStopWords.csv existe: {os.path.exists('top10_noStopWords.csv')}")

# Lister les fichiers dans ces dossiers
print("\nContenu de top10_words.csv/:")
os.system("ls -lh top10_words.csv/")

print("\nContenu de top10_noStopWords.csv/:")
os.system("ls -lh top10_noStopWords.csv/")
```

    ✓ Vérification des fichiers de sortie...
    top10_words.csv existe: True
    top10_noStopWords.csv existe: True
    
    Contenu de top10_words.csv/:
    total 4,0K
    -rw-r--r-- 1 sable sable 102 oct.  22 02:00 part-00000-dee28def-7b7d-4df2-9f83-c1c5ded32998-c000.csv
    -rw-r--r-- 1 sable sable   0 oct.  22 01:57 _SUCCESS
    
    Contenu de top10_noStopWords.csv/:
    total 4,0K
    -rw-r--r-- 1 sable sable 145 oct.  22 01:57 part-00000-2608e003-ab9e-402b-92a6-b97acdf255c4-c000.csv
    -rw-r--r-- 1 sable sable   0 oct.  22 01:57 _SUCCESS





    0




```python
spark.stop()
print("✓ SparkSession arrêtée avec succès!")
```

    ✓ SparkSession arrêtée avec succès!


## Performance notes

- Prefer DataFrame built-ins; avoid Python UDFs for tokenization where possible.
- Keep shuffle partitions modest on local runs.
- Cache wisely and avoid unnecessary actions.


## Reproducibility checklist

- Record Python/Java/Spark versions.
- Fix timezone to UTC.
- Provide exact run command and paths to input/output files.

