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

**Voldemort Route** adalah sistem AI gateway generasi baru yang menyatukan dan menyempurnakan kapabilitas **9Router** dan **OmniRoute**. Dirancang dengan standar **SRE-First**, **Zero Host Pollution**, dan **Industrial Minimalism**, Voldemort Route mengeliminasi kelemahan fundamental arsitektur monolitik Next.js (memory overhead, event loop starvation, packaging bloat) dan menggantikannya dengan pipeline berlatensi ultra-rendah.

### Prinsip Operasional Inti:
1. **Single Binary Executable**: Dikompilasi menjadi satu binary mandiri via Bun (~35 MB) tanpa ketergantungan pada direktori `node_modules` pada host target.
2. **Sub-40MB Memory Ceiling**: Mengonsumsi <40 MB RAM saat idle dan <150 MB pada beban ribuan concurrent Server-Sent Events (SSE) streams.
3. **Zero-Allocation Streaming**: Menggunakan Web Streams API native (`TransformStream`) untuk transfer chunk data tanpa buffering middleware Express.
4. **Hardened Security & Semantic DLP**: In-line firewall untuk mendeteksi dan memblokir kebocoran private keys, secret tokens, dan PII ke provider eksternal.
5. **Air-Gap Local LLM Resilience**: Mampu beroperasi 100% offline dengan auto-fallback otonom ke inference runner lokal saat koneksi internet terputus total.
6. **Cache-Aware Token Compression**: Melakukan kompresi konteks tanpa merusak prefix KV cache milik provider (Anthropic, DeepSeek, OpenAI).
7. **Universal Protocol Translation**: Klien dapat mengirim format apa pun (Anthropic Messages, OpenAI Chat, Google Gemini Content) dan router otomatis menerjemahkannya ke format target provider secara transparan.

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
│ Protocol Bridge (Cross-API)   │ Universal Dialect Adapter   │
└───────────────────────────────┴─────────────────────────────┘
```

---

## 3. Industrial Telemetry & Anti-AI-Slop Visual Identity

Dashboard Voldemort Route menolak estetika generic AI (warna ungu/cyan neon, sudut membulat 24px berlebih, blur glassmorphism, dan transisi lambat). Desain mengadopsi **Bauhaus Brutalism & Industrial Telemetry** (Spesifikasi lengkap terdokumentasi di [[Engineering/Voldemort_Route_Design_System]]):

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
  - Layout: High-density modular grid (compact padding 8px/12px, zero visual filler).

---

## 4. Twelve Battle-Hardened Subsystems

### Subsystem 1: Zero-Allocation Streaming Pipeline & Anti-Timeout Heartbeat
- Mem-pipe upstream `ReadableStream` langsung ke downstream client melalui native `TransformStream`.
- **Reasoning Keep-Alive Heartbeat**: Untuk model penalaran berdurasi panjang (DeepSeek-R1, o1, o3-mini) yang membutuhkan 30–90 detik sebelum mengeluarkan token pertama, router memancarkan komentar SSE `: keep-alive\n\n` setiap 15 detik. Hal ini mencegah putusnya koneksi akibat timeout 504 di reverse proxy (Cloudflare/Nginx).
- Overhead latensi proxy internal di bawah **1.2 milidetik**.

### Subsystem 2: Universal Bidirectional Dialect Adapter
Menjembatani perbedaan format API antara client coding tools dan model tujuan secara transparan:
- **Anthropic Messages** (`/v1/messages` dari Claude Code) ⇄ **OpenAI Chat** (`/v1/chat/completions`).
- **OpenAI Responses / Codex** (`/responses`) ⇄ **Anthropic / DeepSeek**.
- **Google Gemini Content** (`/v1beta/models/...:generateContent`) ⇄ **OpenAI / Claude**.
- Mendukung konversi skema *tool calls / function calling*, *system prompt instructions*, dan *thinking blocks*.

### Subsystem 3: In-Line Semantic DLP & Secret Firewall
Sebelum payload diteruskan ke provider publik eksternal, request melewati firewall DLP:
1. **Entropy Scanner**: Menghitung Shannon Entropy string untuk mendeteksi token acak (API keys, JWT, passwords).
2. **Signature Scrubber**: Regex deterministik untuk mendeteksi Private Keys (RSA, ED25519, OpenSSH, PEM blocks).
3. **PII Masking**: Masking otomatis terhadap alamat email, nomor telepon, dan data sensitif dengan placeholder kriptografi.
4. **Action Policy**: Opsi `BLOCK` (mengembalikan HTTP 400 ke client) atau `REDACT` (mengganti secret dengan sentinel aman).

### Subsystem 4: Cache-Aware Multi-Engine Compression
Mengadopsi keunggulan kompresi OmniRoute dengan optimasi kompatibilitas cache:
- **RTK (RunTime Knowledge)**: Trimming output command CLI (`git diff`, `ls -R`, compiler stacktrace).
- **Caveman Engine (Lite / Full / Ultra)**: Pemotongan sintaksis dan redundansi gramatikal instruksi.
- **Sentinel Code Locking**: Blok kode dikunci dengan token kriptografi `\u0000VR_SENTINEL:[ID]` sebelum manipulasi teks berjalan, menjamin integritas sintaksis 100%.
- **Cache-Aware Prefix Lock**: **Mencegah invalidasi provider-side KV prompt caching** (Anthropic prompt cache discount 90%, DeepSeek context cache). Prompt prefix sistem dan tools definition dijaga statis, kompresi hanya menyasar riwayat percakapan dinamis.
- **Honest Aggregate Inflation Guard**: Mengukur token input vs output. Jika hasil kompresi lebih besar dari teks asli (`compressedTokens > originalTokens`), sistem otomatis rollback ke payload original.
- **Progressive Turn Aging**: 2-3 giliran percakapan terakhir dibiarkan utuh tanpa kompresi; turn lama dikompresi bertingkat.

### Subsystem 5: Resilient 20-Strategy Routing & Air-Gap Fallback
- **Universal Provider Catalog**: Mendukung 350+ provider dengan katalog statis YAML yang di-*lazy-load*.
- **Free-Tier Budget Ledger**: Engine kalkulasi kuota gratis bulanan dengan deduplikasi recurring pool keys.
- **State Machine Circuit Breaker**: Transisi status provider (Closed → Open → Half-Open) untuk mengisolasi kegagalan upstream.
- **Air-Gap Local Fallback**: Ketika seluruh provider cloud gagal atau koneksi internet mati:
  ```
  Client Request ──▶ Cloud Providers Fail ──▶ Circuit Breaker Open
                                                      │
                                                      ▼
                                     Auto-Fallback to Local Inference
                                     (Ollama @ 127.0.0.1:11434 / vLLM)
  ```

### Subsystem 6: Autonomous OAuth Lifecycle & Token Refresher Worker
Banyak provider gratis/murah (seperti Cursor, Kiro, Grok CLI, Google AI Studio) menggunakan OAuth JWT dengan masa kedaluwarsa pendek (15–60 menit):
- Daemon latar belakang otomatis memeriksa `token_expires_at` pada tabel kredensial.
- Melakukan rotasi dan request refresh token baru 5 menit sebelum token expired tanpa interupsi request user.
- Mengisolasi kredensial multi-akun dengan auto-retry jika sebuah akun terkena ban/exhaustion.

### Subsystem 7: In-Flight Concurrency Leases & Leaky-Bucket Queueing
Mencegah error HTTP 429 (Rate Limit Exceeded) akibat lonjakan request konkuren dari banyak agent:
- Menggunakan tabel `concurrency_leases` dan antrean leaky-bucket di memori.
- Jika sebuah akun provider memiliki batas maksimum 5 RPM, request ke-6 tidak langsung ditolak dengan status 429, melainkan di-*queue* dalam waktu terukur (backpressure queue) hingga slot sewa (*lease*) tersedia.

### Subsystem 8: Model Context Protocol (MCP) & A2A Orchestration
- **MCP Server over STDIO & SSE**: Kompatibel 100% dengan spesifikasi Anthropic MCP. Menjembatani tool execution ke Claude Code, Codex, dan Hermes Agent.
- **A2A (Agent-to-Agent) Task Engine**: Orkestrasi komunikasi antar-agent dengan verifikasi tanda tangan digital **HMAC-SHA256** untuk mencegah unauthorized task injection.
- **Agent Card Standard**: Manifest `/.well-known/agent-card.json` untuk auto-discovery kemampuan model.

### Subsystem 9: Scoped Virtual API Keys & Hard Budget Enforcer
- Membuat downstream virtual keys terisolasi (contoh: `vr-live-claude`, `vr-live-cursor`).
- **Hard Dollar Spend Cap**: Menetapkan alokasi anggaran bulanan (contoh: batas $10.00/bulan). Jika tercapai, rute terkunci otomatis.
- **Granular Restrictions**: Whitelist model tertentu, limit RPM/TPM independen, dan tagging proyek.

### Subsystem 10: High-Performance Database Engine (`bun:sqlite`)
- Mengeliminasi 114 tabel gamifikasi dan bloatware OmniRoute.
- Mengonsolidasikan arsitektur menjadi **24 tabel berkinerja tinggi**.
- Modus operasi: `WAL` (Write-Ahead Logging), `PRAGMA synchronous = NORMAL`, dan `PRAGMA busy_timeout = 5000`.
- Enkripsi kolom kredensial menggunakan **AES-256-GCM** berbasis master key `VR_STORAGE_KEY`.

### Subsystem 11: Desktop System Tray & One-Click Cloud Proxy Deployer
- **Zero-Binary Desktop Tray**: Script background terisolasi untuk mengontrol gateway dari taskbar tanpa memicu antivirus.
- **Cloud Egress Deployer**: Deployer otomatis worker proxy egress ke Cloudflare Workers dan Deno Deploy untuk membypass IP rate-limits.
- **Zero-Trust Tailscale Integration**: Registrasi native node ke private tailnet tanpa membuka port publik.

### Subsystem 12: SRE Disaster Recovery Suite & Health Probes
- Automated disaster recovery scripts terintegrasi (`vr-backup`, `vr-restore`, `vr-rollback`).
- Dynamic Catalog Sync: Pembaruan berkala metadata harga dan model provider secara otomatis.
- Kubernetes / Docker Health Probes standar:
  - `/healthz`: Integritas proses gateway.
  - `/readyz`: Kesiapan koneksi SQLite dan provider catalog.
  - `/livez`: Liveness probe untuk container orchestrator.

---

## 5. Consolidated Database Schema (24 Core Tables)

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

-- 2. Providers & Credential Management
CREATE TABLE IF NOT EXISTS providers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    base_url TEXT NOT NULL,
    api_type TEXT NOT NULL, -- 'openai', 'anthropic', 'gemini'
    is_active INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 100
);

CREATE TABLE IF NOT EXISTS provider_credentials (
    id TEXT PRIMARY KEY,
    provider_id TEXT NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    account_label TEXT NOT NULL,
    auth_type TEXT NOT NULL DEFAULT 'api_key', -- 'api_key', 'oauth', 'jwt'
    encrypted_api_key TEXT NOT NULL, -- AES-256-GCM
    encrypted_refresh_token TEXT,
    token_expires_at INTEGER,
    token_refresh_url TEXT,
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
    supports_prompt_cache INTEGER DEFAULT 0,
    is_free_tier INTEGER DEFAULT 0,
    capabilities TEXT NOT NULL -- JSON array: ["tools", "vision", "streaming"]
);

-- 3. Routing, Combos & Circuit Breakers
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

CREATE TABLE IF NOT EXISTS concurrency_leases (
    credential_id TEXT PRIMARY KEY REFERENCES provider_credentials(id) ON DELETE CASCADE,
    max_concurrent INTEGER NOT NULL DEFAULT 2,
    active_leases INTEGER NOT NULL DEFAULT 0,
    last_leased_at INTEGER NOT NULL
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

-- 5. Context Compression & Cache Awareness
CREATE TABLE IF NOT EXISTS compression_profiles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    enable_rtk INTEGER DEFAULT 1,
    enable_caveman INTEGER DEFAULT 1,
    caveman_level TEXT DEFAULT 'full', -- 'lite', 'full', 'ultra'
    cache_aware_prefix_lock INTEGER DEFAULT 1, -- Preserves provider prompt caching
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

-- 7. Protocol Translation & Dialect Mappings
CREATE TABLE IF NOT EXISTS dialect_transforms (
    client_dialect TEXT NOT NULL, -- 'anthropic_messages', 'openai_chat', 'gemini_content'
    target_dialect TEXT NOT NULL,
    transform_rules TEXT NOT NULL, -- JSON config for field mapping
    PRIMARY KEY(client_dialect, target_dialect)
);

-- 8. Model Context Protocol (MCP) & Agent-to-Agent (A2A)
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

-- 9. Telemetry & Proxy Logs
CREATE TABLE IF NOT EXISTS call_logs (
    id TEXT PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    virtual_key_prefix TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    cached_tokens INTEGER DEFAULT 0,
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

-- 10. Proxy Pools & Cloud Deployments
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
  reasoning_heartbeat_interval_ms: 15000 # Prevents Cloudflare 504 during o1/R1 reasoning

compression:
  global_enabled: true
  rtk:
    enabled: true
    max_tool_output_tokens: 1500
  caveman:
    enabled: true
    default_intensity: "full"
  sentinel_code_lock: true
  cache_aware_prefix_lock: true # Protects Anthropic/DeepSeek prompt caching
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
    queue_excess_requests: true # Leaky-bucket queue instead of instant 429
    max_queue_wait_ms: 5000

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
  universal_dialect_adapter:
    enabled: true
    auto_translate_messages_to_chat: true
  oauth_worker:
    auto_refresh_enabled: true
    refresh_window_sec: 300 # Refresh 5 mins before expiry
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
│   ├── voldemort-route.ts        # CLI executable (Bun native single binary)
│   ├── vr-backup.sh              # SRE automated snapshot script
│   ├── vr-restore.sh             # Disaster recovery restore script
│   └── vr-rollback.sh            # One-step version rollback
├── src/
│   ├── core/
│   │   ├── app.ts                # Hono server initialization & lifecycle
│   │   ├── stream.ts             # Zero-alloc SSE stream & reasoning heartbeat
│   │   ├── pipeline.ts           # Interceptor chain: Auth -> DLP -> Cache -> Route
│   │   ├── dialects/             # Universal API Dialect Translators (Messages <-> Chat)
│   │   └── errors.ts             # SRE structured error handling
│   ├── compression/
│   │   ├── index.ts              # Compression orchestrator
│   │   ├── rtk.ts                # Tool result pruner
│   │   ├── caveman.ts            # Syntactic reduction engine
│   │   ├── preservation.ts       # Sentinel code & markdown lock (\u0000VR_SENTINEL)
│   │   ├── cache_lock.ts         # Prompt prefix cache protector
│   │   └── guards.ts             # Honest aggregate inflation guard
│   ├── security/
│   │   ├── dlp.ts                # Data loss prevention interceptor
│   │   ├── entropy.ts            # High-speed Shannon entropy calculator
│   │   ├── crypto.ts             # AES-256-GCM column encryption
│   │   └── virtual_keys.ts       # Scoped budget caps & rate limiters
│   ├── routing/
│   │   ├── catalog/              # Static YAML definitions (350+ providers)
│   │   ├── strategies/           # 19 routing algorithms + Air-gap fallback
│   │   ├── circuit_breaker.ts    # Closed/Open/Half-Open state machine
│   │   ├── queue.ts              # In-flight concurrency leases & leaky-bucket
│   │   └── proxy_pool.ts         # SOCKS5 egress manager & cloud deployer
│   ├── workers/
│   │   ├── oauth_refresher.ts    # Background JWT/OAuth rotation daemon
│   │   └── catalog_sync.ts       # Dynamic pricing & model sync scheduler
│   ├── protocols/
│   │   ├── mcp/                  # Anthropic Model Context Protocol engine
│   │   └── a2a/                  # Agent-to-Agent HMAC task manager
│   ├── storage/
│   │   ├── db.ts                 # Native bun:sqlite client (WAL mode)
│   │   ├── schema.sql            # 24-table consolidated schema
│   │   └── migrations.ts         # Zero-downtime migration runner
│   └── ui/                       # Control plane dashboard (Svelte 5 + Vite SPA)
│       ├── src/components/       # Industrial telemetry & Bauhaus brutalism
│       └── vite.config.ts
├── Dockerfile                    # Multi-stage distroless container (<40MB)
├── package.json
├── tsconfig.json
└── voldemort-route.config.yaml   # Default declarative configuration
```

---

## 8. Summary of Engineering Superiority

1. **Throughput & Memory Efficiency**:
   - Memory idle: **<40 MB** (vs 350 MB di 9Router dan 480 MB di OmniRoute).
   - Binary size: **~35 MB single executable** (zero node_modules on target server).
   - Sub-millisecond stream forwarding dengan zero memory allocation.
2. **Hardened Security & DLP**:
   - In-Line Semantic DLP Firewall untuk memblokir kebocoran credentials ke API eksternal.
   - Enkripsi native AES-256-GCM untuk kolom kredensial sensitif.
3. **Bulletproof SRE Resilience**:
   - **Anti-Timeout Heartbeat**: Mengeliminasi error 504 Gateway Timeout pada model penalaran (R1/o1).
   - **Cache-Aware Compression**: Melindungi efisiensi biaya diskon prompt cache provider (90% savings).
   - **Air-Gap Local LLM Fallback**: Beroperasi 100% tanpa downtime bahkan saat koneksi internet terputus total.
   - **Autonomous OAuth Lifecycle**: Menghilangkan error autentikasi akibat expired JWT tokens pada provider gratis.
