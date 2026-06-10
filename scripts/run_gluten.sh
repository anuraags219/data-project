#!/bin/bash

docker exec -u spark spark-local \
/opt/spark/bin/spark-submit \
--properties-file /opt/spark/configs/gluten.conf \
--jars /opt/gluten/gluten-velox-bundle-spark3.5_2.12-linux_amd64-1.6.0.jar \
"$1"