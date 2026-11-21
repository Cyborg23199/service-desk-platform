#!/usr/bin/env bash
set -euo pipefail

DB_NAME="servicedesk"
BACKUP_DIR="/var/backups/servicedesk"
RETENTION_DAYS=7
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.dump"
CHECKSUM_FILE="${BACKUP_FILE}.sha256"

mkdir -p "${BACKUP_DIR}"

echo "[$(date -Iseconds)] Starting PostgreSQL backup for database '${DB_NAME}'..."
sudo -u postgres pg_dump -Fc -f "${BACKUP_FILE}" "${DB_NAME}"

# Integrity verification: ensure archive table of contents is readable and non-empty
echo "[$(date -Iseconds)] Verifying backup archive integrity..."
TABLE_COUNT="$(sudo -u postgres pg_restore --list "${BACKUP_FILE}" | grep -c "TABLE DATA" || true)"
if [[ "${TABLE_COUNT}" -lt 1 ]]; then
  echo "[$(date -Iseconds)] ERROR: Backup verification failed (no TABLE DATA entries found)." >&2
  rm -f "${BACKUP_FILE}"
  exit 1
fi

sha256sum "${BACKUP_FILE}" > "${CHECKSUM_FILE}"
chmod 640 "${BACKUP_FILE}" "${CHECKSUM_FILE}"

# Retention policy: remove backups older than RETENTION_DAYS
find "${BACKUP_DIR}" -type f \( -name "${DB_NAME}_*.dump" -o -name "${DB_NAME}_*.dump.sha256" \) -mtime "+${RETENTION_DAYS}" -delete

BACKUP_SIZE="$(du -h "${BACKUP_FILE}" | cut -f1)"
echo "[$(date -Iseconds)] Backup succeeded: ${BACKUP_FILE} (size=${BACKUP_SIZE}, verified_tables=${TABLE_COUNT})"