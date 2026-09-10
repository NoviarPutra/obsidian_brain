---
tags:
  - engineering/architecture
  - engineering/cloud
  - storage/r2
  - cloudflare
title: "☁️ Cloudflare R2 Object Storage Architecture & Media Flow"
---

# ☁️ Cloudflare R2 Object Storage Architecture & Media Flow

Comprehensive, production-grade technical specification for **Cloudflare R2 Object Storage** integration across Local Workstations, Hermes Agent, Telegram Bot, and `voldemort-vps`.

---

## 🏛️ 1. High-Level Architecture Topology

```
┌────────────────────────────────────────────────────────────────────────┐
│                      INGESTION & EXECUTION LAYER                       │
│  • CLI: ~/.hermes/bin/cf-flux                                         │
│  • Telegram: @Voldemort_menu_bot (Dockerized)                          │
│  • SRE Backup: /home/voldemort/services/backup/scripts/backup.sh      │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   CLOUDFLARE WORKERS AI PIPELINE                       │
│  • Endpoint: https://api.cloudflare.com/client/v4/accounts/{ID}/ai/run/│
│  • Model: @cf/black-forest-labs/flux-1-schnell                         │
│  • Output: Raw In-Memory JPEG Buffer (~950 KB)                         │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 CLOUDFLARE R2 OBJECT STORAGE PIPELINE                  │
│  • REST API: https://api.cloudflare.com/client/v4/accounts/{ID}/r2/... │
│  • S3 Endpoint: https://{ACCOUNT_ID}.r2.cloudflarestorage.com          │
│  • Bucket: voldemort-gallery                                           │
└──────────────────┬──────────────────────────────────┬──────────────────┘
                   │                                  │
                   ▼                                  ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│       ☁️ R2 BUCKET HIERARCHY         │  │    🧹 LIFECYCLE MANAGEMENT   │
│  • flux/flux_YYYYMMDD_HHMMSS.jpg     │  │  • Local Cache: Auto-Cleaned │
│  • documents/doc_*.md                │  │  • Explicit: -o path.jpg     │
│  • backups/voldemort-backup-*.enc    │  │  • Egress Bandwidth: $0 / Free│
└──────────────────────────────────────┘  └──────────────────────────────┘
```

---

## 🔑 2. Identity, Tokens & Credentials Matrix

All credentials are encrypted and stored in environment files (`chmod 600`) without host pollution:

| Parameter | Configuration Value | Usage Scope & Permissions |
|---|---|---|
| **Account ID** | `738f2def6189bcb43a3d5aae2347ca74` | Global Cloudflare Account ID |
| **Workers AI Token** | `Stored in ~/.hermes/.env` | AI Inference (`Workers AI: Run`) |
| **R2 User API Token** | `Stored in ~/.hermes/.env` | `Account > Workers R2 Storage > Edit` |
| **Bucket Name** | `voldemort-gallery` | Primary Object Storage Bucket |
| **Storage Class** | `Standard` | 10 GB Free Storage / Month |
| **Jurisdiction / Region** | `Automatic (APAC / Singapore)` | Low-latency global edge distribution |

### Exact Token Creation Steps (Cloudflare Dashboard)
1. Navigate to **Manage Account > API Tokens** (or **My Profile > API Tokens**).
2. Click **Create Token** -> Choose **Create Custom Token** (`Get started`).
3. Set Token Name: `voldemort-r2-token`.
4. Permissions:
   - `Account` | `Workers R2 Storage` | **`Edit`**
5. Account Resources:
   - `Include` | `All accounts` (or select Account `738f2def6189bcb43a3d5aae2347ca74`).
6. Click **Continue to summary** -> **Create Token**.
7. Verify Token via CLI:
   ```bash
   curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer <R2_TOKEN>"
   # Expected: {"result":{"status":"active"},"success":true}
   ```

---

## 📁 3. Standardized Object Key Prefix Hierarchy

The bucket `voldemort-gallery` uses a strictly partitioned prefix structure:

```text
voldemort-gallery/
├── 🖼️ flux/
│   ├── flux_20260910_141015.jpg       # Timestamped JPEG files from cf-flux & Telegram
│   └── flux_20260910_141630.jpg
├── 📑 documents/
│   ├── markitdown_parsed_*.md         # Converted MarkItDown documents & reports
│   └── telemetry_briefs_*.pdf
└── 💾 backups/
    ├── voldemort-backup-20260910.tar.gz.enc      # AES-256 encrypted server snapshots
    └── voldemort-backup-20260910.tar.gz.enc.sha256
```

---

## 🌐 4. API Endpoints & Dual Protocol Support

### Protocol A: Direct Cloudflare REST API (HTTP Bearer Auth)
Used by Python lightweight clients, CLI scripts, and Telegram bot without requiring heavy AWS SDK dependencies:
- **Base Endpoint**: `https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/r2/buckets/{BUCKET_NAME}/objects/{KEY}`
- **Upload (PUT)**:
  ```http
  PUT /client/v4/accounts/738f2def6189bcb43a3d5aae2347ca74/r2/buckets/voldemort-gallery/objects/flux/image.jpg HTTP/1.1
  Host: api.cloudflare.com
  Authorization: Bearer <CLOUDFLARE_R2_TOKEN>
  Content-Type: image/jpeg

  <BINARY_PAYLOAD>
  ```
- **Download (GET)**:
  ```http
  GET /client/v4/accounts/738f2def6189bcb43a3d5aae2347ca74/r2/buckets/voldemort-gallery/objects/flux/image.jpg HTTP/1.1
  Host: api.cloudflare.com
  Authorization: Bearer <CLOUDFLARE_R2_TOKEN>
  ```

### Protocol B: Standard S3-Compatible XML API (AWS SigV4)
Used by `boto3`, `rclone`, `@aws-sdk/client-s3`, or MinIO client:
- **S3 Endpoint**: `https://738f2def6189bcb43a3d5aae2347ca74.r2.cloudflarestorage.com`
- **Region**: `auto` (or `us-east-1` for strict SDK defaults)
- **Bucket**: `voldemort-gallery`

---

## 💻 5. Production Implementations & Code Snippets

### A. Python Native Uploader (Zero External Dependencies)

```python
import json
import urllib.request

ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "738f2def6189bcb43a3d5aae2347ca74")
R2_TOKEN = os.environ.get("CLOUDFLARE_R2_TOKEN")
BUCKET = os.environ.get("CLOUDFLARE_R2_BUCKET", "voldemort-gallery")

def upload_bytes_to_r2(payload: bytes, key: str, content_type: str = "image/jpeg") -> bool:
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/r2/buckets/{BUCKET}/objects/{key}"
    headers = {
        "Authorization": f"Bearer {R2_TOKEN}",
        "Content-Type": content_type
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("success", False)
    except Exception as e:
        print(f"R2 Upload Error: {e}")
        return False
```

### B. CLI Client (`~/.hermes/bin/cf-flux`)
The CLI script integrates AI generation and auto-cleaning:

```bash
# 1. Default: Auto-clean local disk, persist to R2 cloud
cf-flux "Swiss architectural minimalist poster"
# Output:
# ☁️ Cloudflare R2: voldemort-gallery/flux/flux_20260910_141630.jpg (Standard Storage)
# 🧹 Local Cache : Auto-Cleaned (Zero Disk Footprint)

# 2. Save explicitly to local destination:
cf-flux "Cyberpunk neon rain Tokyo" -o ./hero.jpg

# 3. Retain copy in ~/.hermes/image_cache/:
cf-flux "Minimalist black obsidian pyramid" --keep-local
```

### C. Telegram Menu Bot (`@Voldemort_menu_bot`)
- Generates image via Cloudflare Workers AI FLUX.1.
- In-memory upload to R2 (`voldemort-gallery/flux/flux_*.jpg`).
- Returns photo directly to user with R2 storage key badge.
- **Zero Disk Footprint**: Does not retain temporary files on VPS host.

---

## 🛡️ 6. Troubleshooting & Common Error Codes

| HTTP Status | Cloudflare Error Code | Root Cause | SRE Resolution |
|---|---|---|---|
| **403 Forbidden** | `10000` | API Token lacks `Workers R2 Storage > Edit` permission. | Re-generate token with `Account > Workers R2 Storage > Edit`. |
| **404 Not Found** | `10006` | Bucket name does not exist under this Account ID. | Verify bucket name matches `voldemort-gallery`. |
| **400 Bad Request** | `InvalidArgument` | Invalid authentication signature when hitting S3 endpoint. | Ensure SigV4 HMAC keys are used for S3 endpoint, or Bearer auth for REST endpoint. |
| **413 Payload Too Large** | `10018` | Single HTTP PUT payload exceeds 5 GB. | Use S3 Multipart Upload for files > 100 MB. |

---

## 📊 7. Economic Advantage & SRE Audit

1. **Zero Bandwidth / Egress Cost**: Unlike AWS S3 ($0.09/GB egress fee), Cloudflare R2 has **$0.00 / GB egress fee**.
2. **Standard Class Quotas (Free Tier)**:
   - **Storage**: 10 GB / month free.
   - **Class A Operations (Writes/Lists)**: 1,000,000 requests / month free.
   - **Class B Operations (Reads)**: 10,000,000 requests / month free.
3. **Disk Exhaustion Immunity**: Offloading media assets to R2 keeps the VPS root filesystem disk usage stable at **~27% (6.6 GB / 25 GB)**.
