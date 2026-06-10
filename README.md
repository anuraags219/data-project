# Local Data Platform

End-to-end CDC pipeline using:

* PostgreSQL
* Debezium
* Kafka
* Spark Structured Streaming
* Spark History Server

## Architecture

```text
postgres-updater
        ↓
postgres (CDC enabled)
        ↓
debezium
        ↓
kafka
        ↓
spark structured streaming
        ↓
parquet / console
```

## Project Structure

```text
.
├── debezium
│   ├── connect.env
│   └── postgres-connector.json
├── docker
│   └── compose
│       ├── debezium.yaml
│       ├── docker-compose.yaml
│       ├── kafka.yaml
│       ├── postgres-updater.yaml
│       ├── postgres.yaml
│       └── spark.yaml
├── gluten
│   └── gluten-velox-bundle-spark3.5_2.12-linux_amd64-1.6.0.jar
├── kafka
│   └── kafka.env
├── postgres
│   ├── init.sql
│   ├── postgres.env
│   └── updater
│       ├── Dockerfile
│       ├── requirements.txt
│       └── update_customers.py
├── README.md
├── scripts
│   └── run.sh
└── spark
    ├── checkpoints
    │   └── customers
    ├── configs
    │   ├── gluten.conf
    │   ├── kafka.conf
    │   └── spark-default.conf
    ├── Dockerfile
    ├── jobs
    │   ├── gluten_test.py
    │   ├── kafka_consumer.py
    │   └── sample_job.py
    └── output
        └── customers
```

---

# End-to-End CDC Pipeline Walkthrough

This section validates the entire pipeline:

```text
Postgres
   ↓
Debezium CDC
   ↓
Kafka Topic
   ↓
Spark Structured Streaming
   ↓
Parquet Files
```

---

## 1. Start Platform

Start all services:

```bash
docker compose \
  -f docker/compose/docker-compose.yaml \
  up -d
```

Verify:

```bash
docker ps
```

Expected containers:

```text
postgres
kafka
debezium-connect
postgres-updater
spark-local
spark-history-server
```

---

## 2. Verify PostgreSQL

Connect:

```bash
docker exec -it postgres \
  psql -U postgres -d inventory
```

Check table:

```sql
SELECT * FROM customers;
```

Verify logical replication:

```sql
SHOW wal_level;
```

Expected:

```text
logical
```

Exit:

```sql
\q
```

---

## 3. Verify Kafka

List topics:

```bash
docker exec kafka \
  /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list
```

Expected system topics:

```text
__consumer_offsets
```

At this point the Debezium CDC topic may not exist yet.

---

## 4. Verify Debezium Connect

List connectors:

```bash
curl http://localhost:8083/connectors
```

Expected:

```json
[]
```

or

```json
["postgres-connector"]
```

Register connector (only once):

```bash
curl -X POST \
  http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @debezium/postgres-connector.json
```

Check status:

```bash
curl \
  http://localhost:8083/connectors/postgres-connector/status
```

Expected:

```text
RUNNING
```

---

## 5. Generate CDC Events

The updater container continuously inserts/updates records.

View logs:

```bash
docker logs -f postgres-updater
```

Example:

```text
[UPDATE] id=14
[INSERT] id=25
```

You can also manually generate changes:

```bash
docker exec -it postgres \
  psql -U postgres -d inventory
```

```sql
UPDATE customers
SET age = 101
WHERE id = 1;
```

---

## 6. Verify Kafka CDC Topic

After Debezium sees the first change, it automatically creates:

```text
inventory.public.customers
```

Verify:

```bash
docker exec kafka \
  /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list
```

Expected:

```text
inventory.public.customers
```

Consume messages:

```bash
docker exec kafka \
  /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic inventory.public.customers \
  --from-beginning
```

You should see CDC events from Debezium.

---

## 7. Start Spark Consumer

Run the Kafka consumer:

```bash
./scripts/run.sh \
  spark/jobs/kafka_consumer.py \
  kafka
```

The Kafka profile automatically loads:

```text
spark/configs/kafka.conf
```

which provides:

```text
spark-sql-kafka connector
```

---

## 8. Verify Spark Streaming

Check running application:

http://localhost:4040

Verify Spark is consuming Kafka records.

---

## 9. Verify Output Files

Spark writes output to:

```text
spark/output/customers/
```

Check files:

```bash
find spark/output/customers
```

Expected:

```text
part-00000...
part-00001...
```

Check checkpoints:

```bash
find spark/checkpoints/customers
```

Expected:

```text
offsets/
commits/
sources/
```

---

## 10. View Spark History

Open:

http://localhost:18081

Historical Spark jobs will appear here once event logs are written.

---

## Cleanup

Stop everything:

```bash
docker compose \
  -f docker/compose/docker-compose.yaml \
  down
```

Remove volumes:

```bash
docker compose \
  -f docker/compose/docker-compose.yaml \
  down -v
```
