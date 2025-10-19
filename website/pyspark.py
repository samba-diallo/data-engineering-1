import findspark
findspark.init()
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("TestPySpark").getOrCreate()
print("Spark version:", spark.version)
spark.stop()