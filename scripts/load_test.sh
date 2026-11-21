#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://127.0.0.1/api/incidents"
OUT_DIR="docs/evidence"
OUT_FILE="${OUT_DIR}/load_test_results.txt"

mkdir -p "${OUT_DIR}"
: > "${OUT_FILE}"

echo "=== Service Desk Platform Load Test Suite ($(date -Iseconds)) ===" | tee -a "${OUT_FILE}"

# Scenarios format: "scenario_name|total_requests|concurrency"
SCENARIOS=(
  "Level_1_Light_c5|500|5"
  "Level_2_Moderate_c20|2000|20"
  "Level_3_Heavy_c50|4000|50"
  "Level_4_Saturation_c100|5000|100"
)

for entry in "${SCENARIOS[@]}"; do
  IFS="|" read -r NAME REQUESTS CONCURRENCY <<< "${entry}"
  echo "" | tee -a "${OUT_FILE}"
  echo ">>> Running ${NAME}: n=${REQUESTS}, c=${CONCURRENCY} against ${BASE_URL}" | tee -a "${OUT_FILE}"
  ab -k -l -n "${REQUESTS}" -c "${CONCURRENCY}" "${BASE_URL}" | tee -a "${OUT_FILE}"
  echo ">>> Cooling down 20s for Prometheus scrape alignment..." | tee -a "${OUT_FILE}"
  sleep 20
done

echo "" | tee -a "${OUT_FILE}"
echo "=== Load test suite completed at $(date -Iseconds) ===" | tee -a "${OUT_FILE}"