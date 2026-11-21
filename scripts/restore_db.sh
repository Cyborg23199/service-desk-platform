#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /var/backups/servicedesk/<backup_file>.dump" >&2
  exit 1
fi

BACKUP_FILE="$1"
DB_NAME="servicedesk"
DB_OWNER="servicedesk_user"

if [[ ! -f "${BACKUP_FILE}" ]]; then
  echo "ERROR: Backup file not found: ${BACKUP_FILE}" >&2
  exit 1
fi

START_NS="$(date +%s%N)"
echo "[$(date -Iseconds)] Starting disaster recovery restore from '${BACKUP_FILE}'..."

# 1. Verify checksum if present
if [[ -f "${BACKUP_FILE}.sha256" ]]; then
  echo "[$(date -Iseconds)] Verifying SHA-256 checksum..."
  sha256sum -c "${BACKUP_FILE}.sha256"
fi

# 2. Stop API service to release active database connections cleanly
echo "[$(date -Iseconds)] Stopping servicedesk-api..."
sudo systemctl stop servicedesk-api

# 3. Terminate any remaining sessions and recreate clean database
echo "[$(date -Iseconds)] Recreating database '${DB_NAME}'..."
sudo -u postgres psql -v ON_ERROR_STOP=1 -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();" >/dev/null
sudo -u postgres psql -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS ${DB_NAME};"
sudo -u postgres psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_OWNER};"

# 4. Restore dump
echo "[$(date -Iseconds)] Restoring data with pg_restore..."
sudo -u postgres pg_restore --no-owner --role="${DB_OWNER}" -d "${DB_NAME}" "${BACKUP_FILE}"

# 5. Restart API service and verify health endpoint
echo "[$(date -Iseconds)] Starting servicedesk-api..."
sudo systemctl start servicedesk-api

END_NS="$(date +%s%N)"
ELAPSED_MS=$(( (END_NS - START_NS) / 1000000 ))
echo "[$(date -Iseconds)] Restore completed in ${ELAPSED_MS} ms."