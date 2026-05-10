# DE1 — Lab 2: PostgreSQL → Star Schema ETL
> Author : Badr TAJINI - Data Engineering I - ESIEE 2025-2026
---
> Students : DIALLO Samba & DIOP Mouhamed
---


Execute all cells. Attach evidence and fill metrics.

## 0. Setup and schemas


```python
from pyspark.sql import SparkSession, functions as F, types as T
spark = SparkSession.builder.appName("de1-lab2").getOrCreate()
base = "data/"
# Explicit schemas
customers_schema = T.StructType([
    T.StructField("customer_id", T.IntegerType(), False),
    T.StructField("name", T.StringType(), True),
    T.StructField("email", T.StringType(), True),
    T.StructField("created_at", T.TimestampType(), True),
])
brands_schema = T.StructType([
    T.StructField("brand_id", T.IntegerType(), False),
    T.StructField("brand_name", T.StringType(), True),
])
categories_schema = T.StructType([
    T.StructField("category_id", T.IntegerType(), False),
    T.StructField("category_name", T.StringType(), True),
])
products_schema = T.StructType([
    T.StructField("product_id", T.IntegerType(), False),
    T.StructField("product_name", T.StringType(), True),
    T.StructField("brand_id", T.IntegerType(), True),
    T.StructField("category_id", T.IntegerType(), True),
    T.StructField("price", T.DoubleType(), True),
])
orders_schema = T.StructType([
    T.StructField("order_id", T.IntegerType(), False),
    T.StructField("customer_id", T.IntegerType(), True),
    T.StructField("order_date", T.TimestampType(), True),
])
order_items_schema = T.StructType([
    T.StructField("order_item_id", T.IntegerType(), False),
    T.StructField("order_id", T.IntegerType(), True),
    T.StructField("product_id", T.IntegerType(), True),
    T.StructField("quantity", T.IntegerType(), True),
    T.StructField("unit_price", T.DoubleType(), True),
])

```

## 1. Ingest operational tables (from CSV exports)


```python
customers = spark.read.schema(customers_schema).option("header","true").csv(base+"lab2_customers.csv")
brands = spark.read.schema(brands_schema).option("header","true").csv(base+"lab2_brands.csv")
categories = spark.read.schema(categories_schema).option("header","true").csv(base+"lab2_categories.csv")
products = spark.read.schema(products_schema).option("header","true").csv(base+"lab2_products.csv")
orders = spark.read.schema(orders_schema).option("header","true").csv(base+"lab2_orders.csv")
order_items = spark.read.schema(order_items_schema).option("header","true").csv(base+"lab2_order_items.csv")

for name, df in [("customers",customers),("brands",brands),("categories",categories),("products",products),("orders",orders),("order_items",order_items)]:
    print(name, df.count())

```

    customers 24
    brands 8
    categories 9
    products 60
    orders 220
    order_items 638
    products 60
    orders 220
    order_items 638


### Evidence: ingestion plan


```python
ingest = orders.join(order_items, "order_id").select("order_id").distinct()
ingest.explain("formatted")
from datetime import datetime as _dt
import pathlib
pathlib.Path("proof").mkdir(exist_ok=True)
with open("proof/plan_ingest.txt","w") as f:
    f.write(str(_dt.now())+"\n")
    f.write(ingest._jdf.queryExecution().executedPlan().toString())
print("Saved proof/plan_ingest.txt")

```

    == Physical Plan ==
    AdaptiveSparkPlan (11)
    +- HashAggregate (10)
       +- Exchange (9)
          +- HashAggregate (8)
             +- Project (7)
                +- BroadcastHashJoin Inner BuildLeft (6)
                   :- BroadcastExchange (3)
                   :  +- Filter (2)
                   :     +- Scan csv  (1)
                   +- Filter (5)
                      +- Scan csv  (4)
    
    
    (1) Scan csv 
    Output [1]: [order_id#196]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_orders.csv]
    PushedFilters: [IsNotNull(order_id)]
    ReadSchema: struct<order_id:int>
    
    (2) Filter
    Input [1]: [order_id#196]
    Condition : isnotnull(order_id#196)
    
    (3) BroadcastExchange
    Input [1]: [order_id#196]
    Arguments: HashedRelationBroadcastMode(List(cast(input[0, int, false] as bigint)),false), [plan_id=1812]
    
    (4) Scan csv 
    Output [1]: [order_id#200]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_order_items.csv]
    PushedFilters: [IsNotNull(order_id)]
    ReadSchema: struct<order_id:int>
    
    (5) Filter
    Input [1]: [order_id#200]
    Condition : isnotnull(order_id#200)
    
    (6) BroadcastHashJoin
    Left keys [1]: [order_id#196]
    Right keys [1]: [order_id#200]
    Join type: Inner
    Join condition: None
    
    (7) Project
    Output [1]: [order_id#196]
    Input [2]: [order_id#196, order_id#200]
    
    (8) HashAggregate
    Input [1]: [order_id#196]
    Keys [1]: [order_id#196]
    Functions: []
    Aggregate Attributes: []
    Results [1]: [order_id#196]
    
    (9) Exchange
    Input [1]: [order_id#196]
    Arguments: hashpartitioning(order_id#196, 200), ENSURE_REQUIREMENTS, [plan_id=1817]
    
    (10) HashAggregate
    Input [1]: [order_id#196]
    Keys [1]: [order_id#196]
    Functions: []
    Aggregate Attributes: []
    Results [1]: [order_id#196]
    
    (11) AdaptiveSparkPlan
    Output [1]: [order_id#196]
    Arguments: isFinalPlan=false
    
    
    Saved proof/plan_ingest.txt


## 2. Surrogate key function


```python
def sk(cols):
    # stable 64-bit positive surrogate key from natural keys
    return F.abs(F.xxhash64(*[F.col(c) for c in cols]))

```

## 3. Build dimensions


```python
dim_customer = customers.select(
    sk(["customer_id"]).alias("customer_sk"),
    "customer_id","name","email","created_at"
)

dim_brand = brands.select(
    sk(["brand_id"]).alias("brand_sk"),
    "brand_id","brand_name"
)

dim_category = categories.select(
    sk(["category_id"]).alias("category_sk"),
    "category_id","category_name"
)

dim_product = products.select(
    sk(["product_id"]).alias("product_sk"),
    "product_id","product_name",
    sk(["brand_id"]).alias("brand_sk"),
    sk(["category_id"]).alias("category_sk"),
    "price"
)

```

## 4. Build date dimension


```python
from pyspark.sql import Window as W
dates = orders.select(F.to_date("order_date").alias("date")).distinct()
dim_date = dates.select(
    sk(["date"]).alias("date_sk"),
    F.col("date"),
    F.year("date").alias("year"),
    F.month("date").alias("month"),
    F.dayofmonth("date").alias("day"),
    F.date_format("date","E").alias("dow")
)

```

## 5. Build fact_sales with broadcast joins where appropriate


```python
# Renomme la colonne product_id dans order_items AVANT le join
oi = order_items.withColumnRenamed("product_id", "oi_product_id").alias("oi")
p = products.alias("p")
o = orders.alias("o")
c = customers.alias("c")

df_fact = (
    oi
    .join(p, F.col("oi.oi_product_id") == F.col("p.product_id"))
    .join(o, "order_id")
    .join(c, "customer_id")
    .withColumn("date", F.to_date("order_date"))
)

df_fact = (
    df_fact
    .withColumn("date_sk", sk(["date"]))
    .withColumn("customer_sk", sk(["customer_id"]))
    .withColumn("product_sk", sk(["oi_product_id"]))  # plus d'ambiguïté ici
    .withColumn("quantity", F.col("quantity").cast("int"))
    .withColumn("unit_price", F.col("unit_price").cast("double"))
    .withColumn("subtotal", F.col("quantity") * F.col("unit_price"))
    .withColumn("year", F.year("date"))
    .withColumn("month", F.month("date"))
    .select("order_id", "date_sk", "customer_sk", "product_sk", "quantity", "unit_price", "subtotal", "year", "month")
)

df_fact.explain("formatted")
with open("proof/plan_fact_join.txt", "w") as f:
    from datetime import datetime as _dt
    f.write(str(_dt.now()) + "\n")
    f.write(df_fact._jdf.queryExecution().executedPlan().toString())
print("Saved proof/plan_fact_join.txt")
```

    == Physical Plan ==
    AdaptiveSparkPlan (20)
    +- Project (19)
       +- Project (18)
          +- BroadcastHashJoin Inner BuildRight (17)
             :- Project (13)
             :  +- BroadcastHashJoin Inner BuildRight (12)
             :     :- Project (8)
             :     :  +- BroadcastHashJoin Inner BuildRight (7)
             :     :     :- Project (3)
             :     :     :  +- Filter (2)
             :     :     :     +- Scan csv  (1)
             :     :     +- BroadcastExchange (6)
             :     :        +- Filter (5)
             :     :           +- Scan csv  (4)
             :     +- BroadcastExchange (11)
             :        +- Filter (10)
             :           +- Scan csv  (9)
             +- BroadcastExchange (16)
                +- Filter (15)
                   +- Scan csv  (14)
    
    
    (1) Scan csv 
    Output [4]: [order_id#200, product_id#201, quantity#202, unit_price#203]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_order_items.csv]
    PushedFilters: [IsNotNull(product_id), IsNotNull(order_id)]
    ReadSchema: struct<order_id:int,product_id:int,quantity:int,unit_price:double>
    
    (2) Filter
    Input [4]: [order_id#200, product_id#201, quantity#202, unit_price#203]
    Condition : (isnotnull(product_id#201) AND isnotnull(order_id#200))
    
    (3) Project
    Output [4]: [order_id#200, product_id#201 AS oi_product_id#267, quantity#202, unit_price#203]
    Input [4]: [order_id#200, product_id#201, quantity#202, unit_price#203]
    
    (4) Scan csv 
    Output [1]: [product_id#191]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_products.csv]
    PushedFilters: [IsNotNull(product_id)]
    ReadSchema: struct<product_id:int>
    
    (5) Filter
    Input [1]: [product_id#191]
    Condition : isnotnull(product_id#191)
    
    (6) BroadcastExchange
    Input [1]: [product_id#191]
    Arguments: HashedRelationBroadcastMode(List(cast(input[0, int, false] as bigint)),false), [plan_id=1886]
    
    (7) BroadcastHashJoin
    Left keys [1]: [oi_product_id#267]
    Right keys [1]: [product_id#191]
    Join type: Inner
    Join condition: None
    
    (8) Project
    Output [4]: [order_id#200, oi_product_id#267, quantity#202, unit_price#203]
    Input [5]: [order_id#200, oi_product_id#267, quantity#202, unit_price#203, product_id#191]
    
    (9) Scan csv 
    Output [3]: [order_id#196, customer_id#197, order_date#198]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_orders.csv]
    PushedFilters: [IsNotNull(order_id), IsNotNull(customer_id)]
    ReadSchema: struct<order_id:int,customer_id:int,order_date:timestamp>
    
    (10) Filter
    Input [3]: [order_id#196, customer_id#197, order_date#198]
    Condition : (isnotnull(order_id#196) AND isnotnull(customer_id#197))
    
    (11) BroadcastExchange
    Input [3]: [order_id#196, customer_id#197, order_date#198]
    Arguments: HashedRelationBroadcastMode(List(cast(input[0, int, false] as bigint)),false), [plan_id=1890]
    
    (12) BroadcastHashJoin
    Left keys [1]: [order_id#200]
    Right keys [1]: [order_id#196]
    Join type: Inner
    Join condition: None
    
    (13) Project
    Output [6]: [order_id#200, oi_product_id#267, quantity#202, unit_price#203, customer_id#197, order_date#198]
    Input [7]: [order_id#200, oi_product_id#267, quantity#202, unit_price#203, order_id#196, customer_id#197, order_date#198]
    
    (14) Scan csv 
    Output [1]: [customer_id#183]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_customers.csv]
    PushedFilters: [IsNotNull(customer_id)]
    ReadSchema: struct<customer_id:int>
    
    (15) Filter
    Input [1]: [customer_id#183]
    Condition : isnotnull(customer_id#183)
    
    (16) BroadcastExchange
    Input [1]: [customer_id#183]
    Arguments: HashedRelationBroadcastMode(List(cast(input[0, int, false] as bigint)),false), [plan_id=1894]
    
    (17) BroadcastHashJoin
    Left keys [1]: [customer_id#197]
    Right keys [1]: [customer_id#183]
    Join type: Inner
    Join condition: None
    
    (18) Project
    Output [6]: [customer_id#197, order_id#200, oi_product_id#267, quantity#202, unit_price#203, cast(order_date#198 as date) AS date#268]
    Input [7]: [order_id#200, oi_product_id#267, quantity#202, unit_price#203, customer_id#197, order_date#198, customer_id#183]
    
    (19) Project
    Output [9]: [order_id#200, abs(xxhash64(date#268, 42)) AS date_sk#269L, abs(xxhash64(customer_id#197, 42)) AS customer_sk#270L, abs(xxhash64(oi_product_id#267, 42)) AS product_sk#271L, quantity#202, unit_price#203, (cast(quantity#202 as double) * unit_price#203) AS subtotal#274, year(date#268) AS year#275, month(date#268) AS month#276]
    Input [6]: [customer_id#197, order_id#200, oi_product_id#267, quantity#202, unit_price#203, date#268]
    
    (20) AdaptiveSparkPlan
    Output [9]: [order_id#200, date_sk#269L, customer_sk#270L, product_sk#271L, quantity#202, unit_price#203, subtotal#274, year#275, month#276]
    Arguments: isFinalPlan=false
    
    
    Saved proof/plan_fact_join.txt


## 6. Write Parquet outputs (partitioned by year, month)


```python
base_out = "outputs/lab2"
(dim_customer.write.mode("overwrite").parquet(f"{base_out}/dim_customer"))
(dim_brand.write.mode("overwrite").parquet(f"{base_out}/dim_brand"))
(dim_category.write.mode("overwrite").parquet(f"{base_out}/dim_category"))
(dim_product.write.mode("overwrite").parquet(f"{base_out}/dim_product"))
(dim_date.write.mode("overwrite").parquet(f"{base_out}/dim_date"))
(df_fact.write.mode("overwrite").partitionBy("year","month").parquet(f"{base_out}/fact_sales"))
print("Parquet written under outputs/lab2/")

```

    Parquet written under outputs/lab2/


## 7. Plan comparison: projection and layout


```python
# Case A: join and then project
a = (orders.join(order_items, "order_id")
            .join(products, "product_id")
            .groupBy(F.to_date("order_date").alias("d"))
            .agg(F.sum(F.col("quantity")*F.col("price")).alias("gmv")))
a.explain("formatted")
_ = a.count()

# Case B: project early
b = (orders.select("order_id","order_date")
            .join(order_items.select("order_id","product_id","quantity"), "order_id")
            .join(products.select("product_id","price"), "product_id")
            .groupBy(F.to_date("order_date").alias("d"))
            .agg(F.sum(F.col("quantity")*F.col("price")).alias("gmv")))
b.explain("formatted")
_ = b.count()

print("Record Spark UI metrics for both runs in lab2_metrics_log.csv")

```

    == Physical Plan ==
    AdaptiveSparkPlan (16)
    +- HashAggregate (15)
       +- Exchange (14)
          +- HashAggregate (13)
             +- Project (12)
                +- BroadcastHashJoin Inner BuildRight (11)
                   :- Project (7)
                   :  +- BroadcastHashJoin Inner BuildLeft (6)
                   :     :- BroadcastExchange (3)
                   :     :  +- Filter (2)
                   :     :     +- Scan csv  (1)
                   :     +- Filter (5)
                   :        +- Scan csv  (4)
                   +- BroadcastExchange (10)
                      +- Filter (9)
                         +- Scan csv  (8)
    
    
    (1) Scan csv 
    Output [2]: [order_id#196, order_date#198]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_orders.csv]
    PushedFilters: [IsNotNull(order_id)]
    ReadSchema: struct<order_id:int,order_date:timestamp>
    
    (2) Filter
    Input [2]: [order_id#196, order_date#198]
    Condition : isnotnull(order_id#196)
    
    (3) BroadcastExchange
    Input [2]: [order_id#196, order_date#198]
    Arguments: HashedRelationBroadcastMode(List(cast(input[0, int, false] as bigint)),false), [plan_id=2342]
    
    (4) Scan csv 
    Output [3]: [order_id#200, product_id#201, quantity#202]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_order_items.csv]
    PushedFilters: [IsNotNull(order_id), IsNotNull(product_id)]
    ReadSchema: struct<order_id:int,product_id:int,quantity:int>
    
    (5) Filter
    Input [3]: [order_id#200, product_id#201, quantity#202]
    Condition : (isnotnull(order_id#200) AND isnotnull(product_id#201))
    
    (6) BroadcastHashJoin
    Left keys [1]: [order_id#196]
    Right keys [1]: [order_id#200]
    Join type: Inner
    Join condition: None
    
    (7) Project
    Output [3]: [order_date#198, product_id#201, quantity#202]
    Input [5]: [order_id#196, order_date#198, order_id#200, product_id#201, quantity#202]
    
    (8) Scan csv 
    Output [2]: [product_id#191, price#195]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_products.csv]
    PushedFilters: [IsNotNull(product_id)]
    ReadSchema: struct<product_id:int,price:double>
    
    (9) Filter
    Input [2]: [product_id#191, price#195]
    Condition : isnotnull(product_id#191)
    
    (10) BroadcastExchange
    Input [2]: [product_id#191, price#195]
    Arguments: HashedRelationBroadcastMode(List(cast(input[0, int, false] as bigint)),false), [plan_id=2346]
    
    (11) BroadcastHashJoin
    Left keys [1]: [product_id#201]
    Right keys [1]: [product_id#191]
    Join type: Inner
    Join condition: None
    
    (12) Project
    Output [3]: [quantity#202, price#195, cast(order_date#198 as date) AS _groupingexpression#314]
    Input [5]: [order_date#198, product_id#201, quantity#202, product_id#191, price#195]
    
    (13) HashAggregate
    Input [3]: [quantity#202, price#195, _groupingexpression#314]
    Keys [1]: [_groupingexpression#314]
    Functions [1]: [partial_sum((cast(quantity#202 as double) * price#195))]
    Aggregate Attributes [1]: [sum#315]
    Results [2]: [_groupingexpression#314, sum#316]
    
    (14) Exchange
    Input [2]: [_groupingexpression#314, sum#316]
    Arguments: hashpartitioning(_groupingexpression#314, 200), ENSURE_REQUIREMENTS, [plan_id=2351]
    
    (15) HashAggregate
    Input [2]: [_groupingexpression#314, sum#316]
    Keys [1]: [_groupingexpression#314]
    Functions [1]: [sum((cast(quantity#202 as double) * price#195))]
    Aggregate Attributes [1]: [sum((cast(quantity#202 as double) * price#195))#313]
    Results [2]: [_groupingexpression#314 AS d#300, sum((cast(quantity#202 as double) * price#195))#313 AS gmv#301]
    
    (16) AdaptiveSparkPlan
    Output [2]: [d#300, gmv#301]
    Arguments: isFinalPlan=false
    
    
    == Physical Plan ==
    AdaptiveSparkPlan (16)
    +- HashAggregate (15)
       +- Exchange (14)
          +- HashAggregate (13)
             +- Project (12)
                +- BroadcastHashJoin Inner BuildRight (11)
                   :- Project (7)
                   :  +- BroadcastHashJoin Inner BuildLeft (6)
                   :     :- BroadcastExchange (3)
                   :     :  +- Filter (2)
                   :     :     +- Scan csv  (1)
                   :     +- Filter (5)
                   :        +- Scan csv  (4)
                   +- BroadcastExchange (10)
                      +- Filter (9)
                         +- Scan csv  (8)
    
    
    (1) Scan csv 
    Output [2]: [order_id#196, order_date#198]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_orders.csv]
    PushedFilters: [IsNotNull(order_id)]
    ReadSchema: struct<order_id:int,order_date:timestamp>
    
    (2) Filter
    Input [2]: [order_id#196, order_date#198]
    Condition : isnotnull(order_id#196)
    
    (3) BroadcastExchange
    Input [2]: [order_id#196, order_date#198]
    Arguments: HashedRelationBroadcastMode(List(cast(input[0, int, false] as bigint)),false), [plan_id=2717]
    
    (4) Scan csv 
    Output [3]: [order_id#200, product_id#201, quantity#202]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_order_items.csv]
    PushedFilters: [IsNotNull(order_id), IsNotNull(product_id)]
    ReadSchema: struct<order_id:int,product_id:int,quantity:int>
    
    (5) Filter
    Input [3]: [order_id#200, product_id#201, quantity#202]
    Condition : (isnotnull(order_id#200) AND isnotnull(product_id#201))
    
    (6) BroadcastHashJoin
    Left keys [1]: [order_id#196]
    Right keys [1]: [order_id#200]
    Join type: Inner
    Join condition: None
    
    (7) Project
    Output [3]: [order_date#198, product_id#201, quantity#202]
    Input [5]: [order_id#196, order_date#198, order_id#200, product_id#201, quantity#202]
    
    (8) Scan csv 
    Output [2]: [product_id#191, price#195]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_products.csv]
    PushedFilters: [IsNotNull(product_id)]
    ReadSchema: struct<product_id:int,price:double>
    
    (9) Filter
    Input [2]: [product_id#191, price#195]
    Condition : isnotnull(product_id#191)
    
    (10) BroadcastExchange
    Input [2]: [product_id#191, price#195]
    Arguments: HashedRelationBroadcastMode(List(cast(input[0, int, false] as bigint)),false), [plan_id=2721]
    
    (11) BroadcastHashJoin
    Left keys [1]: [product_id#201]
    Right keys [1]: [product_id#191]
    Join type: Inner
    Join condition: None
    
    (12) Project
    Output [3]: [quantity#202, price#195, cast(order_date#198 as date) AS _groupingexpression#337]
    Input [5]: [order_date#198, product_id#201, quantity#202, product_id#191, price#195]
    
    (13) HashAggregate
    Input [3]: [quantity#202, price#195, _groupingexpression#337]
    Keys [1]: [_groupingexpression#337]
    Functions [1]: [partial_sum((cast(quantity#202 as double) * price#195))]
    Aggregate Attributes [1]: [sum#338]
    Results [2]: [_groupingexpression#337, sum#339]
    
    (14) Exchange
    Input [2]: [_groupingexpression#337, sum#339]
    Arguments: hashpartitioning(_groupingexpression#337, 200), ENSURE_REQUIREMENTS, [plan_id=2726]
    
    (15) HashAggregate
    Input [2]: [_groupingexpression#337, sum#339]
    Keys [1]: [_groupingexpression#337]
    Functions [1]: [sum((cast(quantity#202 as double) * price#195))]
    Aggregate Attributes [1]: [sum((cast(quantity#202 as double) * price#195))#336]
    Results [2]: [_groupingexpression#337 AS d#329, sum((cast(quantity#202 as double) * price#195))#336 AS gmv#330]
    
    (16) AdaptiveSparkPlan
    Output [2]: [d#329, gmv#330]
    Arguments: isFinalPlan=false
    
    
    == Physical Plan ==
    AdaptiveSparkPlan (16)
    +- HashAggregate (15)
       +- Exchange (14)
          +- HashAggregate (13)
             +- Project (12)
                +- BroadcastHashJoin Inner BuildRight (11)
                   :- Project (7)
                   :  +- BroadcastHashJoin Inner BuildLeft (6)
                   :     :- BroadcastExchange (3)
                   :     :  +- Filter (2)
                   :     :     +- Scan csv  (1)
                   :     +- Filter (5)
                   :        +- Scan csv  (4)
                   +- BroadcastExchange (10)
                      +- Filter (9)
                         +- Scan csv  (8)
    
    
    (1) Scan csv 
    Output [2]: [order_id#196, order_date#198]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_orders.csv]
    PushedFilters: [IsNotNull(order_id)]
    ReadSchema: struct<order_id:int,order_date:timestamp>
    
    (2) Filter
    Input [2]: [order_id#196, order_date#198]
    Condition : isnotnull(order_id#196)
    
    (3) BroadcastExchange
    Input [2]: [order_id#196, order_date#198]
    Arguments: HashedRelationBroadcastMode(List(cast(input[0, int, false] as bigint)),false), [plan_id=2717]
    
    (4) Scan csv 
    Output [3]: [order_id#200, product_id#201, quantity#202]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_order_items.csv]
    PushedFilters: [IsNotNull(order_id), IsNotNull(product_id)]
    ReadSchema: struct<order_id:int,product_id:int,quantity:int>
    
    (5) Filter
    Input [3]: [order_id#200, product_id#201, quantity#202]
    Condition : (isnotnull(order_id#200) AND isnotnull(product_id#201))
    
    (6) BroadcastHashJoin
    Left keys [1]: [order_id#196]
    Right keys [1]: [order_id#200]
    Join type: Inner
    Join condition: None
    
    (7) Project
    Output [3]: [order_date#198, product_id#201, quantity#202]
    Input [5]: [order_id#196, order_date#198, order_id#200, product_id#201, quantity#202]
    
    (8) Scan csv 
    Output [2]: [product_id#191, price#195]
    Batched: false
    Location: InMemoryFileIndex [file:/home/sable/Documents/data engineering1/lab2-practice/data/lab2_products.csv]
    PushedFilters: [IsNotNull(product_id)]
    ReadSchema: struct<product_id:int,price:double>
    
    (9) Filter
    Input [2]: [product_id#191, price#195]
    Condition : isnotnull(product_id#191)
    
    (10) BroadcastExchange
    Input [2]: [product_id#191, price#195]
    Arguments: HashedRelationBroadcastMode(List(cast(input[0, int, false] as bigint)),false), [plan_id=2721]
    
    (11) BroadcastHashJoin
    Left keys [1]: [product_id#201]
    Right keys [1]: [product_id#191]
    Join type: Inner
    Join condition: None
    
    (12) Project
    Output [3]: [quantity#202, price#195, cast(order_date#198 as date) AS _groupingexpression#337]
    Input [5]: [order_date#198, product_id#201, quantity#202, product_id#191, price#195]
    
    (13) HashAggregate
    Input [3]: [quantity#202, price#195, _groupingexpression#337]
    Keys [1]: [_groupingexpression#337]
    Functions [1]: [partial_sum((cast(quantity#202 as double) * price#195))]
    Aggregate Attributes [1]: [sum#338]
    Results [2]: [_groupingexpression#337, sum#339]
    
    (14) Exchange
    Input [2]: [_groupingexpression#337, sum#339]
    Arguments: hashpartitioning(_groupingexpression#337, 200), ENSURE_REQUIREMENTS, [plan_id=2726]
    
    (15) HashAggregate
    Input [2]: [_groupingexpression#337, sum#339]
    Keys [1]: [_groupingexpression#337]
    Functions [1]: [sum((cast(quantity#202 as double) * price#195))]
    Aggregate Attributes [1]: [sum((cast(quantity#202 as double) * price#195))#336]
    Results [2]: [_groupingexpression#337 AS d#329, sum((cast(quantity#202 as double) * price#195))#336 AS gmv#330]
    
    (16) AdaptiveSparkPlan
    Output [2]: [d#329, gmv#330]
    Arguments: isFinalPlan=false
    
    
    Record Spark UI metrics for both runs in lab2_metrics_log.csv
    Record Spark UI metrics for both runs in lab2_metrics_log.csv


## 8. Cleanup


```python
spark.stop()
print("Spark session stopped.")

```

    Spark session stopped.

