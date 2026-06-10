#!/bin/bash

set -euo pipefail

JOB=$1
PROFILES=${2:-}

CONTAINER="spark-local"
SPARK="/opt/spark/bin/spark-submit"

JOB_IN_CONTAINER="/opt/spark/jobs/$(basename "$JOB")"

ARGS=""

load_conf() {
    local CONF_FILE="$1"

    echo "Loading config: $CONF_FILE"

    while IFS='=' read -r key value || [[ -n "$key" ]]; do

        # trim whitespace
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)

        # skip blanks/comments
        [[ -z "$key" ]] && continue
        [[ "$key" =~ ^# ]] && continue

        echo "  $key=$value"

        ARGS="$ARGS --conf $key=$value"

    done < <(
        docker exec "$CONTAINER" sh -c "cat $CONF_FILE 2>/dev/null || true"
    )
}

# --------------------------------------------------
# Always load base Spark config
# --------------------------------------------------

load_conf /opt/spark/configs/spark-default.conf

# --------------------------------------------------
# Load optional profiles
# Example:
#   kafka
#   gluten
#   kafka,gluten
# --------------------------------------------------

if [[ -n "$PROFILES" ]]; then

    IFS=',' read -ra PROFILE_LIST <<< "$PROFILES"

    for PROFILE in "${PROFILE_LIST[@]}"; do

        PROFILE=$(echo "$PROFILE" | xargs)

        load_conf "/opt/spark/configs/${PROFILE}.conf"

    done
fi

echo ""
echo "Submitting:"
echo "$SPARK $ARGS $JOB_IN_CONTAINER"
echo ""

docker exec "$CONTAINER" \
    $SPARK \
    $ARGS \
    "$JOB_IN_CONTAINER"