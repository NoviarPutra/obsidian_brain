---
tags:
  - engineering/ops
title: "⚙️ Hermes ↔ Vault Integration Artifacts"
---

# ⚙️ Hermes ↔ Vault Integration Artifacts

> **Related**: [[Engineering/Hermes_Obsidian_Integration_Spec|🧠 Integration Spec]] | [[Home|🌌 Home]]

Kode pendukung integrasi Hermes ke vault ini. Rancangan dan alasan setiap keputusan ada di
spec; file di sini adalah implementasinya.

## Yang ini sumber kebenaran (live path adalah symlink ke sini)

| File | Live path di VPS |
|---|---|
| `vault_policy.py` | `~/.hermes/hooks/vault_policy.py` |
| `vault-journal.py` | `~/.hermes/bin/vault-journal.py` |
| `journal-alert.sh` | `~/.hermes/bin/journal-alert.sh` |

Mengedit file di sini **langsung mengubah yang berjalan**. Dua konsekuensi: setelah menyentuh
`vault_policy.py`, jalankan `hermes hooks doctor` karena allowlist mencatat mtime saat
persetujuan; dan kalau vault ini pernah di-clone ulang atau di-reset keras, symlink-nya putus
dan timer jurnal gagal — itu harga yang diterima sadar demi nol drift.

## Yang ini salinan, bukan yang berjalan

`systemd/` dan `sync.vps.sh` adalah snapshot untuk riwayat. systemd memiliki unit yang hidup dan
container `obsidian-sync` memuat direktori scripts-nya sendiri, jadi keduanya tidak bisa
disymlink ke sini. Kebenaran live-nya: `systemctl --user cat hermes-journal.service` dan
`~/services/obsidian-stack/scripts/sync.sh`.
