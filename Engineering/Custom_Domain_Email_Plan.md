# 📧 Custom Domain Email Architecture & Roadmap (`noviarputra.my.id`)

Status: 📋 Planned / Roadmap  
Target Domain: `noviarputra.my.id`  
Primary Owner: `@Voldemort` (BOSS)  
Linked Worklog: [[Worklogs/2026-09-12]]

---

## 🎯 Objective
Mengonfigurasi domain pribadi `noviarputra.my.id` agar memiliki alamat email kustom profesional (misal: `halo@noviarputra.my.id`, `contact@noviarputra.my.id`, atau `dika@noviarputra.my.id`) tanpa mengorbankan atau mengganggu kemampuan domain untuk deploy website/web app portofolio di masa depan.

---

## 🧭 DNS Independence Concept (Web vs Email)
Domain `noviarputra.my.id` dapat melayani website dan email secara simultan tanpa konflik:
- **Web Traffic**: Dikelola via DNS Record `A` / `AAAA` / `CNAME` (Arahkan ke IP VPS / Cloudflare Pages / Vercel).
- **Email Traffic**: Dikelola via DNS Record `MX` (Mail Exchange), `TXT` (SPF, DKIM, DMARC).

---

## 🛠️ Selected Approaches & Options

### 🥇 Opsi 1: Cloudflare Email Routing (Rekomendasi Utama - $0 Free Tier)
- **Model**: Automatic Inbound Forwarding ke Gmail pribadi.
- **Kelebihan**:
  - 100% Gratis selamanya tanpa biaya bulanan.
  - Terintegrasi langsung dengan ekosistem Cloudflare yang sudah dipakai di VPS (Cloudflare AI & R2).
  - Menghemat resource VPS karena proses routing ditangani Cloudflare edge network.
- **DNS Records yang Dibutuhkan**:
  - `MX`: `route1.mx.cloudflare.net`, `route2.mx.cloudflare.net`, `route3.mx.cloudflare.net`
  - `TXT (SPF)`: `v=spf1 include:_spf.mx.cloudflare.net ~all`
- **Outbound Email (Kirim Pesan)**:
  - Menggunakan fitur *Send mail as* di Gmail via SMTP relay gratis (Google App Password / Brevo / Resend).

### 🥈 Opsi 2: Zoho Mail (Dedicated Webmail & Inbox Gratis)
- **Model**: 5 Dedicated Mailboxes (5 GB storage per user).
- **Kelebihan**: Punya webmail resmi dan aplikasi mobile mandiri.

### 🥉 Opsi 3: Developer / Bot Transaksional (Resend / AWS SES)
- **Model**: API-based email sending untuk bot Telegram atau aplikasi web.

---

## 📝 Execution Checklist (Untuk Dikerjakan Nanti)
- [ ] Pindahkan Nameserver `noviarputra.my.id` ke Cloudflare (saat ini masih di `dns-parking.com`).
- [ ] Aktifkan menu **Email Routing** di Dashboard Cloudflare untuk zona `noviarputra.my.id`.
- [ ] Buat routing address: `contact@noviarputra.my.id` ➔ `<Gmail Pribadi BOSS>`.
- [ ] Validasi email konfirmasi di inbox Gmail.
- [ ] Uji coba kirim email tes dari luar ke `contact@noviarputra.my.id`.
- [ ] (Opsional) Setup SMTP outbound untuk balas email langsung dengan identitas domain.
