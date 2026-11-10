# Service Desk Platform - Technical Report

## 1. System Architecture & Infrastructure Overview
- **Operating System:** Linux (Ubuntu)
- **Hostname:** `servicedesk-vm`
- **Assigned IP Address:** `156.35.165.47/24`
- **Hardware Resources:**
  - **CPU Cores:** `2`
  - **RAM:** `1.6 GiB`
  - **Storage:** `18 GB`

---

## 2. Phase 1: Machine Preparation & Hardening

### 2.1 System Updates, User Management & SSH
- System package index was updated and all packages were upgraded to their latest versions via `apt update && apt upgrade`.
- Hostname was configured to `servicedesk-vm` using `hostnamectl set-hostname`.
- Created a non-privileged system user `servicedesk` (`adduser --system --group --disabled-login servicedesk`) to run application services under the principle of least privilege.
- Remote SSH access on TCP port 22 was verified and restricted to default infrastructure access controls.
- Outbound network connectivity was confirmed via ICMP ping checks to external DNS resolvers.

### 2.2 Network Hardening & Port Justification
The network firewall (`ufw`) is configured with a strict `default deny incoming` policy. Only essential public web and management services are exposed externally, while backend database and application services remain strictly bound to `localhost`:

| Port | Protocol | Service | Exposure | Justification |
| :--- | :--- | :--- | :--- | :--- |
| **22** | TCP | SSH | Public | Remote VM administration and maintenance. |
| **80** | TCP | HTTP | Public | Public entry point for static assets and HTTP to HTTPS redirection. |
| **443** | TCP | HTTPS | Public | Secure entry point for Nginx reverse proxy serving Web UI and API endpoints. |
| **5432** | TCP | PostgreSQL | Internal (`localhost`) | Relational database engine, isolated from public access. |
| **5000** | TCP | REST API (Gunicorn / Flask) | Internal (`localhost`) | Application backend engine, accessible exclusively via Nginx proxy. |

#### Verification Evidences:
![UFW Firewall Status](images/01-ufw-status.png)