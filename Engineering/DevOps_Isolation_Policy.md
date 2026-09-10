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
   - Seluruh agent selain `devops` (`code`, `ultracode`, `ask`, `plan`, `debug`, `orchestrator`) **DILARANG KERAS** menjalankan command `ssh <vps-host>`, `scp`, `rsync` ke remote host.
3. **Automated Sub-Agent Delegation (Frictionless Integration)**:
   - Jika agent `ultracode` atau agent coding lainnya memerlukan pembacaan log server, schema DB, atau health check di VPS, agent tersebut dilarang mengakses langsung dan **WAJIB** mendelegasikan tugas ke sub-agent `devops` via tool `task(subagent_type='devops', ...)` secara otonom.

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
