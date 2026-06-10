#!/bin/bash

set -e

JOB=$1
PROFILE=${2:-default}

CONTAINER="spark-local"
SPARK="/opt/spark/bin/spark-submit"

JOB_IN_CONTAINER="/opt/spark/jobs/$(basename $JOB)"
CONFIG="/opt/spark/configs"

ARGS=""

# base config
while IFS='=' read -r k v; do
  [[ -n "$k" ]] && ARGS="$ARGS --conf $k=$v"
done < <(docker exec $CONTAINER cat $CONFIG/spark-default.conf)

# gluten config
if [ "$PROFILE" == "gluten" ]; then
  while IFS='=' read -r k v; do
    [[ -n "$k" ]] && ARGS="$ARGS --conf $k=$v"
  done < <(docker exec $CONTAINER cat $CONFIG/gluten.conf)
fi

docker exec $CONTAINER \
  $SPARK \
  $ARGS \
  $JOB_IN_CONTAINER