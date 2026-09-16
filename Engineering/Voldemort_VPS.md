---
tags:
  - infrastructure/vps
  - devops
  - sre
aliases:
  - voldemort-vps
title: "Voldemort VPS Infrastructure & Topology"
---

# 🖥️ Voldemort VPS Infrastructure

> **Environment**: Remote Production Cloud VPS (`voldemort-vps`)
> **Primary User**: `voldemort`
> **Layout**: Modular `/home/voldemort/services/`
> **Related**: [[Engineering/DevOps_Isolation_Policy|🔒 DevOps Isolation Policy]] | [[Engineering/Index|⚡ Engineering MOC]]

---

## 🏛️ Service Topology

- **Isolation**: Container-first architecture (Docker Compose per service).
- **Hermes Gateway**: `hermes-gateway.service` running 24/7.
- **Telegram Bot**: Modular v2.0 Docker container (`@Voldemort_menu_bot`).
- **Database**: PostgreSQL container with automated volume backups.
- **Object Storage**: Synced with Cloudflare R2 (`voldemort-gallery`).
