# Assignment 1: Word Count with Apache Spark

> **Course:** Data Engineering 1  
> **Student:** Samba Diallo (@samba-diallo)  
> **Submission Date:** 2025-10-22  
> **Environment:** Python 3.10, PySpark 4.0.1, Ubuntu Linux

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Environment Setup](#environment-setup)
- [Implementation Details](#implementation-details)
- [Results](#results)
- [How to Run](#how-to-run)
- [Technologies Used](#technologies-used)
- [AI Assistance Disclosure](#ai-assistance-disclosure)
- [License](#license)

---

## 🎯 Overview

This project implements a **word frequency analysis** on product descriptions using **Apache Spark**. The assignment demonstrates proficiency in both **RDD-based** and **DataFrame-based** approaches to distributed data processing.

### Objectives

1. Load and process CSV data containing product descriptions
2. Clean and tokenize text data (lowercase, remove non-alphabetic characters)
3. Count word frequencies using both RDD and DataFrame APIs
4. Remove stopwords and re-analyze frequencies
5. Export top 10 most frequent words to CSV files

---

## 📁 Project Structure

```
data-engineering-assignment1/
│
├── notebook.ipynb                  # Main Jupyter notebook with all implementations
├── a1-brand.csv                    # Input dataset (product descriptions)
├── top10_words.csv/                # Output: Top 10 words (with stopwords)
│   └── part-00000-*.csv
├── top10_noStopWords.csv/          # Output: Top 10 words (without stopwords)
│   └── part-00000-*.csv
├── submission_info.json            # Environment and execution metadata
├── README.md                       # This file
└── .gitignore                      # Git ignore rules
```

---

## 🛠️ Environment Setup

### Prerequisites

- **Python:** 3.10+
- **Java:** OpenJDK 11 (required for Spark)
- **Apache Spark:** 4.0.1
- **Conda/Miniconda:** For environment management

### Installation Steps

```bash
# 1. Create and activate conda environment
conda create -n de1-env python=3.10 openjdk=11 -y
conda activate de1-env

# 2. Install PySpark and dependencies
conda install -c conda-forge pyspark
pip install jupyter pandas pytz

# 3. Set environment variables
export JAVA_HOME=$CONDA_PREFIX
export SPARK_HOME=$CONDA_PREFIX/lib/python3.10/site-packages/pyspark

# 4. Verify installation
python -c "import pyspark; print(pyspark.__version__)"
java -version
```

### System Information

- **Operating System:** Ubuntu Linux (ThinkPad X1 Yoga 3rd Gen)
- **Python Version:** 3.10.x
- **PySpark Version:** 4.0.1
- **Java Version:** OpenJDK 11
- **Timezone:** UTC
- **Working Directory:** `~/Documents/data engineering1/`

---

## 💻 Implementation Details

### 1. RDD-Based Approach

```python
# Load data as RDD
lines = sc.textFile("a1-brand.csv")

# Clean and tokenize
words = (
    lines
    .map(lambda s: re.sub('[^a-z]', ' ', s.lower()))
    .flatMap(lambda s: s.split())
    .filter(lambda w: len(w) >= 2)
)

# Count frequencies
word_counts = (
    words
    .map(lambda w: (w, 1))
    .reduceByKey(lambda a, b: a + b)
    .sortBy(lambda kv: (-kv[1], kv[0]))
)
```

### 2. DataFrame-Based Approach

```python
# Load data as DataFrame
df = spark.read.option("header", "true").csv("a1-brand.csv")

# Clean, tokenize, and count
word_counts = (
    df
    .select("description")
    .withColumn("clean", lower(col("description")))
    .withColumn("clean", regexp_replace(col("clean"), "[^a-z]", " "))
    .withColumn("words", split(col("clean"), "\\s+"))
    .withColumn("word", explode(col("words")))
    .filter(length(col("word")) >= 2)
    .groupBy("word")
    .agg(count("*").alias("count"))
    .orderBy(col("count").desc(), col("word"))
)
```

### 3. Stopwords Removal

```python
from pyspark.ml.feature import StopWordsRemover

remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
# Apply to remove common words like "the", "in", "for", etc.
```

### Key Processing Steps

1. **Text Cleaning:**
   - Convert to lowercase
   - Replace non-alphabetic characters with spaces
   - Split on whitespace

2. **Tokenization:**
   - Split text into individual words
   - Filter out tokens with length < 2

3. **Frequency Analysis:**
   - Count occurrences of each word
   - Sort by frequency (descending) and alphabetically

4. **Stopword Filtering:**
   - Remove common English words using Spark ML's `StopWordsRemover`

---

## 📊 Results

### Top 10 Words (With Stopwords)

The most frequent words include common stopwords like "the", "in", "for", etc.

### Top 10 Words (Without Stopwords)

After removing stopwords, more meaningful content words emerge, providing better insights into product descriptions.

**Note:** Full results are available in:
- `top10_words.csv/part-00000-*.csv`
- `top10_noStopWords.csv/part-00000-*.csv`

---

## 🚀 How to Run

### Option 1: Jupyter Notebook

```bash
# Navigate to project directory
cd ~/Documents/data\ engineering1/

# Activate environment
conda activate de1-env

# Launch Jupyter
jupyter notebook

# Open notebook.ipynb and run all cells
```

### Option 2: VS Code with Jupyter Extension

```bash
# Navigate to project directory
cd ~/Documents/data\ engineering1/

# Open in VS Code
code .

# Open notebook.ipynb
# Select kernel: de1-env
# Run all cells (Shift+Enter)
```

### Spark Configuration

```python
spark = (
    SparkSession.builder
    .appName("Assignment1")
    .master("local[*]")
    .config("spark.sql.shuffle.partitions", "10")  # Optimized for local
    .config("spark.driver.memory", "2g")
    .getOrCreate()
)
```

- **Spark UI:** http://localhost:4040 (when SparkSession is active)

---

## 🔧 Technologies Used

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.10+ | Programming language |
| **Apache Spark** | 4.0.1 | Distributed data processing |
| **PySpark** | 4.0.1 | Python API for Spark |
| **Jupyter** | Latest | Interactive development |
| **Pandas** | Latest | Data visualization |
| **OpenJDK** | 11 | Java runtime for Spark |
| **Conda** | Latest | Environment management |

### Key Libraries

- `pyspark.sql`: DataFrame API
- `pyspark.rdd`: RDD API
- `pyspark.ml.feature.StopWordsRemover`: Stopword removal
- `re`: Regular expressions for text cleaning

---

## 🤖 AI Assistance Disclosure

### Use of Artificial Intelligence

This project was completed **with assistance from AI tools** as part of the learning process. Specifically:

- **AI Tool Used:** Anthropic Claude Sonnet 4.5 (via GitHub Copilot Chat)
- **Nature of Assistance:**
  - Debugging PySpark configuration issues (JAVA_HOME, SPARK_HOME)
  - Understanding differences between RDD and DataFrame APIs
  - Code optimization suggestions (avoiding UDFs, shuffle partitions)
  - Documentation and README structure
  - Best practices for Spark performance tuning

### Learning Outcomes

While AI assisted with technical troubleshooting and explanations:

1. **Core implementations** (RDD word count, DataFrame transformations) were written based on understanding of Spark concepts
2. **Problem-solving approach** was guided by AI explanations but executed independently
3. **Analysis and comparisons** (RDD vs DataFrame) reflect personal understanding gained through the process

### Transparency Statement

I believe in **transparent use of AI as a learning tool**. The AI assistance helped accelerate debugging and clarify concepts, similar to how one would consult documentation, Stack Overflow, or a teaching assistant. The final work represents my understanding and application of Data Engineering principles with Apache Spark.

---

## 📈 Performance Considerations

### Optimizations Applied

1. **Native Functions over UDFs:**
   - Used `pyspark.sql.functions` (lower, regexp_replace, split)
   - Avoided Python UDFs for better performance

2. **Reduced Shuffle Partitions:**
   - Set `spark.sql.shuffle.partitions = 10` for local execution
   - Default (200) is excessive for single-machine runs

3. **Efficient Filtering:**
   - Filtered null values early in the pipeline
   - Removed empty strings before exploding arrays

4. **Single File Output:**
   - Used `.coalesce(1)` for CSV export
   - Avoids multiple part files in output

---

## 📝 Comparison: RDD vs DataFrame

### Are the Results Identical?

**In practice, results may differ** due to:

1. **CSV Parsing:**
   - **RDD:** Treats each line as raw text (includes all columns)
   - **DataFrame:** Parses CSV structure, extracts only "description" column

2. **Header Handling:**
   - **RDD:** May include header row in word count
   - **DataFrame:** Automatically skips header with `option("header", "true")`

3. **Processing Logic:**
   - Both apply same transformations (lowercase, regex, filtering)
   - DataFrame approach is more accurate for structured CSV data

**Conclusion:** DataFrame gives more correct results for analyzing the "description" column specifically.

---

## 🧹 Cleanup

```python
# Stop SparkSession
spark.stop()

# Remove temporary files (optional)
rm -rf spark-warehouse/ metastore_db/ derby.log
```

---

## 📄 License

This project is submitted as part of academic coursework for **Data Engineering 1**.

**Academic Integrity:** This work represents my own understanding and implementation, completed with AI assistance as disclosed above.

---

## 📧 Contact

**Student:** Samba Diallo  
**GitHub:** [@samba-diallo](https://github.com/samba-diallo)  
**Submission Date:** October 22, 2025 (UTC)

---

## 🙏 Acknowledgments

- **Course Instructors** for providing the assignment and dataset
- **Anthropic Claude** for technical assistance and explanations
- **Apache Spark Community** for excellent documentation
- **Stack Overflow** for troubleshooting references

---

**⭐ If this repository helped you, please consider giving it a star!**

