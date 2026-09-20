---
tags:
  - engineering/mobile
  - flutter
  - client
  - omniroute
  - sprint3
title: "OmniRoute Flutter Client — Sprint 3 Plan & Specification"
created: 2026-09-20
status: ready_for_local_execution
---

# OmniRoute Flutter Client — Sprint 3 Plan & Specification

> **Target Platform**: Workstation / Local Machine (macOS, Android, iOS, Desktop)  
> **Backend Service**: `NoviarPutra/omniroute-agent-backend`  
> **Related Architecture**: [[Engineering/Unified_Agent_Backend_Flutter_Architecture|Unified Backend Architecture]] | [[Engineering/Index|Engineering Index]]

---

## 1. Strategi Eksekusi Non-Server

Sprint 3 ditujukan untuk dikerjakan langsung pada workstation pengembang lokal (laptop / macOS), bukan di server VPS. Hal ini dilakukan karena:
1. Flutter SDK, simulator iOS/Android, dan native GUI tools berjalan optimal pada lingkungan workstation lokal.
2. Server VPS tetap fokus bertindak sebagai backend headless SRE & Agent Gateway yang stabil.

---

## 2. Rangkuman Dokumen Panduan Klien

Spesifikasi lengkap, arsitektur modul, dependency `pubspec.yaml`, dan implementasi class `WebSocketService` (Sequence ACK & Resumption) telah disimpan di dalam repository backend:

* **Path Repository**: `docs/FLUTTER_CLIENT_SPEC.md`
* **URL GitHub**: [`NoviarPutra/omniroute-agent-backend/blob/main/docs/FLUTTER_CLIENT_SPEC.md`](https://github.com/NoviarPutra/omniroute-agent-backend/blob/main/docs/FLUTTER_CLIENT_SPEC.md)

---

## 3. Komponen Inti Sprint 3 yang Akan Diimplementasikan di Lokal

1. **Inisialisasi Project Flutter**:
   * Setup project `omniroute_client` dengan Clean Feature-First layout.
   * Konfigurasi Riverpod + Code Generation (`build_runner`).

2. **Network & Protocol Engine**:
   * Integrasi `web_socket_channel` dengan protokol typed JSON frame.
   * Mekanisme **Sequence ACK & Resumption**: mengirim `last_ack_seq_id` saat reconnect agar tidak ada token atau log yang hilang.
   * Heartbeat Ping/Pong otomatis (interval 15 detik).
   * Rest Client via `Dio` dengan automatic JWT Bearer injection & refresh.

3. **Anti-Memory Leak & Storage**:
   * Virtualized rendering chat stream menggunakan `ListView.builder` + `cacheExtent: 300`.
   * Embedded local database (**Drift** SQLite) untuk menyimpan riwayat chat dan log, menjaga heap memory Flutter tetap di bawah 80 MB.
   * Lifecycle cleanup otomatis via `ref.onDispose`.

4. **UI Components & Workspace**:
   * `MessageBubble` dengan Markdown formatting dan syntax highlighting.
   * `CodeBlockViewer` dengan tombol 1-tap copy.
   * `SRETelemetryDrawer` untuk memantau CPU, RAM, Disk, dan status container secara live.
   * `ArtifactPreviewCard` untuk menampilkan gambar Cloudflare Flux dan dokumen yang diekstraksi MarkItDown.

---

## 4. Konektivitas & Zero-Trust Access

* Workstation lokal terhubung ke VPS melalui **Tailscale mesh network**.
* Flutter Client mengarahkan traffic ke IP Tailscale VPS:
  * REST API: `http://100.x.x.x:8088/api/v1`
  * WebSocket: `ws://100.x.x.x:8088/ws`
* Tidak ada port yang dibuka ke internet publik.
