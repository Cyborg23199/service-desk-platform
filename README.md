# Service Desk Platform

A distributed Service Desk management system designed, deployed, and operated as part of the Service Engineering curriculum.

## 📌 Project Overview
The Service Desk Platform allows users to view, create, update, and manage system incidents. It is built using a multi-tier distributed architecture ensuring high availability, security, and end-to-end observability.

---

## 🏗 System Architecture (for Part 1)

```mermaid
flowchart TD
    Client["Clients / Web Browser / API Consumers"] -->|HTTPS :443| Nginx["Nginx Reverse Proxy\n(TLS Termination)"]
    Nginx -->|HTTP 127.0.0.1:8000| Gunicorn["Gunicorn WSGI Server"]
    Gunicorn --> Flask["Flask Application\n(Web UI + REST API)"]
    Flask -->|PostgreSQL Protocol :5432| DB[("PostgreSQL Database")]
```

---

## 🛠 Tech Stack

- **Operating System:** Linux (Ubuntu)
- **Web Server & Reverse Proxy:** Nginx
- **Application Framework:** Python (Flask + Gunicorn)
- **Database:** PostgreSQL
- **Service Management:** `systemd`
- **Observability Stack (Part 2):** Prometheus, Grafana, Node Exporter, Alertmanager

---

## 🚀 Deployment Progress

### Part 1: Design and Deployment
- [x] **Phase 1: VM Preparation & Network Hardening**
  - Updated system dependencies and configured hostname (`servicedesk-vm`).
  - Implemented non-privileged system user (`servicedesk`).
  - Configured firewall (`ufw`) allowing strictly SSH (22), HTTP (80), and HTTPS (443).
- [x] **Phase 2: Database Service & Schema Implementation**
  - Installed and secured PostgreSQL service.
  - Created dedicated application database (servicedesk) and unprivileged DB user.
  - Implemented schema for users, incidents, and comments with strict NOT NULL constraints and timestamp triggers.
- [x] **Phase 3: REST API Implementation**
  - Built modular Flask backend with SQLAlchemy ORM.
  - Implemented CRUD REST API endpoints for /api/users, /api/incidents, and /api/incidents/<id>/comments.
  - Enforced unprivileged PostgreSQL service connection.
- [x] **Phase 4: API Documentation (OpenAPI / Swagger)**
  - Integrated Flasgger library for automated Swagger UI generation.
  - Documented OpenAPI specs for all `/api/users`, `/api/incidents`, and `/api/comments` endpoints at `/apidocs`.
- [x] **Phase 5: Web User Interface**
  - Built a modular web frontend using Flask Blueprints (`src/web/`) and Jinja2 templates.
  - Created dashboard (`index.html`) for incident listing and creation, plus detail views (`detail.html`) for status updates and comment threads.
  - Connected frontend forms to the REST API via asynchronous JavaScript (`fetch` API) and styled with custom CSS.
- [x] **Phase 6: Production Deployment (Gunicorn & Nginx Reverse Proxy)**
  - Configured multi-worker WSGI execution using **Gunicorn** managed by a custom `systemd` service (`servicedesk.service`).
  - Deployed **Nginx** as a reverse proxy on port `80`, forwarding requests to the internal Gunicorn socket (`127.0.0.1:8000`) and serving static files.
- [x] **Phase 7: HTTPS / TLS Certificate Configuration**
  - Generated a 2048-bit RSA self-signed SSL/TLS certificate using OpenSSL.
  - Configured **Nginx** to terminate TLSv1.2/TLSv1.3 traffic on port `443` and enforce permanent HTTP-to-HTTPS redirection (`301`) from port `80`.
- [x] **Phase 8: Systemd Service Management & Lifecycle Control**
  - Standardized the application unit as `servicedesk-api.service` to clearly distinguish the backend WSGI/API service from the Nginx reverse proxy and PostgreSQL database units.
  - Enforced strict service dependencies (`Requires=postgresql.service`, `After=network.target postgresql.service`), production environment variables (`FLASK_ENV=production`), unprivileged execution (`User=uo324701`), and automatic fault recovery (`Restart=on-failure`, `RestartSec=5`).
- [x] **Phase 9: Logging & Diagnostics**
  - Configured dedicated Nginx access and error logs (`/var/log/nginx/servicedesk_access.log`, `/var/log/nginx/servicedesk_error.log`) and enabled structured Gunicorn request/error logging (`--access-logfile -`, `--error-logfile -`) routed to `systemd-journald`.
  - Verified cross-layer log correlation across Nginx, Gunicorn/Flask, `journalctl`, and PostgreSQL (`/var/log/postgresql/`).
- [x] **Phase 10: Security Hardening & Access Control**
  - Enforced network perimeter protection via `UFW` (exposing only ports `22`, `80`, and `443`) while isolating Gunicorn (`127.0.0.1:8000`) and PostgreSQL (`127.0.0.1:5432`) strictly to loopback interfaces.
  - Applied principle of least privilege across OS and database layers (`uo324701` service user, dedicated `servicedesk_user` DB role, `chmod 600` on sensitive files), externalized database credentials and `SECRET_KEY` out of source code into `/etc/servicedesk.env` (`chmod 640`, loaded via `systemd` `EnvironmentFile`), disabled Nginx version disclosure (`server_tokens off`), and verified hardened SSH settings.
- [x] **Phase 11: System Verification & Testing**
  - Created an automated verification suite (`scripts/run_tests.sh`) alongside manual validation covering REST API CRUD and comment workflows, full-stack integration (`Web UI -> REST API -> PostgreSQL`), external port isolation (`5432`, `8000`), and automatic service recovery after a full VM reboot.

### Part 2: Operation & Observability
- [ ] **Phase 1: Definition of Indicators**
- [ ] **Phase 2: System Monitoring (Node Exporter)**
- [ ] **Phase 3: Application Metrics (/metrics)**
- [ ] **Phase 4: Health Check (/health)**
- [ ] **Phase 5: Grafana Dashboard Setup**
- [ ] **Phase 6: Threshold Definition**
- [ ] **Phase 7: Alerting System (Prometheus Rules)**
- [ ] **Phase 8: Notification Delivery (Alertmanager)**
- [ ] **Phase 9: Load Generation & Testing**
- [ ] **Phase 10: Performance Analysis & Saturation Point**
- [ ] **Phase 11: Automated Database Backups**
- [ ] **Phase 12: Business Continuity & Controlled Disaster Recovery**
- [ ] **Phase 13: RPO & RTO Measurement**
- [ ] **Phase 14: Incident Simulation & Diagnostic Drills**
- [ ] **Phase 15: Infrastructure Reboot & Service Auto-Start**
- [ ] **Phase 16: Operations Runbook & Operational Report**
---

## 📖 Technical Report & Documentation

Detailed execution evidence, architectural decisions, and step-by-step logs are documented in the [Technical Report](docs/technical-report.md).