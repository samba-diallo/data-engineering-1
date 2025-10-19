import findspark
findspark.init()

from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder \
        .appName("VersionCheck") \
        .getOrCreate()
    
    print(f"Spark version: {spark.version}")
    spark.stop()

if __name__ == "__main__":
    main()