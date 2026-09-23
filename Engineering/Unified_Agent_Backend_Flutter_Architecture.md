---
tags:
  - engineering/architecture
  - backend/fastapi
  - mobile/flutter
  - agentic/sre
  - omniroute
title: "Unified Agent Backend & Flutter Client Architecture Blueprint"
created: 2026-09-20
status: approved
---

# Unified Agent Backend & Flutter Client Architecture Blueprint
> **System**: Headless Autonomous Agent Gateway & Multi-Platform SRE Workspace  
> **Status**: Approved Blueprint (Bullet-Proof, Anti-Memory Leak, Zero-Trust)  
> **Target Platforms**: Linux Host (Backend) + Flutter Mobile/Desktop (Client)  
> **Related Hubs**: [[Engineering/Index|Engineering Index]] | [[Engineering/OmniRoute|OmniRoute Hub]] | [[Engineering/Telegram_Bots_Architecture|Legacy Telegram Architecture]]

---

## 1. Executive Summary & Architectural Motivation

Sistem ini mentransisikan antarmuka operasional dari keterbatasan Telegram Bot API (rate limit, pembatasan 4.096 karakter, UI terbatas, dan rendering tabel yang rusak) menuju **Headless Asynchronous Agent Gateway** dengan antarmuka native **Flutter Client**.

Seluruh kapabilitas core eksisting tetap dipertahankan dan diperkuat:
- **LLM Routing & Load Balancing**: OmniRoute Engine (`http://127.0.0.1:20128/v1`).
- **Autonomous Reasoning & Tools**: Hermes Agent subprocess & Kilocode skills catalog.
- **Deterministic Tool Engines**: Cloudflare Flux.1 image generator, MarkItDown document parser, SRE telemetry & watchdog.
- **Execution Decoupling**: Menjamin eksekusi tugas SRE di background server tidak pernah terhenti meskipun aplikasi ponsel ditutup atau mengalami *network drop*.

---

## 2. High-Level Architecture (C4 Container View)

```
+-------------------------------------------------------------------------------+
|                    FLUTTER CLIENT (Android / iOS / Desktop)                   |
|  +---------------------+  +----------------------+  +----------------------+  |
|  | Chat / Stream View  |  | SRE Telemetry Drawer |  | Artifact Inspector   |  |
|  +---------------------+  +----------------------+  +----------------------+  |
|  | State: Riverpod (AutoDispose) | Local DB: Drift (SQLite) Virtualized UI|  |
+-------------------------------------------------------------------------------+
                                        ▲
                                        │ WSS (Sequence ACK + Ring Buffer)
                                        │ HTTPS (Payload Uploads & mTLS)
                                        ▼
+-------------------------------------------------------------------------------+
|                     PRIVATE OVERLAY MESH (Tailscale / WireGuard)               |
+-------------------------------------------------------------------------------+
                                        ▲
                                        │ Zero Public Exposure (100.x.x.x / 10.x)|
                                        ▼
+-------------------------------------------------------------------------------+
|                 UNIFIED HEADLESS BACKEND (FastAPI / AsyncIO)                  |
|  +-----------------------+  +---------------------+  +---------------------+  |
|  | Auth & ACL Guard      |  | Untrusted Data Wall |  | Ingress Rate Limiter|  |
|  +-----------------------+  +---------------------+  +---------------------+  |
|  | WSS Connection Hub    |  | Ring Buffer (Seq ID)|  | Task Broker (Worker)|  |
|  +-----------------------+  +---------------------+  +---------------------+  |
+-------------------------------------------------------------------------------+
         │                                       │                     │
         ▼                                       ▼                     ▼
+--------------------+                 +--------------------+ +-----------------+
| OmniRoute (Port    |                 | Task Storage /     | | External SRE &  |
| 20128)             |                 | State (SQLite)     | | Cloudflare APIS |
| - Failover Router  |                 | - Execution States | | - Flux.1 Schnell|
| - Token Telemetry  |                 | - Message History  | | - ntfy Push     |
+--------------------+                 +--------------------+ +-----------------+
```

---

## 3. Core Pillars: Robust, Bullet-Proof, and Anti-Memory-Leak

### Pillar 1: Transport Resilience (WebSocket Sequence ACK & Ring Buffer)
Koneksi jaringan mobile rentan terhadap *packet loss*, perpindahan BTS seluler, dan suspensi sistem operasi.
- **Frame Envelope Standard**: Setiap frame komunikasi memiliki nomor urut sekuensial (`seq_id`) dan `idempotency_key` (UUIDv7).
- **Server Ring Buffer**: Server memelihara ring buffer in-memory berkapasitas 100 frame terakhir per session ID (didukung persistence SQLite).
- **Zero-Drop Reconnection**:
  - Saat Flutter mendeteksi *disconnect*, koneksi WSS mencoba *exponential backoff reconnect*.
  - Handshake pertama pasca-reconnect mengirim: `{"event": "client.resume", "last_ack_seq_id": 42}`.
  - Server otomatis me-replay event `seq_id > 42` dari ring buffer tanpa mengulang komputasi prompt.
- **Heartbeat Contract**: Ping/Pong setiap 15 detik. Jika 2 interval (30s) terlewati tanpa respons, socket ditutup secara bersih dan dipersiapkan untuk siklus reconnect.

### Pillar 2: Strict Memory Hygiene & Backpressure Mitigation

#### Backend (FastAPI / Python Runtime)
- **Bounded Queues**: Seluruh antrean publisher internal dibatasi: `asyncio.Queue(maxsize=50)`.
- **Slow Consumer Throttling & Spooling**: Jika klien mengalami lag transmisi atau queue penuh:
  - Log output tidak lagi ditumpuk di RAM.
  - Server mengalihkan streaming log ke spooling disk file lokal (`/tmp/agent_spool/<session_id>.spool`).
  - Mengirim frame diskon: `{"event": "agent.spool_available", "file_url": "/api/v1/spool/..."}`.
- **Explicit Garbage Collection**:
  - Instance WebSocket disimpan dalam `WeakValueDictionary` untuk mencegah dangling references saat client putus secara tiba-tiba.
  - Task background yang tuntas memicu unbinding context dan membersihkan memory buffer.

#### Client (Flutter Application)
- **Virtualized Windowing**: Rendering chat dan terminal log wajib menggunakan `ListView.builder` dengan `cacheExtent` terbatas (maksimal 2 layar viewport).
- **Local Persistence Offloading**: Seluruh log dan pesan langsung di-flush ke database embedded lokal (**Drift** berbasis SQLite) secara asinkron. State UI hanya memegang *slice* pesan aktif (30-50 node), mencegah widget tree meledak.
- **Controller Lifecycle Discipline**: Seluruh `StreamSubscription`, `TextEditingController`, `ScrollController`, dan WebSocket channel diikat pada `ref.onDispose` di dalam Riverpod `AutoDisposeAsyncNotifier`.

### Pillar 3: Decoupled Headless Task Execution (Life-Cycle Isolation)
- **Independent Task Worker**: Eksekusi agent/SRE diperlakukan sebagai stateful job yang terdaftar pada tabel SQLite `agent_tasks`:
  ```sql
  CREATE TABLE agent_tasks (
      task_id TEXT PRIMARY KEY,
      session_id TEXT NOT NULL,
      status TEXT CHECK(status IN ('queued', 'running', 'completed', 'failed')),
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL
  );
  ```
- **Detach-Safe**: Pengguna dapat mematikan aplikasi Flutter kapan saja. Task tetap berjalan di server sampai tuntas.
- **Reattach-Friendly**: Kapan pun Flutter dibuka kembali, client cukup men-subscribe ulang `task_id` tersebut untuk membaca status final dan output terakumulasi.

### Pillar 4: Zero-Trust Security Perimeter
- **Zero Public Exposure**: Backend di-bind pada private interface Tailscale (`100.x.x.x`) atau WireGuard (`10.x.x.x`). Tidak ada port yang terbuka ke internet publik (`0.0.0.0`).
- **Device Attestation & JWT**: Setiap request wajib menyertakan token otentikasi dengan masa berlaku pendek (*short-lived*) dan *device signature*.
- **Untrusted Data Ingress Wall**: Seluruh payload dokumen, error log eksternal, atau input scraping diisolasi sebagai string pasif sebelum dilewatkan ke LLM client.

### Pillar 5: Out-of-Band Push Notification (ntfy / FCM)
- Ketika task di background selesai, atau terjadi anomali SRE saat aplikasi Flutter dalam kondisi tertutup (deep sleep), backend memicu notifikasi push instan melalui **ntfy** (self-hosted) atau **FCM** (data-only silent push) untuk memicu background fetch atau menampilkan banner peringatan di perangkat.

---

## 4. WebSocket Protocol Specifications

### Format Request Klien (Flutter -> Backend)
```json
{
  "seq_id": 1,
  "idempotency_key": "018e6e5a-381b-7a01-b1e1-8899aabbccdd",
  "event": "client.message.send",
  "payload": {
    "session_id": "sess_default_01",
    "prompt": "Investigasi performa disk dan bersihkan cache docker",
    "mode": "autonomous_sre"
  }
}
```

### Format Stream Event (Backend -> Flutter)
```json
{
  "seq_id": 104,
  "event": "agent.stream.chunk",
  "payload": {
    "session_id": "sess_default_01",
    "chunk": "Memeriksa kapasitas storage dengan `df -h`...\n",
    "timestamp": 1789977620
  }
}
```

### Format Lifecycle Event
```json
{
  "seq_id": 105,
  "event": "agent.execution.status",
  "payload": {
    "session_id": "sess_default_01",
    "state": "tool_executing",
    "details": "Executing: docker system prune -f"
  }
}
```

---

## 5. Implementation Directory Structure

```
/home/voldemort/services/unified-agent-backend/
├── docker-compose.yml          # Containerized deployment with memory/CPU limits
├── Dockerfile                  # Multi-stage lightweight Python 3.11 image
├── pyproject.toml              # Strict dependency lock (FastAPI, uvicorn, websockets, etc.)
├── config/
│   └── settings.py             # Environment & path configs
├── src/
│   ├── api/                    # HTTP & WebSocket endpoints
│   │   ├── deps.py             # Auth & rate-limiting guards
│   │   ├── routes_ws.py        # WSS connection manager & event dispatcher
│   │   └── routes_rest.py      # Artifacts, uploads, health probes
│   ├── core/                   # Shared business & SRE engines (Reused from existing)
│   │   ├── omniroute_client.py # LLM client via OmniRoute (port 20128)
│   │   ├── hermes_runner.py    # Subprocess execution bridge
│   │   ├── markitdown_ops.py   # Document transformation
│   │   └── security.py         # Untrusted data isolation & JWT
│   ├── orchestrator/           # Task queue & state machine
│   │   ├── ring_buffer.py      # Sequence ACK & resumption buffer
│   │   ├── task_broker.py      # Background worker pool
│   │   └── spooler.py          # Disk spooling for high-throughput logs
│   └── storage/
│       └── sqlite_store.py     # SQLite persistence for sessions & tasks
└── scripts/
    └── health_check.py         # SRE automated health probe
```

---

## 6. Execution & Rollout Roadmap

1. **Sprint 1: Core Backend Scaffold & Ring Buffer Engine**
   - Inisialisasi struktur direktori di `/home/voldemort/services/unified-agent-backend/`.
   - Implementasi `ring_buffer.py` dan `routes_ws.py` dengan protokol Sequence ACK.
   - Migrasi modul inti (`omniroute_client.py`, `markitdown_ops.py`, `hermes_runner.py`).

2. **Sprint 2: Task Decoupling & Memory Spooler**
   - Implementasi asynchronous task broker dengan state persistence SQLite.
   - Pengujian backpressure stream simulation (10.000 log lines) untuk memverifikasi zero memory leak pada server runtime.

3. **Sprint 3: Flutter Client Foundation**
   - Inisialisasi arsitektur Flutter (Riverpod + Drift SQLite).
   - Implementasi WebSocket client dengan auto-reconnect dan sequence ACK tracking.
   - Pembuatan widget streaming chat dan execution drawer bervirtualisasi.

4. **Sprint 4: End-to-End Hardening & Cutover**
   - Uji coba over Tailscale private network.
   - Integrasi push notification ntfy.
   - Graceful decommission pada service polling Telegram lama.
