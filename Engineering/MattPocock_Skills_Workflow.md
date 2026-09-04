---
title: "Matt Pocock Skills & Autonomous AI Flow Engine"
tags:
  - ai/skills
  - ai/workflow
  - engineering/guidelines
  - matt-pocock
date: 2026-09-05
updated: 2026-09-05
type: reference
---

# 🛠️ Matt Pocock Engineering Skills & Autonomous AI Flow

Panduan arsitektur dan operasional seluruh skill rekayasa perangkat lunak Matt Pocock untuk agen AI (Kilo / Claude Code). Dokumen ini berfungsi sebagai **single source of truth** bagi agen AI agar dapat menentukan rute kerja, mengeksekusi skill secara otonom, dan memverifikasi ketersediaan dependensi tanpa overengineering.

---

## 🎯 1. Autonomous Agent Directives (Aturan Eksekusi Mandiri)

Agen AI yang membaca dokumen ini **wajib** mematuhi 4 pilar operasional berikut:

1. **Auto-Trigger Cerdas**: Kenali intensi dan bobot tugas user secara otomatis. Jangan menunggu user memanggil `/nama-skill` manual.
2. **Anti-Overengineering (Prinsip YAGNI & Senior Dev)**:
   - **TIDAK PERLU** memanggil seluruh pipeline jika tugasnya kecil / terlokalisasi.
   - Perbaikan 1 file / bug sepele / typo / CSS: **Langsung eksekusi atau pakai `/tdd`**.
   - Fitur baru standar / butuh arsitektur: Masuk **Main Flow** (`grill-with-docs` $	o$ `to-spec` $	o$ `to-tickets` $	o$ `implement`).
   - Task besar, ambigu, dan gelap gulita: Panggil **`wayfinder`**.
   - Ragu memilih alur / bingung: Panggil **`ask-matt`** sebagai traffic controller.
3. **Pre-Flight Verification (Wajib Cek Filesystem)**:
   Sebelum menjalankan tool/flow skill tertentu, pastikan skill tersebut terpasang di:
   - System prompt runtime (`<available_skills>`)
   - Project level: `.kilo/skills/`, `.kilocode/skills/`
   - Global level: `~/.kilocode/skills/`, `~/.config/kilo/skills/`, `~/.agents/skills/`
4. **Fallback Resilience**: Jika file skill tidak ditemukan secara fisik, terapkan prinsip logika skill tersebut secara langsung (*native reasoning*) tanpa melempar error tools missing.

---

## 🧭 2. Decision Matrix: Kapan Menggunakan Alur Apa?

```
                       ┌─────────────────────────────────┐
                       │        User Task / Input        │
                       └────────────────┬────────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
 🟢 [Small / Isolated]         🟡 [Medium / New Feature]     🔴 [Massive / Foggy Scope]
 - 1-2 files diff              - New subsystem               - Unknown architecture
 - Clear bug fix               - Multi-component flow        - Greenfield idea
 - UI / CSS tweak              - Architecture decisions      - High uncertainty
           │                            │                            │
           ▼                            ▼                            ▼
  [Direct Fix / TDD]             [The Main Flow]                [Wayfinder]
  • No grilling needed           1. /grill-with-docs            1. Map decision tickets
  • Minimal diff                 2. /to-spec                    2. Settle blockers
  • Fast verification            3. /to-tickets                 3. Hand off to /to-spec
                                 4. /implement (/tdd + review)
```

### Panduan Ambang Batas Kompleksitas:
| Level Kompleksitas | Karakteristik Tugas | Alur Rekomendasi | Skill Terkait |
| :--- | :--- | :--- | :--- |
| **Micro (Level 1)** | Ganti copy, perbaiki CSS, tambah helper 1 line, fix typo. | Direct Edit / Verification | *None / Pure Edit* |
| **Minor (Level 2)** | Tambah endpoint CRUD standar, fix bug dengan alur jelas. | TDD Focused | `tdd`, `diagnosing-bugs` |
| **Standard (Level 3)** | Fitur baru lengkap, integrasi payment gateway, sistem auth. | Main Flow (Idea $	o$ Ship) | `grill-with-docs`, `to-spec`, `to-tickets`, `implement`, `code-review` |
| **Epic (Level 4)** | Rancang platform dari nol, migrasi arsitektur monolit ke microservices. | Exploratory Mapping | `wayfinder`, `domain-modeling`, `research`, `prototype` |
| **Ambiguous (?)** | Tidak tahu harus mulai dari mana atau flow mana yang cocok. | Interactive Routing | `ask-matt` |


---

## 📚 3. Katalog Lengkap Seluruh Skill Matt Pocock

### 🅰️ Main Pipeline (Idea to Ship)
Rute standar pembuatan fitur dari konsep hingga siap merge:

1. **`grill-with-docs`**
   - **Fungsi**: Wawancara mendalam (*relentless interview*) untuk menantang asumsi, menemukan edge-case, dan merekam hasil kesepakatan dalam format `CONTEXT.md` dan ADR (*Architecture Decision Record*).
   - **Kapan Digunakan**: Saat memulai fitur baru di dalam direktori proyek aktif.
   - **Bedanya dengan `grill-me`**: `grill-with-docs` bersifat **stateful** (menulis file ke disk), sedangkan `grill-me` bersifat stateless (cocok di luar repo).

2. **`to-spec`**
   - **Fungsi**: Menyintesis obrolan, hasil grilling, dan kesepakatan arsitektur menjadi satu dokumen spesifikasi sistem teknis (*System Spec*) yang utuh.
   - **Kapan Digunakan**: Tepat setelah sesi interview/grilling selesai dan siap beralih ke perencanaan teknis.

3. **`to-tickets`**
   - **Fungsi**: Memecah dokumen spec menjadi tiket-tiket kecil (*tracer-bullet tickets*) yang mendeklarasikan dependensi pemblokir (*blocking edges*).
   - **Kapan Digunakan**: Sebelum implementasi multi-sesi dimulai. Menyimpan tiket di `.scratch/<feature>/issues/` atau GitHub Issues.

4. **`implement` & `implement-spec`**
   - **Fungsi**: Mengambil satu tiket kerja, mengeksekusinya menggunakan loop `tdd`, dan mengakhiri sesi dengan `code-review` otomatis sebelum commit.
   - **Kapan Digunakan**: Fase penulisan kode per-tiket. Bekerja dalam context window bersih (`/clear` antar tiket).

5. **`tdd`**
   - **Fungsi**: Mendorong disiplin penulisan kode *Red-Green-Refactor* (tulis unit test yang gagal $	o$ tulis kode minimal $	o$ refactor).
   - **Kapan Digunakan**: Saat membangun behavior baru atau memperbaiki bug secara test-first.

6. **`code-review`**
   - **Fungsi**: Meninjau git diff secara objektif pada dua sumbu: **Standards** (aturan repo) dan **Spec** (kesesuaian tiket).
   - **Kapan Digunakan**: Sebelum commit/merge atau saat memeriksa Pull Request.

