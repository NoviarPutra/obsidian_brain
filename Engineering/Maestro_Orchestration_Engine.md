---
title: "Maestro Multi-Agent Orchestration Engine & Squad Matrix"
tags:
  - ai/maestro
  - ai/orchestration
  - ai/multi-agent
  - engineering/guidelines
  - kilo
date: 2026-09-07
updated: 2026-09-11
type: reference
---

# 🎭 Maestro Multi-Agent Orchestration Engine

> **Related Hubs**: [[Engineering/Index|⚡ Engineering MOC]] | [[MattPocock_Skills_Workflow|🛠️ Matt Pocock Workflow]] | [[OmniRoute_Communication_Style|💬 OmniRoute Persona]] | [[Home|🌌 Home]]

> **Activation Scope**: Engine ini aktif saat menggunakan agent `🎭 Maestro` atau subagent squad (`scout`, `builder`, `reviewer`, `devops`). Maestro bertindak sebagai Chief Tech Lead & Orchestrator yang mengarahkan squad agent spesialis.

Dokumen arsitektur dan spesifikasi operasional untuk **Maestro Multi-Agent Orchestration Engine**. Protokol ini mengorkestrasi squad agen rekayasa perangkat lunak otonom (*autonomous engineering squad*) dengan pembagian peran, tools, kewenangan, dan quality gate yang sangat terisolasi dan disiplin.

---

## 🏛️ Squad Matrix & Exclusive Responsibilities

```
                                ┌──────────────────────────────────────────────────────────┐
                                │                  🎭 MAESTRO (THE BOSS)                   │
                                │   High-Leverage Tech Lead, DAG Router & Synthesizer      │
                                └────────────────────────────┬─────────────────────────────┘
                                                             │
                 ┌───────────────────┬───────────────────────┼───────────────────────┐
                 │                   │                       │                       │
                 ▼                   ▼                       ▼                       ▼
          🔍 SCOUT            ⚡ BUILDER              ⚖️ REVIEWER             🛠️ DEVOPS
     (Discovery & Specs)   (TDD Implementation)    (Adversarial QA)      (VPS & Remote SRE)
```

| Agent | Focus & Specialization | Allowed Tools | Restricted Tools | Autonomous Decision |
| :--- | :--- | :--- | :--- | :--- |
| **🎭 `maestro`** | Chief Architect, DAG Routing, Quality Gates | `task`, `todowrite`, `read`, `glob`, `grep`, `webfetch`, `question` | Dilarang raw code implementation | Menentukan DAG tickets, flow, Circuit Breaker |
| **🔍 `scout`** | Code exploration, caller tracing, large docs | `read`, `glob`, `grep`, `webfetch`, `skill`, `kilo_local_recall` | Strict READ-ONLY (`edit`, `write`, `bash` forbidden) | AST boundary mapping, Unified Truth Matrix. Proactive Read-Only Skills: `codebase-design`, `improve-codebase-architecture`, `domain-modeling`, `research`, `kilo-config`, `find-skills`. |
| **⚡ `builder`** | Isolated ticket TDD, root-cause bug fixing | `read`, `edit`, `write`, `glob`, `grep`, `bash` (test runner), `skill`, `todowrite` | Dilarang `ssh`, dilarang modif VPS | Ponytail minimal diff, Red-Green-Refactor. Proactive Skills: `tdd`, `implement`, `implement-spec`, `diagnosing-bugs`, `resolving-merge-conflicts`, `ui-styling`, `shadcn`, `migrate-radix-to-base`, `migrate-to-shoehorn`. |
| **⚖️ `reviewer`** | Dual-axis review, static audit, regression guard | `read`, `glob`, `grep`, `bash` (linter/test runner), `skill`, `kilo_local_recall` | Strict AUDITOR (`edit`, `write` forbidden) | Autonomous **PASS** / **REJECT** verdict with blockers. Proactive Skills: `code-review`, `design-audit`, `desktop-principles`, `mobile-principles`, `retro`. |
| **🛠️ `devops`** | Remote VPS (`voldemort-vps`), Docker, Reverse Proxy | `bash` (SSH), `read`, `edit`, `write`, `todowrite`, MCP tools | Exclusive VPS authorization | Zero-host-pollution, backup before touch, safe deploy |

---

## 🌀 The 4-Phase Orchestration Pipeline

### Phase 1: Scout, Reconnaissance & DAG Decomposition
1. **Intel Gathering**: Maestro mengutus `scout` untuk mapping boundaries, AST callers, dan membaca multi-file specs masif (2k-20k lines).
2. **Unified Truth Matrix**: Scout mensintesis temuan, dependensi, dan edge cases tanpa menyentuh file code.
3. **Execution DAG**: Maestro memecah problem jadi tiket-tiket terisolasi dan mendaftarkannya di `todowrite`.

### Phase 2: Isolated Ticket Execution (Builder)
1. **Context Isolation**: Maestro mendelegasikan tiap tiket ke `builder` (backend/frontend logic).
2. **TDD Cycle**: Builder menerapkan Red-Green-Refactor dengan prinsip Ponytail (Lazy Senior Dev) — shortest working diff wins.
3. **Structured Return**: Subagent mengembalikan laporan perubahan file dan test assertion yang lulus.

### Phase 3: Adversarial Dual-Axis Review (Reviewer)
1. **Axis 1 (Standards & Clean Code)**: YAGNI, no unrequested abstractions, zero bloat, robust error handling.
2. **Axis 2 (Spec Compliance & Regression Guard)**: Backward compatibility, 100% spec coverage, zero broken callers.
3. **Circuit Breaker**: Maksimal 2 kali perbaikan retry loop jika Reviewer memberi status `REJECT`. Jika belum lolos, eskalasi langsung ke user.

### Phase 4: Final Synthesis, Verification & Worklog
1. **Workspace Verification**: Eksekusi workspace linter dan full test suites.
2. **Remote Deployment**: Jika melibatkan VPS, delegasikan ke agent `devops`.
3. **Autonomous Worklog Persistence**: Otomatis simpan ringkasan milestone ke `/Users/pt-dika/Documents/Obsidian/Worklogs/YYYY-MM-DD.md`.
4. **Final Deliverable**: Kirim ringkasan teknis bersih dan to-the-point ke user.
