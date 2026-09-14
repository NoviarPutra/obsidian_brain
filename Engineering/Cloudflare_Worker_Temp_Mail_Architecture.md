# ⚡ Serverless Catch-All Temp Mail Architecture (Cloudflare Workers + D1 / Telegram)

Status: 📋 Planned / Future Implementation  
Primary Owner: `@Voldemort` (BOSS)  
Linked Worklog: [[Worklogs/2026-09-14]]  
Related Architecture: [[Engineering/Custom_Domain_Email_Plan|Custom Domain Email Plan]]

---

## 🎯 Objective
Membangun infrastruktur custom temporary email / multi-inbox generator dengan **budget Rp 0 (zero cost)**, 100% serverless, tanpa pusing verifikasi nomor HP/OTP, memanfaatkan ekosistem **Cloudflare Email Routing** + **Cloudflare Workers**.

---

## 🧭 Architecture Overview

```text
Sender (Website / Registrasi Eksternal)
       │
       ▼
Cloudflare Edge MX (Email Routing Catch-All *@domain.com)
       │
       ▼
Cloudflare Worker (Event: email())
       │
       ├─► [Pilihan A: Otomasi Bot / Real-time]
       │   Kirim webhook instan ke Telegram Bot (@Voldemort_menu_bot) dengan regex extraction OTP.
       │
       └─► [Pilihan B: UI / REST API]
           Simpan body email & attachment ke Cloudflare D1 Database / KV.
           Dapat diakses via Frontend (Pages) atau di-scrape script Python via REST API.
```

---

## 🛠️ Key Components & Implementation Steps

### 1. DNS & Nameserver Migration ($0)
- Domain yang digunakan tidak perlu ditransfer registrasinya (tetap di registrar asal).
- Cukup ganti **Nameserver (NS)** domain menjadi NS bawaan Cloudflare (misal: `*.ns.cloudflare.com`).
- Tidak mengganggu record website aktif (A/AAAA/CNAME tetap diarahkan ke origin IP).

### 2. Cloudflare Email Routing Configuration
- Masuk ke Cloudflare Dashboard > Domain > **Email Routing**.
- Tambahkan Catch-all Rule: `Catch-All -> Send to Worker`.
- Cloudflare secara otomatis menginjeksi DNS record:
  - `MX`: `route1.mx.cloudflare.net`, dll.
  - `TXT`: SPF record `v=spf1 include:_spf.mx.cloudflare.net ~all`.

### 3. Worker Code Minimalis (Inbound Telegram Forwarder)
```javascript
export default {
  async email(message, env, ctx) {
    const to = message.to;
    const from = message.from;
    const rawEmail = await new Response(message.raw).text();

    // Regex extraction 4-8 digit OTP
    const otpMatch = rawEmail.match(/\b\d{4,8}\b/);
    const otp = otpMatch ? otpMatch[0] : "No OTP detected";

    const text = `📬 *New Inbound Email!*\n*To:* \`${to}\`\n*From:* \`${from}\`\n*OTP:* \`${otp}\``;

    await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: env.TELEGRAM_CHAT_ID,
        text: text,
        parse_mode: "Markdown"
      })
    });
  }
};
```

### 4. Alternatif Ready-to-Deploy (Open Source Web UI)
- Jika butuh UI webmail siap pakai dengan generator inbox ala 10minutemail:
  - Deploy **[dreamhunter2333/cloudflare_temp_email](https://github.com/dreamhunter2333/cloudflare_temp_email)**.
  - Berjalan di atas Cloudflare Pages + Workers + D1 database (semuanya masuk tier gratis).

---

## 🛡️ Senior Dev Checklist Sebelum Eksekusi
- [ ] Pastikan domain yang akan digunakan tidak memiliki email MX aktif yang kritikal/digunakan untuk operasional utama.
- [ ] Bind worker environment variables (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`).
- [ ] Uji skenario edge: email HTML multipart, email encoding base64, dan rate limiting Telegram API.
