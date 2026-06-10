from pyspark.sql import SparkSession
from pyspark.sql.functions import expr

spark = SparkSession.builder.appName("Baseline").getOrCreate()

df = spark.range(10000)

result = (
    df.repartition(16)
      .withColumn("bucket", expr("id % 1000"))
      .groupBy("bucket")
      .count()
)

result.explain(True)
result.show()

spark.stop()