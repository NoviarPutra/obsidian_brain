---
title: "Ultracode Dynamic Workflow Engine & Multi-Phase Orchestration"
tags:
  - ai/ultracode
  - ai/workflow
  - ai/orchestration
  - engineering/guidelines
  - kilo
date: 2026-09-07
updated: 2026-09-07
type: reference
---

# ⚡ Ultracode Dynamic Workflow Engine

> **Activation Scope**: Engine ini **HANYA** aktif jika user secara eksplisit memilih agent `⚡ Ultracode` atau mengeksekusi command `/ultracode`. Pada agent lain (`code`, `plan`, `ask`, `debug`, `orchestrator`), protokol ini **TIDAK AKAN** ter-trigger dan alur kerja berjalan normal sesuai mode masing-masing.

Dokumen arsitektur dan spesifikasi operasional untuk **Ultracode Dynamic Workflow Engine**. Protokol ini mengorkestrasi agen rekayasa perangkat lunak otonom (*autonomous engineering agent*) dengan disiplin tinggi menggunakan state machine 4-fase deterministik, dekomposisi task graf terarah (*Directed Acyclic Graph / DAG*), isolasi sub-agent, dan *adversarial dual-axis review*.

---

## 🎯 1. Prinsip Utama (Core Directives)

1. **Model-Agnostic Architecture**:
   - Protokol berjalan di atas model LLM apa pun (Claude, GPT, DeepSeek, Gemini, Qwen, local LLM).
   - Seluruh sub-agent mewarisi model session aktif secara dinamis (*dynamic model inheritance*).

2. **Large-Document Ingestion & Zero-Gap Comprehension**:
   - Mampu dan sanggup menelan 4-7+ dokumen markdown berukuran masif (2.000 hingga 20.000+ baris per file) secara terstruktur, detail, dan tanpa gap/kehilangan konteks (*lossless comprehension*).
   - **Trik Operasional**:
     - *Windowed Chunk Streaming*: Membaca file masif via tool `read` menggunakan `offset` dan `limit` berkala secara bertahap atau mengekstrak outline/heading terlebih dahulu.
     - *Parallel Context Ingestion*: Memanfaatkan parallel sub-agents (`task: explore` / `task: general`) untuk mencerna dokumen-dokumen secara independen lalu mensintesiskan *cross-document domain graph* & *truth matrix*.
     - *Exhaustive Cross-Referencing*: Memverifikasi referensi silang antar dokumen tanpa asumsi parsial atau halusinasi rangkuman pendek.

3. **Ponytail Philosophy (Lazy Senior Dev)**:
   - Zero unrequested abstractions, zero boilerplate, YAGNI, shortest working diffs.
   - Perbaikan bug selalu menargetkan *root cause* di fungsi bersama (*shared function*), bukan menambal gejala pada setiap pemanggil (*caller*).

3. **Adaptive Fast-Path**:
   - **Level 1 (Micro/Trivial)**: Typo, 1-line edit, single local CSS tweak -> *Direct execution*, bypass total pipeline DAG untuk efisiensi token dan latensi instan.
   - **Level 2+ (Non-Trivial / Standard / Epic)**: Wajib menjalankan 4-fase pipeline secara ketat.

4. **Circuit Breaker**:
   - Maksimal 2x retry loop pada Phase 3 (Adversarial Review). Jika setelah 2x perbaikan blocker belum teratasi, agent wajib berhenti dan mengekspos blocker spesifik ke user secara transparan.

---

## 🌀 2. State Machine 4-Fase Ultracode

```
┌────────────────────────────────────────────────────────┐
│ Phase 1: Scout, Large-Doc Ingestion & Decomposition    │
│ - Chunked/Parallel reading (2k-20k lines docs/codebase)│
│ - Search & map scope boundaries (grep, glob, read)     │
│ - Cross-document domain graph & truth matrix synthesis │
│ - Emit structured JSON DAG tickets & todowrite         │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Phase 2: Isolated Ticket Execution (TDD Loop)          │
│ - Context isolation via sub-agents (task: general)     │
│ - Red -> Green -> Refactor per ticket                  │
│ - Structured payload return (files, tests, diffs)      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Phase 3: Adversarial Dual-Axis Review                  │
│ - Axis 1: Standards, YAGNI, Clean Code                 │
│ - Axis 2: Spec Compliance, Breaking Changes, Callers   │
│ - Max 2 loops (Circuit Breaker)                        │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Phase 4: Final Synthesis & Verification                │
│ - Run workspace linters / test suites                  │
│ - Deliver consolidated changelog & touched files       │
└────────────────────────────────────────────────────────┘
```

---

## 📊 3. Format Spesifikasi Tiket DAG (Phase 1)

```json
{
  "workflow": "Refactor Authentication & Session Tokens",
  "tickets": [
    {
      "id": "TICKET-01",
      "title": "Migrate Token Storage to SecureStore",
      "scope_files": ["src/auth/tokenStorage.ts", "src/auth/__tests__/tokenStorage.test.ts"],
      "action": "MODIFY",
      "dependencies": [],
      "acceptance_criteria": [
        "TokenStorage encrypts payload before persisting",
        "Legacy getItem signature remains backward-compatible"
      ]
    }
  ]
}
```

---

## 🛡️ 4. Dual-Axis Adversarial Review Matrix (Phase 3)

| Sumbu Audit | Kriteria Verifikasi | Tindakan Jika Gagal |
| :--- | :--- | :--- |
| **Axis 1: Standards & Clean Code** | - Bebas dari abstraksi/helper yang tidak diminta (YAGNI).<br>- Tidak menambah dependency baru tanpa izin.<br>- Error handling & resource cleanup aman. | Re-scope ticket & hapus boilerplate. |
| **Axis 2: Spec Compliance & Regressions** | - Tidak ada breaking signature changes pada external callers.<br>- Edge cases (null/undefined, concurrency, timeouts) tertangani.<br>- Memenuhi 100% acceptance criteria Phase 1. | Re-open ticket bersangkutan untuk root-cause fix. |

---

## 📚 5. Protokol Pembacaan Dokumen Masif (Massive Document Ingestion Protocol)

Ketika berhadapan dengan 4-7+ dokumen markdown berukuran besar (2.000 s/d 20.000+ baris per file), agent Ultracode mengeksekusi strategi **Hierarchical Map-Reduce Ingestion** untuk menjamin pemahaman 100% tanpa celah (*zero gap*):

1. **Structural Table of Contents (TOC) & Section Boundary Scan**:
   - Menghindari *dumping* isi file secara membabi-buta ke context window utama.
   - Menggunakan `grep` untuk mengekstrak struktur heading (`#`, `##`, `###`) dan line numbers dari tiap file guna memetakan arsitektur dokumen.

2. **Windowed Offset-Limit Traversal**:
   - Membaca file masif per blok 2.000 baris menggunakan `read` (`offset=1, limit=2000`, `offset=2001, limit=2000`, dst.) secara sistematis atau menargetkan section yang relevan dengan presisi baris.

3. **Sub-Agent Fan-Out (Parallel Document Processing)**:
   - Mendelegasikan pembacaan dan analisis tiap file (atau potongan file besar) ke sub-agent independen via `task` (`explore` atau `general`).
   - Setiap sub-agent menghasilkan *Structured Extraction Payload*:
     - **Core Architecture & Invariants**: Aturan mutlak dan state machine.
     - **Entity & Glossary Mapping**: Entitas, model data, dan relasi.
     - **Actionable Requirements & Constraints**: Dependency graf, edge cases, cross-file references.
     - **Exact Line Citations**: Bookmark baris penting untuk deep reference.

4. **Cross-Document Fusion & Truth Matrix**:
   - Main agent menggabungkan output ekstraksi dari seluruh dokumen menjadi satu *Unified Knowledge Graph* dan *Truth Matrix*.
   - Mencegah kontradiksi antar dokumen dan memastikan tidak ada blind spot sebelum melangkah ke Phase 2 (Execution).

---

## ⚙️ 6. Integrasi Konfigurasi Kilo (`kilo.json`)

Agent `⚡ Ultracode` didaftarkan secara global di `~/.config/kilo/kilo.json`:
- **Agent Name**: `ultracode` (Display: `⚡ Ultracode`, Color: `accent`, Mode: `all`).
- **Command Trigger**: `/ultracode <task>`.
- **Progress Tracking**: Real-time via `todowrite`.
- **Sub-Agent Execution**: Context-isolated via `task` tool (`explore` & `general`).
