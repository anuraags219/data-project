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

# Start Platform

```bash
docker compose \
  -f docker/compose/docker-compose.yaml \
  up -d
```

Verify:

```bash
docker ps
```

---

# Stop Platform

```bash
docker compose \
  -f docker/compose/docker-compose.yaml \
  down
```

---

# Rebuild Spark Image

```bash
docker compose \
  -f docker/compose/docker-compose.yaml \
  build spark
```

---

# Restart Spark Only

```bash
docker compose \
  -f docker/compose/docker-compose.yaml \
  restart spark
```

---

# Spark Job Submission

Generic command:

```bash
./scripts/run.sh <job.py> [profile]
```

Examples:

## Run Standard Spark Job

```bash
./scripts/run.sh spark/jobs/sample_job.py
```

## Run Gluten Job

```bash
./scripts/run.sh spark/jobs/gluten_test.py gluten
```

## Run Kafka Consumer

```bash
./scripts/run.sh spark/jobs/kafka_consumer.py kafka
```

## Run Kafka + Gluten

```bash
./scripts/run.sh spark/jobs/kafka_consumer.py kafka,gluten
```

---

# Spark Profiles

## Default

Always loaded:

```text
spark/configs/spark-default.conf
```

## Kafka

Additional Kafka connector configuration:

```text
spark/configs/kafka.conf
```

## Gluten

Additional Gluten acceleration configuration:

```text
spark/configs/gluten.conf
```

---

# Kafka

List Topics:

```bash
docker exec kafka \
  /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list
```

Consume CDC Events:

```bash
docker exec kafka \
  /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic inventory.public.customers \
  --from-beginning
```

---

# Debezium

List Connectors:

```bash
curl http://localhost:8083/connectors
```

Connector Status:

```bash
curl http://localhost:8083/connectors/postgres-connector/status
```

---

# PostgreSQL

Connect:

```bash
docker exec -it compose-postgres-1 \
  psql -U postgres -d inventory
```

Example Query:

```sql
SELECT * FROM customers;
```

---

# Logs

Spark:

```bash
docker logs -f spark-local
```

Kafka:

```bash
docker logs -f kafka
```

Debezium:

```bash
docker logs -f connect
```

Postgres:

```bash
docker logs -f compose-postgres-1
```

Updater:

```bash
docker logs -f postgres-updater
```

---

# Web UI

## Spark History Server

http://localhost:18081

## Debezium Connect REST API

http://localhost:8083

## Spark Application UI

Available while a Spark job is running:

http://localhost:4040

---

# CDC Topic

Current Debezium topic:

```text
inventory.public.customers
```

Generated events:

```text
c = insert
u = update
d = delete
```

---

# Output Locations

Spark Output:

```text
spark/output/
```

Spark Checkpoints:

```text
spark/checkpoints/
```

Spark Event Logs:

```text
spark-events volume
```
