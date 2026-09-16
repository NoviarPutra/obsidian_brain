---
tags:
  - engineering/integration
  - cloudflare
  - automation
title: "Atria 100M Token Farmer Integration"
---

# 🤖 Atria 100M Token Farmer — Integration Notes

> **Status**: Script Patched & Ready, Awaiting Cloudflare Worker Deployment
> **Created**: 2026-09-15
> **Tags**: #atria #farmer #omniroute #cloudflare #automation

---

## Overview

Script otomatisasi untuk registrasi akun massal Atria Dawn Preview (100.000.000 token per akun) dengan integrasi OmniRoute sebagai target database.

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  farm_atria.py  │────▶│ Cloudflare Temp   │────▶│  Atria API      │
│  (Multi-Worker) │     │  Email Worker     │     │  (Auth/Register)│
└────────┬────────┘     └──────────────────┘     └────────┬────────┘
         │                                                │
         │ Inject Key                                     │ Get API Key
         ▼                                                ▼
┌─────────────────┐                          ┌─────────────────┐
│ OmniRoute DB    │                          │ keys.txt        │
│ (SQLite)        │                          │ (Backup)        │
└─────────────────┘                          └─────────────────┘
```

---

## Files Structure

```
/tmp/sandbox_atria/
├── farm_atria.py          # Main script (patched for OmniRoute)
└── config/
    ├── .env.example       # Template konfigurasi
    ├── README.md          # Dokumentasi
    ├── requirements.txt   # Python dependencies
    └── run.bat            # Windows launcher (original)
```

---

## Modifications Made

### 1. Database Path
- **Before**: `%APPDATA%\9router\db\data.sqlite` (Windows 9router)
- **After**: `/home/voldemort/.omniroute/storage.sqlite` (VPS OmniRoute)

### 2. Functions Renamed
| Original | New |
|----------|-----|
| `init_9router_node()` | `init_omniroute_node()` |
| `inject_key_to_9router()` | `inject_key_to_omniroute()` |

### 3. Schema Adaptation
- **9router**: Table `providerNodes`, JSON blob di kolom `data`
- **OmniRoute**: Table `provider_nodes`, kolom `api_key` langsung + `provider_specific_data`

### 4. Output Format
```
# Before: YYYY-MM-DD HH:MM:SS | email | key | 100M_TOKENS | 9router:True
# After:  YYYY-MM-DD HH:MM:SS | email | key | 100M_TOKENS | OmniRoute:True
```

---

## Prerequisites

### ✅ Available
- Python 3.11+
- `requests>=2.31.0`
- OmniRoute running at `127.0.0.1:20128`
- Node `Atria` already in DB

### ❌ Required (Blocker)
1. **Cloudflare Account** dengan custom domain
2. **Cloudflare Email Routing** aktif untuk domain
3. **Worker deployment** dari repo: `dreamhunter2333/cloudflare_temp_email`

---

## Cloudflare Worker Setup Steps

### Step 1: Clone Repository
```bash
git clone https://github.com/dreamhunter2333/cloudflare_temp_email
cd cloudflare_temp_email/worker
```

### Step 2: Install Wrangler
```bash
npm install -g wrangler
```

### Step 3: Create D1 Database & KV Namespace
```bash
wrangler d1 create temp_email_db
wrangler kv namespace create temp_email_kv
```

### Step 4: Configure wrangler.toml
```toml
name = "temp-email-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"


binding = "DB"
database_name = "temp_email_db"
database_id = "<YOUR_D1_ID>"


binding = "KV"
id = "<YOUR_KV_ID>"

vars = {
  JWT_SECRET = "random-string-aman",
  DOMAINS = '["domainkamu.com"]'
}
```

### Step 5: Deploy Worker
```bash
wrangler deploy
```

### Step 6: Configure Script
Buat `.env`:
```ini
CF_API_BASE=https://temp-email-worker.nama-lu.workers.dev
CF_DOMAIN=domainkamu.com
TARGET_ACCOUNTS=10
WORKER_THREADS=3
```

---

## Usage

### Test Single Account
```bash
cd /tmp/sandbox_atria
python farm_atria.py 1 1
```

### Run with Multiple Workers
```bash
python farm_atria.py 50 5
```

### Expected Output
```
========================================================================
      ATRIA 100M TOKEN MULTI-WORKER FARMER & OMNIROUTER INJECTOR
========================================================================
[+] OmniRoute Node 'Atria' Terdeteksi (ID: atria-xxxxxxx)
[+] Model Target   : atria/Atria-Dawn-Preview (256K)
[+] Domain Worker  : @domainkamu.com
[+] Target Panen   : 50 Akun (5.000 Juta Tokens)
[W1] [#1/50] ✓ user1@domainkamu.com | abc123... | +100M Tokens | OmniRoute:True (2.3s)
...
```

---

## Security Notes

- Script menggunakan sandbox `/tmp/sandbox_atria/` — tidak mengganggu filesystem utama
- Database OmniRoute dilindungi dengan `db_lock` threading
- API keys disimpan di kolom `api_key` OmniRoute (bukan JSON blob)
- Backup otomatis ke `keys.txt`

---

## Related

- [[Worklogs/2026-09-15|🗓️ 2026-09-15 Worklog]]
- [[Multi_Account_Worker_Farm_Architecture|📐 Worker Farm Architecture]]
- [[OmniRouter/Index|🔀 OmniRoute Index]]
