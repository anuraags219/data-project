from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder \
    .appName("GlutenPlanTest") \
    .getOrCreate()

df = spark.range(1000000)

result = (
    df
    .withColumn("bucket", col("id") % 100)
    .groupBy("bucket")
    .count()
)

result.explain(True)

result.show()

print(result._jdf.queryExecution().executedPlan().toString())

spark.stop()