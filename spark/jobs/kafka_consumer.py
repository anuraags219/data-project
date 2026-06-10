from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = (
    SparkSession.builder
    .appName("KafkaCDCConsumer")
    .getOrCreate()
)

raw_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "inventory.public.customers")
    .option("startingOffsets", "earliest")
    .load()
)

cdc_schema = StructType([
    StructField(
        "payload",
        StructType([
            StructField(
                "before",
                StructType([
                    StructField("id", IntegerType()),
                    StructField("name", StringType()),
                    StructField("age", IntegerType()),
                    StructField("updated_at", LongType())
                ])
            ),
            StructField(
                "after",
                StructType([
                    StructField("id", IntegerType()),
                    StructField("name", StringType()),
                    StructField("age", IntegerType()),
                    StructField("updated_at", LongType())
                ])
            ),
            StructField("op", StringType()),
            StructField("ts_ms", LongType())
        ])
    )
])

parsed = (
    raw_df
    .selectExpr("CAST(value AS STRING) AS json")
    .select(
        from_json(
            col("json"),
            cdc_schema
        ).alias("data")
    )
)

customers = (
    parsed
    .select(
        when(
            col("data.payload.op") == "d",
            col("data.payload.before.id")
        ).otherwise(
            col("data.payload.after.id")
        ).alias("id"),

        when(
            col("data.payload.op") == "d",
            col("data.payload.before.name")
        ).otherwise(
            col("data.payload.after.name")
        ).alias("name"),

        when(
            col("data.payload.op") == "d",
            col("data.payload.before.age")
        ).otherwise(
            col("data.payload.after.age")
        ).alias("age"),

        col("data.payload.op").alias("operation"),

        col("data.payload.ts_ms").alias("event_ts")
    )
)

query = (
    customers.writeStream
    .format("parquet")
    .option(
        "path",
        "/opt/spark/output/customers"
    )
    .option(
        "checkpointLocation",
        "/opt/spark/checkpoints/customers"
    )
    .outputMode("append")
    .start()
)

query.awaitTermination()