---
tags:
  - engineering/email
  - sop
  - documentation
title: "Panduan Pengguna & Batasan Operasional Email Virtual noviarputra.my.id"
---

# 📖 Panduan Pengguna & Batasan Operasional Email Virtual (`noviarputra.my.id`)

Dokumen ini disusun sebagai Standard Operating Procedure (SOP) bagi operator, tester, atau anggota tim yang menggunakan 20 akun email virtual di domain `noviarputra.my.id`.

---

## 🎯 1. Konsep & Arsitektur Dasar

Alamat email `user01@noviarputra.my.id` s/d `user20@noviarputra.my.id` adalah **Virtual Inbound Forwarding Aliases**, bukan kotak surat mandiri (mailbox).
* **Mekanisme**: Semua pesan yang dikirim ke alamat-alamat ini diproses oleh edge Cloudflare dan diteruskan instan ke 1 kotak masuk pusat Administrator (`sptfyv0004@gmail.com`).
* **Kredensial**: Tidak ada username/password individual untuk login.

---

## ✅ 2. Apa yang BISA Dilakukan (Capabilities)

* **Registrasi Multi-Akun**: Mendaftar akun baru pada berbagai platform web, media sosial, tools AI, forum, dan SaaS.
* **Penerimaan Kode OTP & 2FA**: Menerima kode verifikasi angka secara real-time (latensi < 3 detik).
* **Penerimaan Magic Link**: Mengklik link aktivasi dan pendaftaran yang dikirimkan oleh sistem eksternal.
* **Agregasi Notifikasi**: Menerima email laporan, status tiket, tagihan digital, dan newsletter.
* **Zero Mailbox Full**: Tidak ada risiko kuota storage penuh per akun karena email tidak disimpan di server domain lokal.

---

## ❌ 3. Apa yang TIDAK BISA Dilakukan (Restrictions)

* **TIDAK BISA Login Langsung ke Webmail**: Tidak dapat login ke Gmail, Outlook, atau webmail domain independen dengan akun `userXX@noviarputra.my.id`.
* **TIDAK BISA Mengirim / Membalas Email (No Native Outbound)**: Sistem murni *Inbound*. Tidak bisa membuat email keluar baru (compose) atau membalas pesan secara langsung.
* **TIDAK ADA Privasi Antar Pengguna**: Seluruh email masuk bermuara di satu inbox pusat yang dikelola Administrator. Jangan gunakan untuk urusan personal, perbankan pribadi, atau data rahasia individu.
* **TIDAK Mendukung Mail Client (IMAP/POP3)**: Aplikasi seperti Apple Mail, Thunderbird, atau MS Outlook tidak bisa dihubungkan menggunakan kredensial akun ini.
* **Dilarang Menggunakan Format Acak**: Sistem menggunakan *Strict Explicit Routing*. Alamat di luar `user01` s/d `user20` (misal: `user21`, `admin@...`) akan langsung ditolak (hard bounce) oleh Cloudflare.

---

## ⚠️ 4. Batasan Teknis & Limitasi Sistem

1. **Ukuran Maksimum Email**: **25 MB** (termasuk attachments). Email di atas 25 MB akan ditolak di edge.
2. **Filter Keamanan**: File berbahaya berekstensi `.exe`, `.bat`, `.vbs`, `.iso` otomatis diblokir sistem keamanan Google/Cloudflare.
3. **Limit Kecepatan Masuk**: Pengiriman blast/spam ekstrem (>60 email/menit dari satu IP) dapat mengalami greylisting sementara di sisi Gmail.

---

## 🔄 5. SOP Alur Kerja User

1. **Gunakan Alamat Resmi**: Masukkan salah satu alamat yang dialokasikan (contoh: `user04@noviarputra.my.id`).
2. **Trigger Kode / Link**: Lakukan registrasi atau request OTP pada platform target.
3. **Koordinasi ke Admin**: Hubungi pemegang akses central inbox (`sptfyv0004@gmail.com`):
   > *"Tolong cek OTP untuk user04 dari platform [Nama Layanan]."*
4. **Triase Admin**: Admin mencari email dengan filter `to:user04@noviarputra.my.id` di Gmail dan memberikan kodenya kepada pengguna.
