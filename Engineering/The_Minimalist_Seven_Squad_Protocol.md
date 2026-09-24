---
tags:
  - architecture
  - multi-agent
  - orchestration
  - profiles
date: "2026-09-15"
---

# 🥋 The Minimalist Seven Squad & Profiles Architecture

> **SSOT Reference**: [[Worklogs/2026-09-15|Today's Worklog]] | [[Engineering/AGENTS|Engineering AGENTS]] | [[Engineering/Index|Engineering MOC]]

## 1. Squad Overview &  Profiles Mapping

To prevent context bloat, prompt drift, rate limit bottlenecks, race conditions, and memory leaks, the ecosystem is strictly partitioned into dedicated ** Profiles** under ``.

| Role | Profile Name | Core Focus | Curated Skills Scope |
| :--- | :--- | :--- | :--- |
| **Lead / Orchestrator** | `default` | Backlog decomposition, ticket delegation, user interaction. | Full orchestrator suite (`multi-agent-squad-orchestration`, `subagent-driven-development`) |
| **Builder / TDD Engineer** | `craft` | Red-Green-Refactor, bug patches, surgical minimal diffs. | `tdd`, `agentic-coding-discipline`, `ast-grep`, `implement`, `systematic-debugging` (19 skills) |
| **Scout / Researcher** | `lens` | Web scraping, docs parsing, grounded citations, schema reverse engineering. | `arxiv`, `research`, `community-forum-scraping`, `blocked-page-recovery`, `leadgen-prospector` (13 skills) |
| **Adversarial QA / Gatekeeper** | `veto` | Threat modeling, security scans, edge-case probing, YAGNI enforcement. | `requesting-code-review`, `smart-contract-security-recon`, `grill-me`, `design-audit` (10 skills) |
| **Infra & SRE Sentinel** | `sentinel` | Docker container lifecycle, system health, PostgreSQL/SQLite WAL, uptime. | `omniroute`, `rest-graphql-debug`, `systematic-debugging`, `inspecting--desktop-dom` (5 skills) |
| **Doc & Vault Scribe** | `draft` | Obsidian sync, daily worklog persistence, Google Workspace, document artifacts. | `obsidian`, `google-workspace`, `worklog`, `curriculum-module-generator`, `pdf`, `docx`, `xlsx` (15 skills) |
| **Systems Specialist / GODMODE** | `zero` | Low-level profiling, kernel/socket forensics, byte offsets, emergency escalations. | `python-debugpy`, `node-inspect-debugger`, `smart-contract-security-recon`, `diagnosing-bugs` (7 skills) |

> *Note on `sentinel`*: Profile name `root` is reserved by /OS system binary boundaries, so the SRE Sentinel is provisioned as `sentinel`.

## 2. Zero-Leak & High-Stability Guardrails

1. **Memory & Context Isolation**:
   - Each profile maintains isolated `memories/`, `sessions/`, and `workspace/` directories.
   - Context compression active (`threshold: 0.75`, `target_ratio: 0.2`, `protect_last_n: 30`).
   - SQLite journals locked to Write-Ahead Logging (`journal_mode: wal`) to prevent file lock contention and race conditions.

2. **Concurrency & Rate Limit Shielding**:
   - Subagent concurrency throttled (`delegation.max_concurrent_children: 2`).
   - Prompt caching enabled (`prompt_caching: cache_ttl: 5m`) against OmniRoute endpoint (`http://127.0.0.1:20128/v1`), caching system prompts and eliminating repeated token billing.
   - Loop guardrails enforced (`hard_stop_enabled: true`, max 5 idempotent cycles) to eliminate zombie infinite loops.

3. **No Boundary Overlap (Autonomous Dispatch Contract)**:
   - Communication follows the strict JSON relay specification documented in `references/autonomous-dispatch-contract.md`.
