---
tags:
  - engineering/architecture
  - telegram
  - bots
  - hermes
  - cloudflare
title: "🤖 Telegram Bots Dual Architecture & Modular Engine Specification"
---

# 🤖 Telegram Bots Dual Architecture & Modular Engine Specification

Comprehensive technical specification for the **Dual Telegram Bot Ecosystem** running 24/7 on `voldemort-vps` and local developer environment.

---

## 🏛️ 1. High-Level Dual Bot Landscape

The environment operates **two distinct, complementary Telegram Bots** serving separate architectural domains:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TELEGRAM ECOSYSTEM (VPS 24/7)                              │
│                                                                                             │
│  ┌──────────────────────────────────────────┐    ┌──────────────────────────────────────────┐
│  │ 🤖 BOT 1: Voldemort Menu Bot             │    │ ⚕️ BOT 2: Hermes AI Assistant Gateway    │
│  │ • Handle: @Voldemort_menu_bot            │    │ • Handle: Dedicated Assistant Bot        │
│  │ • Token: 8874533491:AAHh...              │    │ • Token: 8247955434:AAEE...              │
│  │ • Runtime: Docker (voldemort-menu-bot)   │    │ • Runtime: Systemd Unit (hermes-gateway) │
│  │ • Domain: Menu UI, Flux AI, MarkItDown,  │    │ • Domain: Autonomous Engineering, 67     │
│  │   Dozzle VPS Status, Cloudflare R2 Mon   │    │   Skills, Google Workspace, Deep Memory  │
│  └──────────────────┬───────────────────────┘    └────────────────────┬─────────────────────┘
│                     │                                                 │
│                     ▼                                                 ▼
│  ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                                 SHARED INFRASTRUCTURE                                  │ │
│  │ • OmniRoute AI Gateway: http://127.0.0.1:20128/v1 (Model: AG -> Gemini Flash High Pool) │ │
│  │ • Cloudflare Workers AI & R2: @cf/flux-1-schnell & bucket voldemort-gallery             │ │
│  │ • Persistent Storage: ~/.hermes/state.db, ~/.hermes/memories/USER.md, ~/.hermes/skills/ │ │
│  └────────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 2. Bot 1: Voldemort Menu Bot (`@Voldemort_menu_bot`)

### A. Modular Package Architecture (`telegram_bot/`)
Refactored from a 1,300-line monolithic script into a clean, decoupled Python package:

```text
telegram_bot/
├── __init__.py               # Package metadata (v2.0.0)
├── config.py                 # Central config, env vars, admin guards, logger
│
├── core/                     # Core Processing & AI Integrations
│   ├── prompt_rules.py       # 8 visual style rules (photorealistic, cinematic, cyberpunk, anime, etc.)
│   ├── meta_prompt.py        # Meta-prompt compiler & AI markdown restructure via OmniRoute
│   └── markitdown_ops.py     # Microsoft MarkItDown extraction (files, tables, audio, URLs)
│
├── services/                 # Cloud & Infrastructure Services
│   ├── cloudflare_flux.py    # Cloudflare Workers AI FLUX.1 generator & daily quota tracker
│   ├── cloudflare_r2.py      # Cloudflare R2 auto-uploader & live bucket quota telemetry
│   └── vps_telemetry.py      # Dozzle probe, host RAM/CPU/Disk metrics, Docker fleet status
│
├── ui/                       # Presentation & Formatting
│   ├── keyboards.py          # Dynamic inline keyboards with role-based visibility filtering
│   └── formatters.py         # Markdown fallback safe-senders & smart caption editors
│
├── handlers/                 # Event & Message Handlers
│   ├── commands.py           # /start, /help, /reset
│   ├── callbacks.py          # Callback query router & state transition engine
│   ├── doc_handler.py        # Document upload handler (PDF, DOCX, XLSX, PPTX, CSV)
│   └── text_handler.py       # Multi-mode text & prompt input processor
│
└── main.py                   # Application builder & polling lifecycle
```

### B. Feature Matrix & Access Control
| Feature | Target Audience | Technology Stack |
|---|---|---|
| **✍️ Meta-Prompt Generator** | Public / All Users | OmniRoute LLM (`AG`), 6 categories, bilingual (ID/EN) |
| **🖼️ Flux.1 Image Synthesis** | Public / All Users | Cloudflare Workers AI FLUX.1 Schnell + auto R2 storage |
| **📑 Microsoft MarkItDown** | Public / All Users | Fast local extraction or Vision OCR via LLM |
| **📊 Daily Quota Tracker** | Public / All Users | Free tier 60 images tracker with progress bar |
| **🖥️ Status VPS & Dozzle** | **Admin Only (`708066102`)** | Live host `/proc` stats, Dozzle container probe, Docker stats |
| **☁️ Monitor Cloudflare R2** | **Admin Only (`708066102`)** | Direct R2 REST API, partition breakdown, 10 GB quota gauge |

### C. Containerized Docker Deployment
- **Directory**: `/home/voldemort/services/telegram-bot/`
- **Image**: `voldemort-menu-bot:2.0.0`
- **Container Name**: `voldemort-menu-bot`
- **Network**: `host` (zero latency to `127.0.0.1:20128` OmniRoute and `127.0.0.1:8888` Dozzle)
- **Resource Limits**: `cpus: '0.5'`, `memory: 256M`

---

## ⚕️ 3. Bot 2: Hermes AI Assistant Telegram Gateway

### A. Core Engine & Capabilities
- **Engine**: Native Hermes Autonomous Agent daemon (`hermes gateway run --external-supervisor`).
- **Personality**: `Hermes Ultracode` (`SOUL.md`) with 4-phase dynamic workflow engine and Jaksel SRE persona.
- **Skill Arsenal**: **67 active skill packages** with pre-installed virtualenv dependencies (`docx`, `pdf-toolkit`, `youtube-content`, `reddit-reading`, `web-search`, etc.).
- **Workspace Integration**: Google Workspace API OAuth2 (`gmail`, `drive`, `calendar`, `docs`, `sheets`).
- **Memory Subsystem**: Persistent user profiling (`~/.hermes/memories/USER.md`), SQLite session state (`state.db`), and cron execution ledger.

### B. Systemd Daemon Deployment
- **Unit**: `/etc/systemd/system/hermes-gateway.service`
- **User**: `voldemort`
- **Working Directory**: `/home/voldemort/.hermes`
- **Auto-Restart**: `always` (restart delay 5s)
- **Logs**: `/home/voldemort/.hermes/logs/gateway.log`

---

## 🛡️ 4. Zero-Conflict Polling Guarantee

Running multiple polling bots on the same token triggers `HTTP 409 Conflict: terminated by other getUpdates request`. The infrastructure prevents this via:
1. **Isolated Tokens**: Bot 1 (`8874533491:...`) and Bot 2 (`8247955434:...`) use dedicated bot tokens registered via `@BotFather`.
2. **Decommissioned Local Daemons**: The local macOS launchd job `ai.hermes.gateway` was cleanly unloaded (`launchctl bootout`) to ensure exclusive 24/7 cloud polling from `voldemort-vps`.

---

## 🔍 5. Quick Health & Diagnostic Commands

```bash
# 1. Check Voldemort Menu Bot Container Status
ssh voldemort-vps "docker ps | grep voldemort-menu-bot"

# 2. Tail Voldemort Menu Bot Logs
ssh voldemort-vps "docker logs voldemort-menu-bot --tail 30 -f"

# 3. Check Hermes AI Assistant Gateway Service Status
ssh voldemort-vps "systemctl status hermes-gateway.service --no-pager"

# 4. Tail Hermes Gateway Logs
ssh voldemort-vps "tail -n 30 -f /home/voldemort/.hermes/logs/gateway.log"
```
