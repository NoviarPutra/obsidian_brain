---
title: "Voldemort Route — Architecture Blueprint (Robust, Bulletproof & Future-Proof)"
tags:
  - engineering/sre
  - architecture
  - voldemort-route
  - ai-gateway
  - blueprint
date: 2026-09-20
---

# ⚡ Voldemort Route — Architecture Blueprint
### *The Autonomous, High-Throughput, Bulletproof AI Gateway & Protocol Hub*

---

## 1. System Vision & Core Engineering Principles

**Voldemort Route** adalah generasi penyempurnaan dari *9Router* dan *OmniRoute*. Dirancang dengan paradigma **SRE-First**, **Zero Host Pollution**, dan **Industrial Minimalism**, Voldemort Route mengeliminasi kelemahan fundamental Next.js (memory overhead, event loop starvation, packaging bloat) dan menggantikannya dengan arsitektur modern berlatensi ultra-rendah.

### Prinsip Operasional:
1. **Single Binary Executable**: Dikompilasi menjadi satu binary mandiri via Bun (~35 MB) tanpa ketergantungan pada direktori `node_modules` di server target.
2. **Sub-40MB Memory Ceiling**: Mengonsumsi <40 MB RAM pada status idle dan <150 MB pada beban ribuan concurrent SSE streams.
3. **Zero-Allocation Streaming**: Menggunakan Web Streams API native (`TransformStream`) untuk transfer chunk SSE tanpa buffering middleware.
4. **Hardened Security & DLP**: Dilengkapi in-line scanner untuk mencegah kebocoran private keys, secret tokens, dan PII ke provider eksternal.
5. **Air-Gap Local LLM Resilience**: Mampu beroperasi 100% offline dengan auto-fallback ke inference runner lokal saat koneksi internet terputus total.

---

## 2. Technology Stack & Runtime Decisions

```
┌─────────────────────────────────────────────────────────────┐
│                    VOLDEMORT ROUTE CORE                     │
├───────────────────────────────┬─────────────────────────────┤
│ Component                     │ Technology Selection        │
├───────────────────────────────┼─────────────────────────────┤
│ Runtime Engine                │ Bun v1.2+ (JavaScript/TS)   │
│ HTTP & Routing Framework      │ Hono v4+ (Web Standards)    │
│ Embedded Control Plane UI     │ Svelte 5 (Runes) + Vite     │
│ In-Process Persistence        │ bun:sqlite (Native C engine)│
│ State Synchronization (Opt)   │ LiteFS / Raft Replication   │
│ Desktop Background Tray       │ Zero-Binary Native Runner   │
│ Transport Security & Egress   │ Native TLS + SOCKS5 Pooling │
└───────────────────────────────┴─────────────────────────────┘
```

### Mengapa Bun + Hono Menggantikan Next.js + Express?
- **Throughput & Latency**: Hono di atas Bun memproses request HTTP hingga 5x lebih cepat daripada Express/Next.js Route Handlers.
- **Native SQLite Performance**: `bun:sqlite` mengeksekusi query 3x lebih cepat dibanding `better-sqlite3` dan 15x dibanding `sql.js` tanpa kompilasi node-gyp.
- **Packaging Simplicity**: Frontend Svelte 5 dikompilasi menjadi single static bundle (<1.5 MB) dan di-embed langsung ke binary Hono via `serveStatic`.

---

## 3. Industrial Telemetry & Anti-AI-Slop Visual Identity

Dashboard Voldemort Route menolak estetika generic AI (neon purple/cyan glow, rounded cards 24px berlebih, glassmorphism buram, dan transisi lambat). Desain mengadopsi **Bauhaus Brutalism & Industrial Telemetry**:

- **Color Foundation**:
  - `Background Base`: `#090D10` (Deep Obsidian Void)
  - `Surface Panel`: `#0E141B` (Matte Industrial Slate)
  - `Border / Dividers`: `#1A232E` (1px Solid Sharp Borders)
  - `Text Primary`: `#F0F4F8` (High Contrast Crisp White)
  - `Text Muted`: `#64748B` (Technical Slate Grey)
- **Functional Status Accents**:
  - `Healthy / Route Active`: `#10B981` (Industrial Emerald)
  - `Throttled / Rate-Limited`: `#F59E0B` (Amber Core Alert)
  - `Offline / Circuit Open`: `#EF4444` (Crimson Critical)
  - `Compression Active`: `#3B82F6` (Cobalt Precision)
- **Typography & Grid**:
  - Font: `JetBrains Mono` / `Geist Mono` untuk seluruh metrik, tabel status, dan logs.
  - Layout: High-density modular grid (compact padding 8px/12px, zero wasted space).

---

## 4. Nine Core Architectural Subsystems

### Subsystem 1: Zero-Allocation Streaming Pipeline
- Mem-pipe upstream `ReadableStream` langsung ke downstream client melalui native `TransformStream`.
- Tanpa konversi `Buffer` atau manipulasi string pada body stream kecuali jika inspeksi kompresi diaktifkan.
- Latensi perantara (*proxy overhead*) di bawah **1.2 milidetik**.

### Subsystem 2: In-Line Semantic DLP & Secret Firewall
Sebelum payload diteruskan ke provider eksternal (OpenAI, Anthropic, Google, dll.), request dicegat oleh layer DLP:
1. **Entropy Scanner**: Menghitung Shannon Entropy string untuk mendeteksi token acak berkekuatan tinggi (API Keys, JWT, passwords).
2. **Signature Scrubber**: Regex biner untuk memblokir Private Keys (RSA, ED25519, OpenSSH, PEM blocks).
3. **PII Masking**: Masking otomatis terhadap alamat email, nomor telepon, dan identifier internal dengan placeholder terenkripsi.
4. **Action Policy**: Opsi `BLOCK` (mengembalikan status 400 ke client) atau `REDACT` (mengganti token sensitif sebelum diteruskan).

### Subsystem 3: Hardened Multi-Engine Compression Pipeline
Mengadopsi keunggulan kompresi OmniRoute dengan refaktorisasi modular:
- **RTK (RunTime Knowledge)**: Trimming output command terminal (`git diff`, directory trees, error stacktrace).
- **Caveman Engine (Lite / Full / Ultra)**: Pemotongan sintaksis dan redundansi gramatikal instruksi prompt.
- **Sentinel Code Locking**: Seluruh blok kode dikunci menggunakan token kriptografi `\u0000VR_SENTINEL:[ID]` sebelum kompresi berjalan, mencegah kerusakan indentasi dan sintaksis.
- **Honest Aggregate Inflation Guard**: Mengukur token input vs output. Jika hasil kompresi lebih besar dari teks asli (`compressedTokens > originalTokens`), pipeline otomatis melakukan rollback 100% ke teks asli.
- **Progressive Turn Aging**: 2-3 turn percakapan terakhir dijaga tanpa kompresi; turn lama dikompresi bertingkat.

### Subsystem 4: Resilient 20-Strategy Routing & Air-Gap Fallback
- **Universal Provider Catalog**: Mendukung 350+ provider dengan lazy-loaded schema.
- **Free-Tier Budget Ledger**: Engine kalkulasi kuota gratis bulanan dengan deduplikasi recurring pool keys.
- **State Machine Circuit Breaker**: Transisi status provider (Closed → Open → Half-Open) untuk mencegah antrean request pada upstream yang mati.
- **Air-Gap Local Fallback**: Ketika seluruh provider cloud gagal atau internet mati:
  ```
  Request ──▶ Cloud Providers Fail ──▶ Circuit Breaker Open
                                              │
                                              ▼
                             Auto-Fallback to Local Inference
                             (Ollama @ 127.0.0.1:11434 / vLLM)
  ```

### Subsystem 5: Multi-Agent Protocol Hub (MCP & A2A)
- **MCP Server over STDIO & SSE**: Kompatibel penuh dengan spesifikasi Anthropic MCP. Menjembatani tool execution ke Claude Code, Codex, dan Hermes Agent.
- **A2A (Agent-to-Agent) Task Engine**: Orkestrasi komunikasi antar-agent dengan verifikasi tanda tangan digital **HMAC-SHA256** untuk mencegah injeksi tugas dari pihak ketiga.
- **Agent Card Standard**: Menyediakan manifest `/.well-known/agent-card.json` untuk auto-discovery kapabilitas model.

### Subsystem 6: Scoped Virtual API Keys & Hard Budget Enforcer
- Membuat virtual keys untuk sub-agent atau client terpisah (misal: `vr-live-claude`, `vr-live-cursor`).
- **Hard Dollar Spend Cap**: Menetapkan alokasi anggaran bulanan (contoh: batas $10.00/bulan). Jika tercapai, rute terkunci otomatis.
- **Granular Restrictions**: Whitelist model tertentu, limit RPM/TPM independen, dan tagging proyek.

### Subsystem 7: High-Performance Database Engine (`bun:sqlite`)
- Mengeliminasi 114 tabel gamifikasi dan bloatware OmniRoute.
- Mengonsolidasikan arsitektur menjadi **22 tabel berkinerja tinggi**.
- Modus operasi: `WAL` (Write-Ahead Logging), `PRAGMA synchronous = NORMAL`, dan `PRAGMA busy_timeout = 5000`.
- Enkripsi kolom sensitif menggunakan **AES-256-GCM** berbasis master key `VR_STORAGE_KEY`.

### Subsystem 8: Desktop System Tray & One-Click Cloud Proxy Deployer
- **Zero-Binary Desktop Tray**: Script background terisolasi untuk mengontrol gateway dari taskbar tanpa memicu antivirus.
- **Cloud Egress Deployer**: Deployer otomatis worker proxy egress ke Cloudflare Workers dan Deno Deploy untuk membypass IP rate-limits.
- **Zero-Trust Tailscale Integration**: Registrasi native node ke private tailnet tanpa membuka port publik.

### Subsystem 9: SRE Disaster Recovery Suite & Health Probes
- Automated disaster recovery scripts terintegrasi (`vr-backup`, `vr-restore`, `vr-rollback`).
- Kubernetes / Docker Health Probes standar:
  - `/healthz`: Status integritas proses.
  - `/readyz`: Status koneksi database SQLite dan provider catalog.
  - `/livez`: Liveness check untuk container orchestrator.

---

## 5. Consolidated Database Schema (22 Core Tables)

```sql
-- 1. Metadata & Settings
CREATE TABLE IF NOT EXISTS system_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS global_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    category TEXT NOT NULL
);

-- 2. Providers & Nodes
CREATE TABLE IF NOT EXISTS providers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    base_url TEXT NOT NULL,
    api_type TEXT NOT NULL, -- 'openai', 'anthropic', 'gemini', etc.
    is_active INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 100
);

CREATE TABLE IF NOT EXISTS provider_credentials (
    id TEXT PRIMARY KEY,
    provider_id TEXT NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    account_label TEXT NOT NULL,
    encrypted_api_key TEXT NOT NULL, -- AES-256-GCM
    quota_limit_monthly REAL DEFAULT 0.0,
    current_month_usage REAL DEFAULT 0.0,
    is_rate_limited INTEGER DEFAULT 0,
    reset_at INTEGER,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS model_catalog (
    id TEXT PRIMARY KEY,
    provider_id TEXT NOT NULL REFERENCES providers(id),
    model_name TEXT NOT NULL,
    context_window INTEGER NOT NULL,
    input_cost_per_m REAL DEFAULT 0.0,
    output_cost_per_m REAL DEFAULT 0.0,
    is_free_tier INTEGER DEFAULT 0,
    capabilities TEXT NOT NULL -- JSON array: ["tools", "vision", "streaming"]
);

-- 3. Routing & Combos
CREATE TABLE IF NOT EXISTS routing_combos (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    strategy TEXT NOT NULL, -- 'cost', 'latency', 'fallback', 'round-robin'
    pipeline_definition TEXT NOT NULL, -- JSON array of target nodes
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS circuit_breakers (
    domain TEXT PRIMARY KEY,
    state TEXT NOT NULL DEFAULT 'CLOSED', -- 'CLOSED', 'OPEN', 'HALF_OPEN'
    failure_count INTEGER DEFAULT 0,
    last_failure_at INTEGER,
    cooldown_until INTEGER DEFAULT 0
);

-- 4. Scoped Virtual API Keys & Budgets
CREATE TABLE IF NOT EXISTS virtual_keys (
    key_hash TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    prefix TEXT NOT NULL,
    monthly_budget_usd REAL DEFAULT 0.0,
    current_spend_usd REAL DEFAULT 0.0,
    rpm_limit INTEGER DEFAULT 60,
    tpm_limit INTEGER DEFAULT 100000,
    allowed_models TEXT, -- JSON array or '*'
    is_active INTEGER DEFAULT 1,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS key_rate_limits (
    key_hash TEXT NOT NULL REFERENCES virtual_keys(key_hash) ON DELETE CASCADE,
    window_timestamp INTEGER NOT NULL,
    request_count INTEGER DEFAULT 0,
    token_count INTEGER DEFAULT 0,
    PRIMARY KEY(key_hash, window_timestamp)
);

-- 5. Context Compression & Rules
CREATE TABLE IF NOT EXISTS compression_profiles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    enable_rtk INTEGER DEFAULT 1,
    enable_caveman INTEGER DEFAULT 1,
    caveman_level TEXT DEFAULT 'full', -- 'lite', 'full', 'ultra'
    progressive_aging INTEGER DEFAULT 1,
    inflation_guard INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS compression_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    original_tokens INTEGER NOT NULL,
    compressed_tokens INTEGER NOT NULL,
    tokens_saved INTEGER NOT NULL,
    execution_time_ms REAL NOT NULL,
    engine_used TEXT NOT NULL
);

-- 6. Security, DLP & Audit
CREATE TABLE IF NOT EXISTS dlp_rules (
    id TEXT PRIMARY KEY,
    rule_type TEXT NOT NULL, -- 'entropy', 'regex', 'pii'
    pattern TEXT NOT NULL,
    action TEXT NOT NULL DEFAULT 'REDACT', -- 'REDACT', 'BLOCK', 'AUDIT'
    is_enabled INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS dlp_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    virtual_key_prefix TEXT NOT NULL,
    target_provider TEXT NOT NULL,
    rule_triggered TEXT NOT NULL,
    action_taken TEXT NOT NULL,
    excerpt TEXT NOT NULL
);

-- 7. Model Context Protocol (MCP) & Agent-to-Agent (A2A)
CREATE TABLE IF NOT EXISTS mcp_tools (
    id TEXT PRIMARY KEY,
    server_name TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    schema_json TEXT NOT NULL,
    is_enabled INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS mcp_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    execution_time_ms REAL NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS a2a_tasks (
    task_id TEXT PRIMARY KEY,
    origin_agent TEXT NOT NULL,
    target_agent TEXT NOT NULL,
    status TEXT NOT NULL, -- 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED'
    signature_hash TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    completed_at INTEGER
);

CREATE TABLE IF NOT EXISTS a2a_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES a2a_tasks(task_id) ON DELETE CASCADE,
    timestamp INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL
);

-- 8. Telemetry & Proxy Logs
CREATE TABLE IF NOT EXISTS call_logs (
    id TEXT PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    virtual_key_prefix TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_latency_ms REAL NOT NULL,
    ttft_ms REAL NOT NULL, -- Time to First Token
    status_code INTEGER NOT NULL,
    cost_usd REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS hourly_usage (
    hour_timestamp INTEGER NOT NULL,
    provider_id TEXT NOT NULL,
    total_requests INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_cost REAL DEFAULT 0.0,
    PRIMARY KEY(hour_timestamp, provider_id)
);

-- 9. Proxy Pools & Tunneling
CREATE TABLE IF NOT EXISTS proxy_pools (
    id TEXT PRIMARY KEY,
    protocol TEXT NOT NULL, -- 'socks5', 'http'
    address TEXT NOT NULL,
    auth_credentials TEXT,
    is_healthy INTEGER DEFAULT 1,
    latency_ms REAL DEFAULT 0.0,
    last_checked INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS deployed_cloud_workers (
    id TEXT PRIMARY KEY,
    platform TEXT NOT NULL, -- 'cloudflare', 'deno', 'vercel'
    endpoint_url TEXT NOT NULL,
    deployed_at INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE'
);
```

---

## 6. Declarative Configuration Spec (`voldemort-route.config.yaml`)

```yaml
version: "1.0"

server:
  host: "0.0.0.0"
  port: 20128
  mode: "production"
  trust_proxy: true
  max_body_size_mb: 32
  read_timeout_sec: 120

storage:
  driver: "sqlite"
  database_path: "/var/lib/voldemort-route/storage.sqlite"
  wal_mode: true
  encryption_key_env: "VR_STORAGE_KEY"

streaming:
  zero_allocation: true
  chunk_flush_interval_ms: 5
  max_concurrent_connections: 5000

compression:
  global_enabled: true
  rtk:
    enabled: true
    max_tool_output_tokens: 1500
  caveman:
    enabled: true
    default_intensity: "full"
  sentinel_code_lock: true
  honest_inflation_guard: true
  progressive_aging:
    enabled: true
    uncompressed_recent_turns: 3

security:
  dlp:
    enabled: true
    shannon_entropy_threshold: 4.5
    scan_private_keys: true
    mask_pii: true
    action_on_detection: "REDACT" # Options: REDACT | BLOCK | AUDIT
  rate_limiting:
    global_rpm: 600
    store: "memory"

routing:
  default_strategy: "cost-optimized-with-fallback"
  circuit_breaker:
    failure_threshold: 5
    cooldown_seconds: 30
  air_gap_local_fallback:
    enabled: true
    provider: "ollama"
    endpoint: "http://127.0.0.1:11434"
    model: "qwen2.5-coder:7b"
    timeout_sec: 60

protocols:
  mcp:
    enabled: true
    enable_stdio_bridge: true
    enable_sse_endpoint: true
  a2a:
    enabled: true
    require_hmac_signing: true
    secret_env: "VR_A2A_SECRET"

infrastructure:
  tailscale:
    enabled: false
    auth_key_env: "TS_AUTHKEY"
    hostname: "voldemort-route"
  desktop_tray:
    enabled: false
    start_minimized: true
```

---

## 7. Repository Layout & Project Structure

```
voldemort-route/
├── bin/
│   ├── voldemort-route.ts        # CLI entry point (Bun CLI executable)
│   ├── vr-backup.sh              # Automated SQLite snapshot script
│   ├── vr-restore.sh             # Disaster recovery restore script
│   └── vr-rollback.sh            # Version rollback automation
├── src/
│   ├── core/
│   │   ├── app.ts                # Hono server initialization & lifecycle
│   │   ├── pipeline.ts           # Interceptor chain: Auth -> DLP -> Cache -> Route
│   │   ├── stream.ts             # Zero-alloc SSE transform stream
│   │   └── errors.ts             # SRE structured error handling
│   ├── compression/
│   │   ├── index.ts              # Compression orchestrator
│   │   ├── rtk.ts                # Tool result pruner
│   │   ├── caveman.ts            # Syntactic reduction engine
│   │   ├── preservation.ts       # Sentinel code & markdown lock
│   │   └── guards.ts             # Honest aggregate inflation guard
│   ├── security/
│   │   ├── dlp.ts                # Data loss prevention interceptor
│   │   ├── entropy.ts            # High-speed Shannon entropy calculator
│   │   ├── crypto.ts             # AES-256-GCM column encryption
│   │   └── virtual_keys.ts       # Budget caps and token quotas
│   ├── routing/
│   │   ├── catalog/              # Static YAML definitions (350+ providers)
│   │   ├── strategies/           # 19 routing algorithms + Air-gap fallback
│   │   ├── circuit_breaker.ts    # Closed/Open/Half-Open state machine
│   │   └── proxy_pool.ts         # SOCKS5 egress manager & cloud deployer
│   ├── protocols/
│   │   ├── mcp/                  # Anthropic Model Context Protocol engine
│   │   └── a2a/                  # Agent-to-Agent HMAC task manager
│   ├── storage/
│   │   ├── db.ts                 # Native bun:sqlite client
│   │   ├── schema.sql            # 22-table database schema
│   │   └── migrations.ts         # Zero-downtime migration runner
│   └── ui/                       # Control plane dashboard (Svelte 5)
│       ├── src/
│       │   ├── components/       # Metric cards, route graph, telemetry
│       │   ├── routes/           # /dashboard, /providers, /keys, /dlp
│       │   └── app.html
│       ├── package.json
│       └── vite.config.ts
├── Dockerfile                    # Multi-stage ultra-lightweight distroless image
├── package.json
├── tsconfig.json
└── voldemort-route.config.yaml   # Default declarative configuration
```

---

## 8. Summary of Engineering Superiority

1. **Performance & Footprint**:
   - Memory idle: **<40 MB** (vs 350 MB di 9Router dan 480 MB di OmniRoute).
   - Binary size: **~35 MB single executable** (zero runtime dependencies).
   - Startup latency: **<15 milidetik** dari eksekusi hingga siap menerima traffic HTTP.
2. **Security & Data Integrity**:
   - Menjadi gateway AI pertama dengan **In-Line Semantic DLP Firewall** untuk mencegah kebocoran credentials.
   - Enkripsi database AES-256-GCM terintegrasi secara native.
3. **Resilience & Business Continuity**:
   - 100% immune terhadap pemadaman koneksi internet via **Air-Gap Local LLM Fallback**.
   - Dilengkapi **Honest Inflation Guard** untuk menjamin pengeluaran token tidak pernah membengkak akibat manipulasi konteks.
