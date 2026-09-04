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

Panduan arsitektur dan operasional seluruh skill rekayasa perangkat lunak Matt Pocock untuk agen AI (Kilo / Claude Code). Dokumen ini berfungsi sebagai **single source of truth** bagi agen AI agar dapat menentukan rute kerja, mengeksekusi skill secara otonom, dan memverifikasi ketersediaan dependensi tanpa overengineering atau kebingungan logika (*zero ambiguity*).

---

## 🎯 1. Autonomous Agent Directives (5 Pilar Eksekusi AI)

Agen AI yang membaca dokumen ini **wajib** mematuhi 5 pilar operasional berikut:

1. **Direct Execution First (Eksekusi Langsung)**:
   - Jika instruksi/tugas user sudah jelas, dipahami secara penuh, dan yakin bisa diselesaikan tanpa kendala (misal: single-file fix, helper function, typo, CSS tweak, refactor sepele), **langsung kerjakan dengan native tools**.
   - **TIDAK PERLU** memanggil skill apa pun jika tidak ada nilai tambah arsitektural.

2. **Auto-Trigger Cerdas (Tanpa Panggilan Manual)**:
   - Jangan menunggu user mengetik `/nama-skill`. Kenali intensi dan bobot tugas secara otomatis untuk mengaktifkan workflow terkait hanya saat dibutuhkan.

3. **Anti-Overengineering (Prinsip YAGNI)**:
   - Dilarang memaksakan pipeline panjang (*grill → spec → tickets → implement*) untuk tugas kecil.
   - Gunakan pipeline penuh **hanya** untuk perancangan fitur baru substansial, perubahan arsitektur besar, atau domain baru.

4. **Pre-Flight Verification (Wajib Cek Filesystem)**:
   - Sebelum mengeksekusi alur skill khusus, periksa ketersediaan skill di lingkungan saat ini:
     - Runtime system prompt (`<available_skills>`)
     - Direktori project: `.kilo/skills/`, `.kilocode/skills/`
     - Direktori global: `~/.kilocode/skills/`, `~/.config/kilo/skills/`, `~/.agents/skills/`

5. **Fallback Resilience (Native Reasoning)**:
   - Jika file/tool skill tidak ditemukan secara fisik di runtime, **tetap jalankan prinsip dan metodologi logisnya secara native** tanpa melempar error `tool not found` kepada user.

---

## 🧭 2. Decision Matrix: Kapan Menggunakan Alur Apa?

```
                       ┌─────────────────────────────────┐
                       │        User Task / Request      │
                       └────────────────┬────────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
 🟢 [Small / Clear Task]       🟡 [Medium / New Feature]     🔴 [Massive / Foggy Scope]
 • 1-2 files diff              • Fitur baru multi-komponen   • Ide belum matang
 • Bug fix terlokalisir        • Perubahan alur data/bisnis  • Greenfield project
 • CSS / Copy / One-liner      • Butuh kesepakatan arsitek   • Tingkat ketidakpastian tinggi
           │                            │                            │
           ▼                            ▼                            ▼
  [Direct Fix / /tdd]            [The Main Flow]                [Wayfinder]
  1. Native edit / test          1. /grill-with-docs            1. Pemetaan kartu keputusan
  2. Zero pipeline bloat         2. /to-spec                    2. Selesaikan blocker satu per satu
  3. Verifikasi cepat            3. /to-tickets                 3. Oper ke /to-spec saat terang
                                 4. /implement (/tdd + review)
```

### Panduan Ambang Batas Kompleksitas:
| Level Kompleksitas | Karakteristik Tugas | Alur Rekomendasi | Skill Terkait |
| :--- | :--- | :--- | :--- |
| **Micro (Level 1)** | Ganti copy, perbaiki CSS, tambah helper 1 line, fix typo. | Direct Edit / Verification | *Tanpa skill (Pure Native)* |
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
   - **Kapan Digunakan**: Memulai fitur baru di dalam repositori aktif.
   - **Bedanya dengan `grill-me`**: `grill-with-docs` bersifat **stateful** (menulis file ke disk), sedangkan `grill-me` bersifat stateless (cocok di luar direktori repo).

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
   - **Kapan Digunakan**: Membangun behavior baru atau memperbaiki bug secara test-first.

6. **`code-review`**
   - **Fungsi**: Meninjau git diff secara objektif pada dua sumbu: **Standards** (aturan repo) dan **Spec** (kesesuaian tiket).
   - **Kapan Digunakan**: Sebelum commit/merge atau saat memeriksa Pull Request.

---

### 🅱️ Strategic Planning, Prototyping & Investigation

7. **`wayfinder`**
   - **Fungsi**: Memecahkan inisiatif raksasa / *greenfield project* yang terlalu gelap (*foggy*) untuk satu sesi menjadi peta keputusan bersama (*map of decision tickets*).
   - **Kapan Digunakan**: Proyek sangat besar yang belum jelas arsitektur akhirnya. Menghasilkan *keputusan*, bukan *deliverable*, lalu diserahkan ke `/to-spec`.

8. **`prototype`**
   - **Fungsi**: Membangun kode purwarupa cepat (*throwaway code*) untuk menjawab pertanyaan teknis (apakah state model cocok? bagaimana interaksi UI-nya?).
   - **Kapan Digunakan**: Saat debat desain tidak bisa diselesaikan hanya lewat diskusi. Disimpan di branch `prototype/<name>` sebagai sumber primer.

9. **`research`**
   - **Fungsi**: Menugaskan sub-agent di background untuk membaca sumber primer (dokumentasi resmi, RFC, standard API) dan menghasilkan ringkasan Markdown terverifikasi.
   - **Kapan Digunakan**: Memerlukan kepastian teknis pihak ketiga tanpa membebani context window sesi utama.

10. **`to-questionnaire`**
    - **Fungsi**: Kebalikan dari grilling; mengubah ketidakpastian yang bergantung pada pihak eksternal menjadi daftar kuesioner rapi untuk dikirim ke klien/stakeholder.
    - **Kapan Digunakan**: Keputusan teknis terhambat oleh missing requirement dari luar tim.

---

### 🅲 Diagnosis, Arsitektur & Pemeliharaan Codebase

11. **`diagnosing-bugs`**
    - **Fungsi**: Loop diagnosis ketat untuk bug sulit/flaky. Menolak berteori sebelum memiliki *single command feedback loop* yang mereproduksi kegagalan (merah), lalu membuat tes regresi.
    - **Kapan Digunakan**: Menghadapi laporan bug misterius, error intermiten, atau regresi performa.

12. **`triage`**
    - **Fungsi**: Memproses issue mentah dan PR eksternal melalui state-machine triage, mengategorikan, memverifikasi, dan menyusun brief kerja yang siap dieksekusi agent.
    - **Kapan Digunakan**: Menangani backlog issue yang menumpuk dari user/kontributor luar.

13. **`improve-codebase-architecture`**
    - **Fungsi**: Memindai codebase untuk menemukan peluang perbaikan struktur modul (*deep modules*) dan menyajikannya dalam laporan visual HTML.
    - **Kapan Digunakan**: Jadwal refactoring berkala atau maintenance codebase.

14. **`codebase-design` & `domain-modeling`**
    - **Fungsi**:
      - `codebase-design`: Mengatur interface modul agar dalam (*deep modules: interface sempit, fungsionalitas kaya*).
      - `domain-modeling`: Menajamkan istilah bisnis (domain glossary) di `CONTEXT.md` dan mencatat ADR.
    - **Kapan Digunakan**: Layer kosakata yang mendasari proses arsitektur dan refactoring.

15. **`resolving-merge-conflicts`**
    - **Fungsi**: Menyelesaikan git merge/rebase conflict hunk demi hunk berdasarkan intensi asli author tanpa pernah menjalankan `--abort`.
    - **Kapan Digunakan**: Terjadi konflik git saat rebase/merge.

16. **`retro`**
    - **Fungsi**: Menjalankan evaluasi retrospeksi setelah fitur selesai dibuat untuk mendokumentasikan apa yang dipelajari dan apa yang perlu di-improve.

---

### 🅳 Manajemen Konteks & Interaksi Sesi

17. **`ask-matt`**
    - **Fungsi**: Router interaktif yang merekomendasikan skill atau workflow mana yang paling pas untuk kondisi spesifik saat ini.
    - **Kapan Digunakan**: Ragu memilih alur kerja terbaik.

18. **`handoff` & `claude-handoff`**
    - **Fungsi**: Memadatkan (*compact*) riwayat percakapan panjang ke satu file Markdown portabel untuk dilanjutkan oleh agen/sesi baru dengan token bersih.
    - **Kapan Digunakan**: Context window mendekati zona degradasi (>150k token) atau ingin berganti lingkungan/worktree.

19. **`wait-what`**
    - **Fungsi**: Rem darurat untuk mereset penjelasan agent yang melenceng atau terlalu berbelit-belit agar dijelaskan ulang dengan bahasa yang lebih sederhana dan grounded.
    - **Kapan Digunakan**: Respons agen sebelumnya tidak mendarat dengan baik atau mulai halu.

---

### 🅴 Setup, Automation & Tooling Khusus

20. **`setup-matt-pocock-skills`**
    - **Fungsi**: Menginisialisasi konfigurasi awal di repositori baru (triage labels, direktori ADR `docs/adr/`, format `CONTEXT.md`, dan tracker issues).
    - **Kapan Digunakan**: Dijalankan satu kali saat pertama kali menyiapkan repositori baru.

21. **`wizard`**
    - **Fungsi**: Mengenerate script Bash interaktif langkah-demi-langkah untuk tugas-tugas yang hanya bisa dieksekusi oleh manusia (membuka dashboard cloud, setup secret CI, konfigurasi payment key).
    - **Kapan Digunakan**: Menemukan blocker yang mutlak membutuhkan tindakan langsung user di GUI/dashboard eksternal.

22. **`setup-ts-deep-modules`**
    - **Fungsi**: Memasang `dependency-cruiser` pada project TypeScript untuk membatasi akses modul internal agar hanya bisa diakses via entry point.

23. **`migrate-to-shoehorn`**
    - **Fungsi**: Mengganti type assertion kotor (`as Type`) pada file testing dengan helper resmi `@total-typescript/shoehorn`.

24. **`writing-fragments` → `writing-beats` → `writing-shape` → `writing-for-agents`**
    - **Fungsi**: Rantai penulisan konten/artikel/dokumentasi dari ide mentah acak (*fragments*) $	o$ rangkaian ketukan alur (*beats*) $	o$ paragraf utuh (*shape*) $	o$ format optimal LLM (*writing-for-agents*).

---

## ⚡ 4. Ringkasan Eksekusi bagi AI Agent

```
[Prompt Masuk]
      │
      ▼
Apakah task sudah jelas & yakin aman?
      ├──> [YA] $	o$ Eksekusi Langsung (Direct Execution / Native Tools)
      │
      └──> [TIDAK] $	o$ Cek Kompleksitas & Cek Ketersediaan Skill di Disk
                         ├──> [Skill Ada] $	o$ Jalankan Tool Skill Terkait
                         └──> [Skill Tidak Ada] $	o$ Terapkan Metodologi Logisnya secara Native
```
