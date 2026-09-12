# Blueprint Arsitektur: Multi-Account Worker Farm Engine

> **Status**: Archived / Backlog Design  
> **Date**: 2026-09-12  
> **Tags**: #architecture #bot #worker #anti-detect #automation #python

---

## 1. Overview & Objective
Sistem orkestrasi worker otomatis untuk multi-account automation (farming/ternak akun) dengan prioritas utama:
- **Zero-Ban Rate**: Isolasi fingerprint dan network routing.
- **Resource Efficiency**: Pilihan engine ringan (API-level TLS impersonation) vs real browser sandbox.
- **Modularity**: Worker independen berbasis task queue & state machine.

---

## 2. Pilihan Arsitektur Worker

### A. Lightweight API Worker (`curl_cffi` / TLS Impersonation)
- **Footprint**: ~30–50 MB RAM per instance (bisa jalanin ratusan akun per VPS).
- **Mekanisme**: Bypass TLS JA3/JA4 & HTTP/2 frame fingerprinting langsung ke internal REST/GraphQL endpoints tanpa render layout/DOM.
- **Use Cases**: Daily check-in, token claiming, faucet, checking status, polling updates, auto-fwd.

### B. Heavyweight Browser Sandbox (Playwright Stealth / Camoufox)
- **Footprint**: ~200–400 MB RAM per instance (butuh cgroups/Docker resource limit ketat).
- **Mekanisme**: Real Chromium/Firefox dengan spoofed canvas, WebGL vendor, WebRTC, audio context, fonts, dan timezone profile.
- **Use Cases**: Registrasi akun baru, bypass Cloudflare Turnstile / reCAPTCHA v3, platform dengan evaluasi mouse movement bezier (behavioral analysis).

---

## 3. 4 Pilar Anti-Detect (Zero-Ban Framework)
1. **Proxy Binding (Strict Sticky IP)**: 1 Akun = 1 Dedicated Residential / 4G Mobile Proxy. Larang keras IP hopping antar sesi.
2. **Device Fingerprint Isolation**: Tiap akun memiliki metadata tersimpan (User-Agent, Viewport, Storage, Cookie Jar, Hardware Concurrency).
3. **Non-Linear Gaussian Jitter**: Hindari `sleep()` statis. Gunakan random delay berdistribusi normal (`random.gauss(mean, std)`) untuk menyerupai perilaku manusia.
4. **State Machine & Queue**: Dispatcher menggunakan Redis/RQ atau Asyncio Semaphore dengan state lifecycle: `IDLE` -> `RUNNING` -> `COOLDOWN` -> `ERROR` / `BANNED`.

---

## 4. Scaffold Implementasi Awal (Python Asyncio)

```python
import asyncio
import random
from dataclasses import dataclass
from typing import Optional
from curl_cffi.requests import AsyncSession

@dataclass
class AccountProfile:
    account_id: str
    proxy_url: Optional[str]      # Format: http://user:pass@ip:port
    user_agent: str
    session_cookies: dict
    auth_token: Optional[str] = None
    is_active: bool = True

class FarmWorker:
    def __init__(self, profile: AccountProfile):
        self.profile = profile
        self.session: Optional[AsyncSession] = None

    async def init_session(self):
        self.session = AsyncSession(
            impersonate="chrome124",
            proxies={"http": self.profile.proxy_url, "https": self.profile.proxy_url} if self.profile.proxy_url else None,
            timeout=30
        )
        self.session.headers.update({
            "User-Agent": self.profile.user_agent,
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"'
        })
        if self.profile.session_cookies:
            self.session.cookies.update(self.profile.session_cookies)

    async def random_jitter(self, min_sec: float = 3.0, max_sec: float = 8.0):
        await asyncio.sleep(random.uniform(min_sec, max_sec))

    async def execute_task(self, task_name: str, payload: dict) -> dict:
        try:
            await self.random_jitter()
            # Action execution logic
            return {"success": True, "task": task_name, "account_id": self.profile.account_id}
        except Exception as e:
            return {"success": False, "error": str(e), "account_id": self.profile.account_id}

    async def close(self):
        if self.session:
            await self.session.close()
```

---

## 5. Next Discussion Checklist (Pending Inputs)
- [ ] Penentuan target platform spesifik.
- [ ] Pemilihan skema database akun (SQLite vs PostgreSQL vs JSON).
- [ ] Tipe proxy yang akan digunakan (Rotating vs Sticky Mobile/Residential).
- [ ] Orchestration layer (Standalone Python CLI vs Celery / Redis Queue vs Docker Compose).
