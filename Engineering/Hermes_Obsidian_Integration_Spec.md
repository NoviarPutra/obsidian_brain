---
tags:
  - engineering/architecture
  - hermes
  - obsidian
  - vault
  - security
title: "🧠 Hermes ↔ Obsidian Vault Integration Specification"
---

# 🧠 Hermes ↔ Obsidian Vault Integration Specification

> **Related**: [[Engineering/Index|⚡ Engineering MOC]] | [[Engineering/Telegram_Bots_Architecture|🤖 Telegram Bots Architecture]] | [[Worklogs/Index|📓 Worklogs Index]] | [[Home|🌌 Home]]

**Status**: disetujui, belum dibangun · **Tanggal**: 2026-09-26 · **Host**: VPS voldemort (`103.174.114.224`)
**Hasil grilling**: 30 keputusan, frontier kosong.

---

## 1. Premis — ini membatasi, bukan membuka

Diskusi awal berangkat dari pertanyaan "apakah memberi Hermes akses ke vault". Audit membalik premis itu: **aksesnya sudah ada dan tanpa penjaga.** Keadaan terverifikasi sebelum pekerjaan ini:

- `approvals.mode: 'off'` dan `destructive_slash_confirm: false` di `~/.hermes/config.yaml`
- `HERMES_WRITE_SAFE_ROOT` tidak diset — di `.env` maupun di env proses gateway yang hidup
- `platform_toolsets` **absen**, jadi Telegram mendapat bundle default penuh: `file`, `terminal`, `code_execution`, `delegation`, `cronjob`, `browser`
- Skill bawaan `~/.hermes/skills/note-taking/obsidian/SKILL.md` aktif di skills prompt — *"Read, search, create, and edit notes in the Obsidian vault"*
- `~/.hermes/memories/MEMORY.md` baris 1, disuntik ke system prompt setiap sesi, menyebut path vault secara eksplisit
- `OBSIDIAN_VAULT_PATH` tidak diset, dan tidak ada pemicu otonom

Yang belum ada hanyalah pemicu dan **seluruh penjaganya**.

## 2. Fakta yang mengikat desain

| Fakta (terverifikasi langsung di box) | Konsekuensi |
|---|---|
| `sync.sh` siklus ~62s: `inotifywait -t 60` + `sleep 2` + `git add -A` + commit + push | Tulisan harus atomik; commit bukan tugas Hermes |
| Konflik → `rebase --abort` → `stash` → `pull --rebase -X theirs` → `stash pop 2>/dev/null \|\| true` | `Worklogs/` adalah zona kehilangan data |
| `Worklogs/2026-09-21.md` memuat 4 marker konflik **di dalam HEAD**, sudah ter-push | Kerusakan nyata, bukan hipotetis |
| `cleanup_stale_locks` menghapus `.git/*.lock` >3 menit, tanpa cek proses pemilik | Hermes tidak boleh memegang lock git |
| Lint: wikilink rusak → `exit 1`; orphan → warning, `exit 0` | Jurnal tidak butuh link masuk |
| Hook lint ada di Mac, **tidak ada** di VPS; lint memindai seluruh vault, bukan diff | Satu link rusak dari VPS membekukan semua commit Mac, senyap |
| Tidak ada vector store; `state.db` FTS hanya mengindeks pesan percakapan | Sisi baca terikat `context_length: 65536`, bukan ukuran vault |
| `HERMES_WRITE_SAFE_ROOT` nol referensi di `terminal_tool.py` / `code_execution_tool.py` | Tulisan lewat shell melewatinya sepenuhnya |
| `memory_tool_store.py` & `skills_tool.py` menulis via `atomic_write_text`, nol import `file_safety` | Safe root aman diset tanpa mematikan tool `memory`/`skill_manage` |
| RAM 3910 MB total, ~2000 MB available, swap ~1 GB terpakai | Hindari proses baru — tanpa MCP server |

## 3. Arsitektur penegakan — apa yang benar-benar menahan apa

| Lapis | Menahan | Kekuatan |
|---|---|---|
| Shell hook `pre_tool_call`, `fail_closed: true` | kebijakan path untuk `write_file`, `patch`, `delete_file`, `move_file`, `read_file`, `search_files` | **Kode.** `exit 2` memblok; pesannya menjadi hasil tool yang dilihat model |
| `HERMES_WRITE_SAFE_ROOT` (2 root) | semua tulisan tool file, berlapis di bawah hook | **Kode**, tapi tool file saja |
| `agent.disabled_toolsets: [code_execution, delegation]` | menghapus `execute_code` dan `delegate_task` | **Absolut** — toolnya tidak ada |
| `approvals.mode: manual` | konfirmasi tombol Telegram untuk edit file eksisting | **Kode.** Blok 300s, timeout → `BLOCKED` ("Silence is not consent") |
| Wrapper jurnal | path tulis otonom, atomisitas, batas ukuran, gate lint | **Kode**, jalur otonom saja |
| `transform_tool_result` hook | scan kredensial sebelum konten meninggalkan box | **Kode** — kemampuan redact diverifikasi saat membangun |
| Isi `SKILL.md` dan prompt | sisanya | **Imbauan.** Bukan penjaga |

## 4. Komponen

**A — Batas tulis.** Drop-in systemd `Environment=HERMES_WRITE_SAFE_ROOT=/home/voldemort/documents:/home/voldemort/services/obsidian-stack/vault`. Lewat drop-in, bukan `.env`, karena env proses gateway hanya memuat `HERMES_HOME`; diverifikasi lewat `/proc/<pid>/environ` setelah restart. Safe root diperiksa **terakhir** di `_classify_write_denial`, setelah denylist kredensial dan subpath HERMES_HOME.

**B — Kebijakan path.** `~/.hermes/hooks/vault_policy.py`, terdaftar di `hooks:` dengan `fail_closed: true` dan `hooks_auto_accept: true` (tanpa yang kedua, hook terdaftar tapi **dilewati diam-diam** di gateway headless). Aturan:

- `Hermes/` — bebas tulis
- `Engineering/` — buat-baru saja; edit file eksisting → eskalasi ke approval
- `Worklogs/` — **ditolak** (zona `-X theirs` + `vault_scribe.py` menu bot menempel tanpa lock)
- Baca — whitelist `Engineering/`, `Worklogs/`, `Hermes/`; di luar itu ditolak
- Sisanya ditolak

**C — Jurnal otonom.** systemd user timer harian memanggil wrapper. Target dihitung **wrapper** dari jam sistem, bukan dipilih model: `Hermes/Journal/YYYY-MM-DD.md`. Tulis ke `.tmp.XXXX` di direktori yang sama lalu `os.replace()` — rename satu filesystem itu atomik, sehingga `inotifywait` tidak pernah menangkap file setengah jadi. Batas ukuran keras per entri. Hari tanpa aktivitas tidak menulis file sama sekali. Setelah menulis: jalankan `vault_lint.py`; kalau menolak, file dihapus kembali dan admin dipaging — vault tidak pernah tertinggal dalam keadaan yang memblok commit. Pengikat: `flock`, `RuntimeMaxSec`, batas iterasi agent.

**D — Jalur interaktif (chat Telegram).** Note masuk `Hermes/Inbox/YYYY-MM-DD-HHMM-<slug>.md` — satu file per note, tidak pernah menyentuh file jurnal, jadi tick otonom dan sesi interaktif tidak pernah memegang file yang sama. Edit note eksisting menampilkan diff di chat lalu menunggu tombol konfirmasi.

**E — Commit.** Hermes tidak menjalankan git sama sekali; `sync.sh` memungut dalam ≤62 detik. Alasannya `cleanup_stale_locks`: operasi git yang menahan `index.lock` >3 menit akan lock-nya dihapus, lalu dua proses menulis index yang sama — korupsi, bukan konflik merge. Tambahan `.gitignore` vault: `**/.tmp.*`.

**F — Pengerasan jalur pengiriman.** Kedua script sinkron berhenti membuang status `git commit`. Tanpa ini, satu wikilink rusak yang di-push dari VPS menolak **setiap** commit Mac berikutnya, sementara script launchd membuang pesan hook ke `/dev/null` lalu mencatat "Pushed local changes" karena `git push` pada branch up-to-date keluar 0 — pekerjaan menumpuk tanpa satu tanda.

**G — Remediasi.** `Worklogs/2026-09-21.md` dibereskan, kedua sisi dipertahankan dengan penanda asal.

**H — Paging.** Bot Hermes (`@voldemort_gateway_hermes_bot`) untuk laporan rutin; unit `OnFailure=` lewat token menu bot untuk kasus Hermes mati atau OOM-killed — proses terpisah, jadi tetap bisa bicara saat penulisnya sendiri yang rusak.

## 5. Ledger keputusan

| # | Keputusan |
|---|---|
| Q1 | Dua arah: baca dan tulis |
| Q2 | Pemicu otonom terjadwal |
| Q3 | Gagal berisik, tanpa retry loop |
| Q4 | Satu pekerjaan per tick: jurnal harian append-only |
| Q5 | Namespace `Hermes/Journal/`, tidak pernah menyentuh file lain |
| Q6 | Gate tulis → lint → batalkan bila ditolak |
| Q7 | Harian, dengan `flock` + timeout keras + batas iterasi |
| Q8 | Ikut konvensi vault; prosa Indonesia, path/command English |
| Q9 | Hari kosong tidak menulis; batas ukuran entri keras |
| Q10 | Bot Hermes utama + backstop systemd via token menu bot |
| Q11 | Whitelist direktori baca |
| Q12 | Scan kredensial sebelum konten meninggalkan box |
| Q13 | Target tulis dikunci wrapper + instruksi data-only |
| Q14 | Timer dipasang disabled; tiga tick verifikasi manual dulu |
| Q15 | `HERMES_WRITE_SAFE_ROOT` diset ke dua root |
| Q16 | Tool `file` bawaan + wrapper tipis; tanpa MCP server |
| Q17 | systemd user timer, bukan cron internal Hermes |
| Q18 | Baca on-demand dengan batas byte; tanpa index |
| Q19 | Hermes tidak pernah menyentuh git |
| Q20 | Tulis atomik: temp di direktori sama + `os.replace()` |
| Q21 | Perbaiki `Worklogs/2026-09-21.md`, pertahankan kedua sisi |
| Q22 | Perbaiki wedge lint asimetris sebagai bagian pekerjaan ini |
| Q23 | Allowlist tulis bertingkat; `Worklogs/` dilarang |
| Q24 | Edit eksisting lewat diff + konfirmasi eksplisit |
| Q25 | Cakupan baca interaktif sama dengan otonom |
| Q26 | Note interaktif satu file per note di `Hermes/Inbox/` |
| Q27 | `approvals.mode: manual` |
| Q28 | Penegakan lewat shell hook `pre_tool_call` |
| Q29 | Cabut `code_execution`; `terminal` tetap hidup |
| Q30 | Cabut `delegation` |

## 6. Kriteria penerimaan

Timer dipasang dalam keadaan **disabled**. Tiga tick manual:

1. Hari berisi aktivitas → menulis satu file baru, tidak menyentuh yang lain
2. Hari kosong → benar-benar tidak menulis apa pun
3. Jurnal dengan wikilink rusak yang disengaja → wrapper membatalkan tulisannya sendiri, memaging, vault tetap lint-clean

Empat uji kebijakan:

1. Tulis ke `Worklogs/` diblok hook
2. Edit note `Engineering/` memunculkan tombol konfirmasi Telegram yang nyata
3. Tulis di luar safe root ditolak `write_file`
4. Hook yang sengaja dibuat error **menolak**, bukan meloloskan (bukti `fail_closed` bekerja)

## 7. Celah yang tetap ada — dinamai, tidak disembunyikan

- **`terminal` melewati semuanya kecuali hook.** Nol referensi `HERMES_WRITE_SAFE_ROOT` di `terminal_tool.py`. Hook melihat panggilannya, tapi memolisikan string shell bisa dilangkahi. Docstring `agent/file_safety.py` sendiri menyatakannya: *"Every guard here is defense-in-depth, NOT a security boundary: the terminal tool runs as the same OS user and can read/write anything."*
- **Cakupan hook untuk subagent belum terbukti** — karena itu `delegation` dicabut (Q30), mengubah "belum terverifikasi" menjadi "tidak relevan".
- Jalur `-X theirs` di `sync.sh` tetap bisa membuang hunk lokal di `Worklogs/`.
- Mac tidak pernah menyelesaikan konflik (`rebase --abort`, berhenti) → divergensi bisa membesar.
- `cleanup_stale_locks` tetap tanpa cek identitas proses.
- Scan kredensial adalah regex, bukan semantik — ia menangkap pola token yang dikenal, bukan rahasia yang ditulis prosa.
- Output tool yang melebihi budget di-spill ke `~/.hermes/cache/spillover/` dan path-nya diserahkan ke model, jadi batas output bukan mekanisme containment.

Spesifikasi ini **tidak** mengklaim zero-gap. Klaimnya lebih sempit dan bisa diuji: setiap celah di atas sudah dinamai, dan setiap batas yang disebut "ditegakkan" memang ditegakkan kode, bukan prompt.

## 8. Urutan bangun

`G` dan `F` lebih dulu — membereskan yang sudah rusak sebelum menambah penulis baru. Lalu `A`, `B`, `C`, `D`, `E`, `H`, dengan verifikasi di setiap langkah, baru tiga tick penerimaan.
