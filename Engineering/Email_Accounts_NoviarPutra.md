---
tags:
  - engineering/email
  - cloudflare
  - accounts
title: "Email Routing Accounts & Limit Documentation (`noviarputra.my.id`)"
---

# 📧 Cloudflare Email Routing - Dokumentasi Sistem & Akun

- **Target Domain**: `noviarputra.my.id`
- **Destination Email**: `sptfyv0004@gmail.com`
- **Status Sistem**: **AKTIF & OPERASIONAL (VERIFIED)**
- **Tanggal Konfigurasi**: 2026-09-20
- **Penyedia Layanan**: Cloudflare Email Routing (Edge Inbound Forwarding)
- **Zone ID**: `71774b24ea6bc92e647d0e1a096b323c`
- **Account ID**: `2083ac727c2c309b505e4117edb7efd0`

---

## 📋 1. Daftar 20 Akun Email (Autoincrement)

Semua email yang dikirim ke alamat di bawah ini otomatis diteruskan secara instan ke `sptfyv0004@gmail.com`:

1. `user01@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
2. `user02@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
3. `user03@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
4. `user04@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
5. `user05@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
6. `user06@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
7. `user07@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
8. `user08@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
9. `user09@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
10. `user10@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
11. `user11@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
12. `user12@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
13. `user13@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
14. `user14@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
15. `user15@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
16. `user16@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
17. `user17@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
18. `user18@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
19. `user19@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`
20. `user20@noviarputra.my.id` ➔ `sptfyv0004@gmail.com`

---

## ⚙️ 2. Aturan, Kuota, dan Batasan Sistem (Limits)

### A. Cloudflare Email Routing (Inbound Forwarding)
- **Biaya**: $0 (100% Gratis selamanya).
- **Kuota Custom Address**: Maksimal 200 alamat per zona (Terpakai: 20 / 200).
- **Kuota Destination Address**: Maksimal 200 alamat terverifikasi per akun (Terpakai: 1 / 200).
- **Ukuran Maksimum Email**: 25 MB per pesan (termasuk attachments).
- **Limit Pesan Masuk Harian**: *Unmetered* (Tidak ada batasan kuota harian statis untuk pemakaian wajar).
- **Rate Limit Edge**: Perlindungan lonjakan ekstrem (~100–200 pesan/menit dari pengirim yang sama untuk mitigasi mail-bombing).

### B. Batasan Penerimaan Google Gmail (`sptfyv0004@gmail.com`)
- **Batas Penerimaan Pesan**: ~10.000 email per hari.
- **Batas Kecepatan Masuk**: ~60 pesan per menit (melebihi ini akan mengalami penundaan/greylisting sementara oleh Google).
- **Kapasitas Kotak Masuk**: Berbagi kuota penyimpanan Google Drive (15 GB gratis).

### C. Aturan Outbound (Kirim Email Keluar)
- Cloudflare Email Routing murni **Inbound Forwarding** (hanya menerima pesan masuk).
- Jika perlu membalas atau mengirim email atas nama domain, gunakan fitur *Send mail as* di Gmail via SMTP Relay eksternal gratis (misal: Brevo 300 email/hari atau Resend 100 email/hari).

---

## 🛡️ 3. DNS Telemetri Aktif

- **MX 1**: `route1.mx.cloudflare.net` (Priority: 28)
- **MX 2**: `route2.mx.cloudflare.net` (Priority: 85)
- **MX 3**: `route3.mx.cloudflare.net` (Priority: 57)
- **SPF**: `v=spf1 include:_spf.mx.cloudflare.net ~all`
