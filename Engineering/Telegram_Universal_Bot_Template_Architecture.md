---
tags:
  - engineering/architecture
  - telegram
  - template
  - boilerplate
  - hermes
title: "🤖 Telegram Universal Bot & Hermes Agent Boilerplate Architecture"
---

# 🤖 Telegram Universal Bot & Hermes Agent Boilerplate Architecture

Production-grade, multi-mode, zero-bloat boilerplate specification for building modern Telegram Bots and Hermes Autonomous AI Agents.

---

## 🏛️ 1. Core Architectural Pillars

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TELEGRAM BOT CORE APPLICATION                      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        DYNAMIC MODE SWITCHER                          │  │
│  │   • BOT_MODE=menu     (Interactive button menus & utility tools)      │  │
│  │   • BOT_MODE=hermes   (Autonomous AI reasoning agent & tool loop)     │  │
│  │   • BOT_MODE=hybrid   (Menu UI + integrated "Ask Hermes AI" sub-agent)│  │
│  └──────────────────┬────────────────────────────────────┬───────────────┘  │
│                     │                                    │                  │
│                     ▼                                    ▼                  │
│  ┌──────────────────────────────────────┐    ┌───────────────────────────┐  │
│  │     3-TIER RBAC & ERROR RELAY        │    │  DROP-IN PLUGIN REGISTRY  │  │
│  │ • Owner / Admin / Whitelist / Guest  │    │ • Cloudflare FLUX.1 AI    │  │
│  │ • Sliding-window rate limiter        │    │ • Cloudflare R2 Storage   │  │
│  │ • Instant DM error traceback relay   │    │ • Microsoft MarkItDown    │  │
│  │                                      │    │ • System Telemetry Probe  │  │
│  └──────────────────┬───────────────────┘    └───────────┬───────────────┘  │
│                     │                                    │                  │
│                     ▼                                    ▼                  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     STORAGE & DUAL TRANSPORT LAYER                    │  │
│  │ • Storage: Zero-dependency Async SQLite (WAL Mode, crash resilient)   │  │
│  │ • Transport: Long Polling (Local Dev) ⟷ FastAPI Webhook (Production) │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 2. Boilerplate Directory Layout

```text
telegram-universal-bot-template/
├── src/
│   ├── config.py              # Strongly-typed Pydantic Settings
│   ├── main.py                # Application entrypoint & transport bootstrapper
│   ├── core/
│   │   ├── app.py             # Telegram app builder & message coordinator
│   │   ├── rbac.py            # @require_role('owner'|'admin'|'whitelist') & rate limiter
│   │   ├── error_relay.py     # Unhandled exception DM relay to Bot Owner
│   │   ├── storage.py         # Stdlib async SQLite WAL adapter (Zero dependencies)
│   │   └── llm_client.py      # Universal OpenAI / OmniRoute gateway adapter
│   ├── hermes/
│   │   ├── client.py          # Hermes Autonomous Agent client & reasoning extractor
│   │   └── prompt_builder.py  # System prompt & memory context assembler
│   ├── plugins/
│   │   ├── __init__.py        # Drop-in plugin registry (@register_plugin)
│   │   ├── cloudflare_flux.py # FLUX.1 Image synthesis & quota tracker
│   │   ├── cloudflare_r2.py   # Cloudflare R2 object storage uploader & telemetry
│   │   ├── markitdown_converter.py # Microsoft MarkItDown multi-format parser
│   │   └── system_telemetry.py # Host CPU/RAM, Dozzle, and Docker fleet stats
│   └── ui/
│       ├── keyboards.py       # Dynamic role-filtered inline keyboards
│       └── formatters.py      # Markdown fallback safe-senders & smart editors
├── scripts/
│   ├── init.sh                # Interactive CLI setup wizard
│   └── test_llm.py            # LLM gateway connectivity tester
├── tests/                     # Pytest automated test suite
├── Dockerfile                 # Multi-stage lean non-root image (UID 1000)
├── docker-compose.yml         # Production compose spec with resource caps
├── Makefile                   # Developer task automation
└── .env.example               # Documented configuration template
```

---

## ⚡ 3. Key Design Decisions

1. **Framework Choice**: Python 3.11+ with `python-telegram-bot` v21+ Async. Native compatibility with Hermes Agent core and Microsoft MarkItDown without foreign language bridges.
2. **Persistence**: Asynchronous SQLite WAL mode with zero third-party dependencies (`sqlite3` stdlib via `asyncio.to_thread`).
3. **RBAC Guardrails**: 3-tier hierarchy (`Owner` > `Admin` > `Whitelist` > `Guest`) with sliding-window rate limiters.
4. **DevEx**: Interactive setup wizard (`./scripts/init.sh`) generates valid configuration in under 60 seconds.
