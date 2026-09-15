---
tags:
  - architecture
  - devops
  - sre
  - security
date: "2026-09-10"
---

# 🔒 DevOps VPS Isolation & Server Clean Layout Policy

> **Single Source of Truth**: `/Users/pt-dika/Documents/Obsidian/Engineering/DevOps_Isolation_Policy.md`

---

## 🛡️ 1. Principle of Exclusive Delegation (Zero-Trust Tool Isolation)

1. **Exclusive Delegation**:
   - **HANYA** agent `devops` yang memiliki otorisasi untuk berinteraksi, menjalankan perintah SSH, deploy service, mengelola Docker container, atau mengubah konfigurasi di remote server VPS (`voldemort-vps` / production / staging).
2. **Hard Lockdown for Other Agents**:
   - Seluruh agent selain `devops` (`code`, `maestro`, `scout`, `builder`, `reviewer`, `ask`, `plan`, `debug`, `orchestrator`) **DILARANG KERAS** menjalankan command `ssh <vps-host>`, `scp`, `rsync` ke remote host.
3. **Automated Sub-Agent Delegation (Frictionless Integration)**:
   - Jika agent `maestro` atau agent coding lainnya memerlukan pembacaan log server, schema DB, atau health check di VPS, agent tersebut dilarang mengakses langsung dan **WAJIB** mendelegasikan tugas ke sub-agent `devops` via tool `task(subagent_type='devops', ...)` secara otonom.

---

## 🏗️ 2. Server Data Architecture & Clean Layout Hygiene

1. **Modular Service Directory Hierarchy**:
   - Semua service wajib terpusat dan terisolasi di direktori terstandarisasi (`~/services/<service-name>` atau `/opt/services/<service-name>`).
   - Dilarang menyebar file script, konfigurasi sementara, atau data di root `/`, `/tmp`, atau root home user.
   - **Struktur Standar Setiap Service**:

     ```
     ~/services/<service-name>/
     ├── docker-compose.yml       # Single source of truth untuk stack container
     ├── .env                     # Environment variables & secret (chmod 600)
     ├── config/                  # Folder konfigurasi mounted (nginx, caddy, json, yaml)
     └── data/                    # Persistent bind-mounts / volume mappings
     ```

2. **Container-First Doctrine (Zero Host Pollution)**:
   - Dilarang menginstall package, runtime, atau library langsung di host OS (`apt install nodejs`, `pip install`, dll.) bila service tersebut dapat di-containerize via Docker. Host OS wajib dijaga lean, minimalis, dan bersih.
3. **Safe Config Versioning & Backup Before Touch**:
   - Sebelum menyentuh/mengubah file konfigurasi server yang sedang aktif, wajib membuat backup snapshot lokal di direktori yang sama:

     ```bash
     cp config.yml config.yml.bak.$(date +%Y%m%d%H%M%S)
     ```

4. **Network & Reverse Proxy Isolation**:
   - Service internal dilarang melakukan port binding langsung ke `0.0.0.0:<port>`. Seluruh service internal wajib bind ke `127.0.0.1:<port>` atau Docker internal network, dan di-route via Central Reverse Proxy (Caddy / Nginx / Traefik) dengan HTTPS otomatis.

---

## ⚡ 3. SRE Operational Protocol & Safety Guardrails

1. **Pre-Flight Verification**: Selalu verifikasi target host (`hostname`), user (`whoami`), dan working directory (`pwd`) sebelum mengeksekusi mutating action.
2. **Blast Radius & Destructive Guard**: Operasi destruktif (`rm -rf`, `docker compose down -v`, database drop/migrate, `iptables -F`) wajib didahului verifikasi ganda dan konfirmasi user.
3. **Idempotency & Zero Downtime**: Utamakan `docker compose up -d --build` & non-breaking proxy reload (`nginx -s reload`) daripada full restart.
4. **Post-Deploy Observability**: Wajib langsung cek status container (`docker ps`), endpoint healthcheck (`curl -fsSL`), dan tail logs (`docker logs --tail 50 <container>`) setelah setiap perubahan.
5. **Secret Hygiene**: Dilarang menampilkan raw credentials, token, private key, atau production password di plain text output terminal.

---

## 💎 4. Hardened DevOps & Universal Engineering Quality Mandates

Setiap eksekusi task oleh agent `devops` (dan seluruh squad agent) **WAJIB** menerapkan 7 standar kualitas fundamental:

1. **Structured & Standardized Execution (Terstruktur & Terstandarisasi)**:
   - Layout direktori kanonikal (`~/services/<service>/`), Docker compose terstruktur, konfigurasi modular, dan lifecycle operasional baku (*pre-flight -> timestamped backup -> deploy -> observability verify*).
2. **Robust & Bullet-Proof (Tahan Banting & Fail-Safe)**:
   - Fail-closed error handling di semua script automasi, safe fallback, explicit timeout pada command remote, non-zero exit trap (`set -euo pipefail`), dan kernel hung task protection (`kernel.hung_task_panic=0`).
3. **Future-Proof & Backward-Compatible (Skalabilitas & Jangka Panjang)**:
   - Desain container & proxy backward-compatible, skema environment terisolasi, skrip otomatisasi independen dari versi OS, dan automated weekly virtual disk maintenance (`fstrim.timer`).
4. **Anti-Memory Leak & Resource Hygiene (Nol Kebocoran Memori & Resource)**:
   - **Docker Log Rotation**: Wajib terpasang di daemon (`max-size: 50m`, `max-file: 3`).
   - **Systemd Journald Caps**: Batas kuota ketat (`SystemMaxUse=200M`, `MaxRetentionSec=7day`).
   - **Kernel Dirty Page Throttling**: Buffer flush agresif (`vm.dirty_background_ratio=5`, `vm.dirty_ratio=10`).
   - **Postgres WAL & DB Dumps**: Rotasi automated backup harian (`find ... -mtime +7 -delete`).
5. **Anti-Race Condition & Atomic Concurrency (Nol Race Condition)**:
   - Semua cron/timer script wajib memakai atomic lockfile non-blocking (`exec 200>/var/lock/<service>.lock; flock -n 200 || exit 0`).
   - Dilarang menjalankan multiple mutating automations secara simultan pada shared storage/state tanpa lock guard.
6. **Anti-Rate Limit & Throttling Resilience (Kebal Rate Limit)**:
   - Nginx proxy connection pooling (`keepalive 32`), dynamic rate-limiting zones (`limit_req_zone`), dan client retry backoff dengan jitter pada webhook/integrasi luar.
7. **Readable & Self-Documenting (Mudah Dibaca & Maintainable)**:
   - Skrip bersih ber-header bash standar, konfigurasi self-explanatory dengan komentar esensial, penamaan service deskriptif, dan zero cryptic hacks.

