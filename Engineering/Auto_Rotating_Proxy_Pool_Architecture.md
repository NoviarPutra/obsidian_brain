---
tags:
  - engineering/architecture
  - proxy
  - networking
  - sre
  - anti-bot
title: "🌐 Auto-Rotating Proxy Pool & Hybrid Residential Fallback Architecture"
date: "2026-09-16"
---

# 🌐 Auto-Rotating Proxy Pool & Hybrid Residential Fallback Architecture

> **Related**: [[Engineering/Index|⚡ Engineering MOC]] | [[Engineering/DevOps_Isolation_Policy|🔒 DevOps Isolation Policy]] | [[Home|🌌 Home]]

---

## 🧭 Executive Summary & Core Philosophy

Arsitektur proxy ini dirancang menggunakan prinsip **Ponytail (Lazy Senior Dev)**:
- **Cost-Efficiency**: 80-90% traffic berjalan di atas infrastruktur zero-cost (Tor multiplexed pool).
- **Separation of Concerns**: Scraping client (Puppeteer, Playwright, Python) hanya mengenal 1 entrypoint proxy (`http://127.0.0.1:8080`) tanpa perlu mengelola logic rotasi IP di level aplikasi.
- **Zero Host Pollution**: Seluruh stack terisolasi murni di Docker container di bawah `/home/voldemort/services/proxy-pool/`.
- **Security Hardened**: Binding strictly di `127.0.0.1` (localhost only) untuk mencegah open-proxy exploitation.

---

## 🏛️ System Topology

```
                  ┌───────────────────────────────────────────────────────────┐
                  │                 Scraping Clients                          │
                  │        (Playwright / Puppeteer / Python / cURL)           │
                  └─────────────────────────────┬─────────────────────────────┘
                                                │
                                                ▼ (HTTP / HTTPS CONNECT)
                                  ┌───────────────────────────┐
                                  │      HAProxy (Port 8080)  │
                                  │  Round-Robin Load Balancer│
                                  └─────────────┬─────────────┘
                                                │
                 ┌───────────────┬──────────────┼──────────────┬──────────────┐
                 │               │              │              │              │
                 ▼               ▼              ▼              ▼              ▼
           [Privoxy :8118] [Privoxy :8119] [Privoxy :8120] [Privoxy :8121] [Privoxy :8122]
                 │               │              │              │              │
                 ▼               ▼              ▼              ▼              ▼
           [Tor Node 1]    [Tor Node 2]   [Tor Node 3]   [Tor Node 4]   [Tor Node 5]
           (SOCKS :9052)   (SOCKS :9054)  (SOCKS :9056)  (SOCKS :9058)  (SOCKS :9060)
                 │               │              │              │              │
                 └───────────────┴───────┬──────┴──────────────┴──────────────┘
                                         │
                                         ▼
                            [Tor Public Exit Nodes (WAN)]
                                         │
                                         ▼
                           [Target Destination / API]
```

### Management & Telemetry
- **On-Demand Webhook API**: `POST http://127.0.0.1:8088/rotate` (Dispatches `SIGNAL NEWNYM` ke seluruh Tor control ports).
- **HAProxy SRE Metrics Dashboard**: `http://127.0.0.1:8089/stats` (Real-time monitoring worker health & throughput).

---

## 📂 Production Service Blueprint

Lokasi Deployment: `/home/voldemort/services/proxy-pool/`

### 1. `docker-compose.yml`
```yaml
services:
  haproxy:
    image: haproxy:2.8-alpine
    container_name: proxy-haproxy
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:8080" # Proxy Gateway
      - "127.0.0.1:8089:8089" # SRE Dashboard
    volumes:
      - ./haproxy/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
    depends_on:
      - tor-pool
    networks:
      - proxy-net

  tor-pool:
    build: ./tor-pool
    container_name: proxy-tor-pool
    restart: unless-stopped
    environment:
      - TOR_INSTANCES=5
      - ROTATION_INTERVAL=120
    ports:
      - "127.0.0.1:8088:8088" # Webhook API
    networks:
      - proxy-net

networks:
  proxy-net:
    name: proxy-net
    driver: bridge
```

### 2. `haproxy/haproxy.cfg`
```haproxy
global
    log stdout format raw local0 info
    maxconn 2048

defaults
    log global
    mode tcp
    timeout connect 10s
    timeout client 60s
    timeout server 60s

frontend stats
    mode http
    bind 0.0.0.0:8089
    stats enable
    stats uri /stats
    stats refresh 5s

frontend tor_front
    bind 0.0.0.0:8080
    mode tcp
    default_backend tor_back

backend tor_back
    mode tcp
    balance roundrobin
    default-server check inter 5s fall 2 rise 2

    server tor_node_1 tor-pool:8118 check
    server tor_node_2 tor-pool:8119 check
    server tor_node_3 tor-pool:8120 check
    server tor_node_4 tor-pool:8121 check
    server tor_node_5 tor-pool:8122 check
```

### 3. `tor-pool/entrypoint.sh`
Membangun N instances Tor & Privoxy secara dinamis saat container boot:
- Privoxy dikonfigurasi dengan `forward-socks5t` untuk memastikan seluruh query DNS di-resolve di exit relay (mencegah DNS leak lokal).

### 4. `tor-pool/rotator.py`
Daemon Python tanpa library eksternal (stdlib pure):
- Menjalankan background loop rotasi staggered setiap 120 detik.
- Mengexpose endpoint `POST /rotate` untuk instant IP renewal jika scraper mendeteksi block `403` / `429`.

---

## 🔍 Critical Reality Check & Gap Analysis

| Dimensi | Local Tor Rotating Pool | Commercial Residential (e.g. Maskify.su) |
| :--- | :--- | :--- |
| **Cost** | $0 (Free forever) | Pay-per-GB ($0.30 - $5 / GB) |
| **ASN Classification** | Datacenter / Tor Public Relays | ISP / Mobile Residential |
| **Bypass Turnstile / Datadome** | Rendah (Kerap kena infinite CAPTCHA) | Sangat Tinggi (Device rumahan asli) |
| **Throughput & Latency** | 500ms - 2500ms | 100ms - 400ms |
| **Data Privacy & Integrity** | 100% Bersih di server sendiri | Grey-market risk (reseller botnet / adware) |

---

## 🚀 The Hybrid Escalation Protocol (Recommended SRE Pattern)

Gunakan pola fallback cerdas di level kode aplikasi. Jangan buang kuota residential berbayar untuk request yang bisa diselesaikan secara gratis.

```
       [Request Baru]
             │
             ▼
    [Tier 1: Local Tor Pool]
             │
      Sukses? ──► YES ──► [Selesai / Return Data]
             │
            NO (HTTP 403 / Turnstile / CAPTCHA)
             │
             ▼
    [Tier 2: Maskify.su / Paid Residential]
             │
             ▼
     [Return Data]
```

### Production Implementation (Python `httpx`)
```python
import httpx
import time

LOCAL_PROXY = "http://127.0.0.1:8080"
LOCAL_ROTATE = "http://127.0.0.1:8088/rotate"
RESIDENTIAL_PROXY = "http://user:pass@gw.maskify.su:10000" # Fallback only

def resilient_scrape(url: str):
    # Phase 1: Zero-cost Tor attempt
    try:
        with httpx.Client(proxies=LOCAL_PROXY, timeout=10.0) as client:
            resp = client.get(url)
            if resp.status_code not in (403, 429) and "cf-turnstile" not in resp.text:
                return resp.text
    except Exception:
        # Trigger renewal for zombie circuit
        httpx.post(LOCAL_ROTATE)

    # Phase 2: Escalation to Residential Proxy
    print("[!] Escalating to Tier 2 Residential Proxy...")
    with httpx.Client(proxies=RESIDENTIAL_PROXY, timeout=20.0) as client:
        return client.get(url).text
```

---

## 🛡️ Anti-Leak Client Guardrails (Playwright & Puppeteer)

Ketika menggunakan browser automation dengan Tor, **wajib mematikan WebRTC** agar IP publik host tidak bocor via STUN query:

```javascript
// Puppeteer Hardened Flags
const browser = await puppeteer.launch({
  args: [
    '--proxy-server=http://127.0.0.1:8080',
    '--disable-webrtc',
    '--disable-features=WebRtcHideLocalIpsWithMdns',
    '--enforce-webrtc-ip-permission-check',
    '--no-sandbox'
  ]
});
```

---

## 🛠️ SRE Operations Cheat Sheet

```bash
# Cek kesehatan container
docker compose -f /home/voldemort/services/proxy-pool/docker-compose.yml ps

# Force renew seluruh IP seketika
curl -X POST http://127.0.0.1:8088/rotate

# Test rotasi IP via cURL
curl -s -x http://127.0.0.1:8080 https://api.ipify.org?format=json

# Monitoring status HAProxy & backend node
curl -s http://127.0.0.1:8089/stats
```
