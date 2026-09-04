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
