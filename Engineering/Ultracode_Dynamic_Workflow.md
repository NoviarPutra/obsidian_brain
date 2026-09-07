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

2. **Ponytail Philosophy (Lazy Senior Dev)**:
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
│ Phase 1: Scout & Task Decomposition (Zero Direct Code) │
│ - Search & map scope boundaries (grep, glob, read)     │
│ - Emit structured JSON DAG tickets                     │
│ - Register tickets into todowrite                      │
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

## ⚙️ 5. Integrasi Konfigurasi Kilo (`kilo.json`)

Agent `⚡ Ultracode` didaftarkan secara global di `~/.config/kilo/kilo.json`:
- **Agent Name**: `ultracode` (Display: `⚡ Ultracode`, Color: `accent`, Mode: `all`).
- **Command Trigger**: `/ultracode <task>`.
- **Progress Tracking**: Real-time via `todowrite`.
- **Sub-Agent Execution**: Context-isolated via `task` tool (`explore` & `general`).
