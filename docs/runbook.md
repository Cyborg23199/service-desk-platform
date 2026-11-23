# Service Desk Platform — Operational Runbook

**System:** Service Desk Incident Management Platform  
**Environment:** Single-node Linux VM (`Ubuntu 24.04 LTS`, `2 vCPU`, `2 GB RAM`, `18 GB Disk`)  
**Primary Endpoints:**  
- **Application & API (HTTPS):** `https://<VM_IP>/` | Health: `https://<VM_IP>/health` | Metrics: `http://127.0.0.1:8000/metrics`  
- **Prometheus:** `http://127.0.0.1:9090` (via SSH tunnel)  
- **Alertmanager:** `http://127.0.0.1:9093` (via SSH tunnel)  
- **Grafana:** `http://127.0.0.1:3000` (via SSH tunnel)  

---

## 1. Architecture & Service Dependencies

### 1.1 Request & Telemetry Flow
- **Client Traffic:** `Client (HTTPS :443)` -> `Nginx Reverse Proxy` -> `Gunicorn / Flask API (127.0.0.1:8000)` -> `PostgreSQL (127.0.0.1:5432)`
- **Observability Pipeline:** `Prometheus (127.0.0.1:9090)` scrapes `/metrics` from `servicedesk-api` (`:8000`), `node_exporter` (`:9100`), and self (`:9090`) every `15s` -> evaluates `alert_rules.yml` -> routes alerts to `Alertmanager (127.0.0.1:9093)` -> dispatches Slack webhook notifications (`#servicedesk-alerts`), while `Grafana (127.0.0.1:3000)` visualizes Prometheus metrics.
- **Backup Pipeline:** `servicedesk-backup.timer` (`02:00:00` daily) -> `servicedesk-backup.service` (`scripts/backup_db.sh`) -> `pg_dump -Fc` + SHA-256 verification -> `/var/backups/servicedesk/` (`7-day` retention).

### 1.2 Startup & Runtime Dependencies
- `servicedesk-api.service` requires `network.target` and `postgresql.service` (`After=network.target postgresql.service`). If PostgreSQL is down, API `/health` degrades to `HTTP 503` and write/read queries fail with `HTTP 500`.
- `nginx.service` proxies external HTTPS traffic to `127.0.0.1:8000`; if `servicedesk-api` is stopped, Nginx returns `HTTP 502 Bad Gateway`.

---

## 2. Service Inventory & Essential Commands

| Component | Systemd Unit | Listening Port | Configuration Path | Log Inspection Command |
| :--- | :--- | :--- | :--- | :--- |
| **Reverse Proxy** | `nginx.service` | `80`, `443` | `/etc/nginx/sites-available/servicedesk` | `sudo journalctl -u nginx -n 50 --no-pager` |
| **Backend API** | `servicedesk-api.service` | `127.0.0.1:8000` | `/etc/systemd/system/servicedesk-api.service` | `sudo journalctl -u servicedesk-api -n 50 --no-pager` |
| **Database** | `postgresql.service` | `127.0.0.1:5432` | `/etc/postgresql/*/main/` | `sudo journalctl -u postgresql -n 50 --no-pager` |
| **Metrics Scraper** | `prometheus.service` | `127.0.0.1:9090` | `/etc/prometheus/prometheus.yml` | `sudo journalctl -u prometheus -n 50 --no-pager` |
| **Host Exporter** | `node_exporter.service` | `127.0.0.1:9100` | `/etc/systemd/system/node_exporter.service` | `sudo journalctl -u node_exporter -n 50 --no-pager` |
| **Alert Router** | `alertmanager.service` | `127.0.0.1:9093` | `/etc/alertmanager/alertmanager.yml` | `sudo journalctl -u alertmanager -n 50 --no-pager` |
| **Dashboards** | `grafana-server.service` | `127.0.0.1:3000` | `/etc/grafana/grafana.ini` | `sudo journalctl -u grafana-server -n 50 --no-pager` |
| **Daily DB Backup** | `servicedesk-backup.timer` | — | `/etc/systemd/system/servicedesk-backup.*` | `sudo journalctl -u servicedesk-backup.service -n 50 --no-pager` |

---

## 3. Standard Operating Procedures (SOPs)

### 3.1 Post-Reboot & Daily Health Checklist
Run the following verification commands after maintenance or VM reboot:

    systemctl is-active postgresql servicedesk-api nginx prometheus node_exporter alertmanager grafana-server servicedesk-backup.timer
    curl -sk https://127.0.0.1/health
    curl -s http://127.0.0.1:9090/api/v1/targets | grep -o '"health":"[^"]*"'
    df -h /

**Expected Outcome:** All 8 units report `active`, `/health` returns `{"status":"healthy"}`, all 3 Prometheus targets report `"health":"up"`, and `/` disk usage is `< 80%`.

### 3.2 Safe Configuration Reloads
- **Nginx:** `sudo nginx -t && sudo systemctl reload nginx`
- **Prometheus & Alert Rules:** `promtool check config /etc/prometheus/prometheus.yml && promtool check rules /etc/prometheus/alert_rules.yml && sudo systemctl reload prometheus`
- **Alertmanager:** `amtool check-config /etc/alertmanager/alertmanager.yml && sudo systemctl restart alertmanager`
- **Systemd Units:** `sudo systemctl daemon-reload && sudo systemctl restart <unit_name>`

---

## 4. Incident Response Playbooks (Main Alerts & Recovery)

### 4.1 `ServiceDeskAPIDown` (`CRITICAL`)
- **Trigger:** `up{job="servicedesk_api"} == 0` for `> 1m`. Users see `HTTP 502 Bad Gateway`.
- **Diagnosis:**

      sudo systemctl status servicedesk-api --no-pager
      sudo journalctl -u servicedesk-api -n 40 --no-pager

- **Remediation:**

      sudo systemctl restart servicedesk-api
      curl -sk https://127.0.0.1/health

- **Escalation:** If Gunicorn fails to bind or crashes repeatedly, inspect `/etc/servicedesk.env` and recent commits in `git log -n 5`.

### 4.2 `ServiceDeskPostgreSQLDown` (`CRITICAL`)
- **Trigger:** `max(servicedesk_db_up) == 0` for `> 1m`. `/health` returns `HTTP 503`; API mutations return `HTTP 500`.
- **Diagnosis:**

      sudo systemctl status postgresql --no-pager
      sudo journalctl -u postgresql -n 40 --no-pager
      df -h /

- **Remediation:**

      sudo systemctl start postgresql
      curl -sk https://127.0.0.1/health

- **Escalation:** If PostgreSQL fails due to corrupted data files or accidental database drop, execute the Disaster Recovery procedure in Section 5.2.

### 4.3 `HighHostCPUUsageWarning` / `HighHostCPUUsageCritical` (`> 75%` / `> 90%`)
- **Trigger:** Sustained host CPU utilization above threshold (`for: 5m` warning / `for: 3m` critical).
- **Diagnosis:**

      uptime
      ps -eo pid,ppid,cmd,%cpu,%mem --sort=-%cpu | head -n 10

- **Remediation:**
  - If caused by legitimate traffic spikes, inspect `HTTP Requests / sec` in Grafana (saturation threshold is `~600 RPS` at concurrency `c=20`).
  - If caused by a runaway process, terminate it safely (`kill -TERM <PID>`, or `kill -9 <PID>` if unresponsive).

### 4.4 `HighHostMemoryUsageWarning` / `HighHostMemoryUsageCritical` (`> 80%` / `> 92%`)
- **Trigger:** Available RAM drops below `20%` (`warning`) or `8%` (`critical`, high OOM-killer risk).
- **Diagnosis:**

      free -h
      ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head -n 10

- **Remediation:** Restart memory-heavy non-critical services or verify Gunicorn worker count (`3 workers` configured in `servicedesk-api.service`).

### 4.5 `HighRootDiskUsageWarning` / `HighRootDiskUsageCritical` (`> 80%` / `> 90%`)
- **Trigger:** Root filesystem (`/`) usage exceeds `80%` (`for: 10m`) or `90%` (`for: 5m`).
- **Diagnosis:**

      df -h /
      sudo du -xh / --max-depth=2 2>/dev/null | sort -hr | head -n 15

- **Remediation:**
  - Vacuum old systemd journal logs: `sudo journalctl --vacuum-time=7d`
  - Clean APT package cache: `sudo apt-get clean`
  - Remove stale temporary files in `/tmp` or `/var/tmp` and verify `/var/backups/servicedesk/` honors the 7-day retention policy.

### 4.6 `HighHTTP5xxErrorRateWarning` / `HighHTTP5xxErrorRateCritical` (`> 1%` / `> 5%`)
- **Trigger:** Elevated server-side errors (`HTTP 5xx`) across API endpoints.
- **Diagnosis:**

      sudo journalctl -u servicedesk-api -n 50 --no-pager
      sudo tail -n 50 /var/log/nginx/error.log

- **Remediation:** Correlate failing endpoints in Grafana (`HTTP Errors` panel) with database health (`servicedesk_db_up`) and restart `servicedesk-api` if worker deadlock is suspected.

---

## 5. Backup & Database Restoration Procedures

- **RPO Target:** `24 hours` (automated daily backup at `02:00:00` via `servicedesk-backup.timer`).
- **RTO Target:** `15 minutes` (validated actual recovery time: **`2.62 seconds`**).

### 5.1 Manual On-Demand Backup (Pre-Maintenance)

    cd /home/uo324701/service-desk-platform
    sudo ./scripts/backup_db.sh
    sudo ls -lh /var/backups/servicedesk/

### 5.2 Full Database Restoration (`restore_db.sh`)

    cd /home/uo324701/service-desk-platform
    LATEST_DUMP="$(sudo find /var/backups/servicedesk -maxdepth 1 -name 'servicedesk_*.dump' | sort -r | head -n 1)"
    sudo ./scripts/restore_db.sh "${LATEST_DUMP}"
    curl -sk https://127.0.0.1/health
