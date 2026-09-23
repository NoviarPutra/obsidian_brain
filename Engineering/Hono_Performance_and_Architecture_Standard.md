---
tags:
  - engineering/standards
  - backend
  - hono
  - typescript
  - architecture
  - performance
title: "Hono Framework Architecture & Performance Maximization Standard"
---

# Hono Framework Architecture & Performance Maximization Standard

> **Document Scope**: Panduan arsitektur kanonikal, konvensi teknis, dan standar optimasi performa Hono (`hono.dev/docs/`) untuk squad backend (`builder-backend`, `query`, `analyst`, `scout`).

---

## 1. Core Architecture & Philosophy

Hono dirancang berbasis **Web Standards** (W3C/WHATWG) dengan prinsip **Zero External Dependencies**:
- **Pure Web API**: Menggunakan native `Request`, `Response`, `Headers`, `URL`, `ReadableStream`, dan Web Crypto API tanpa abstraksi vendor-lock atau library Node.js legacy (`IncomingMessage`/`ServerResponse`).
- **Unified Signature**: Seluruh aplikasi Hono mengekspos signature interface tunggal:
  ```ts
  app.fetch(request: Request, env?: Record<string, unknown>, executionCtx?: ExecutionContext): Response | Promise<Response>
  ```
- **Runtime Neutrality**: Satu codebase dapat berjalan identik pada Cloudflare Workers, Bun, Deno, Node.js (`@hono/node-server`), AWS Lambda, Fastly Compute, dan Vercel Edge.
- **Preset `hono/tiny`**: Bundle ukuran ultra-ringan (< 14 kB) untuk meminimalkan cold-start latency pada serverless edge isolates.

---

## 2. Routing Engine Mechanics & Deep Performance

Hono mengimplementasikan multi-engine routing architecture yang dipilih otomatis oleh `SmartRouter`:

### Engine Taxonomy & Characteristics

1. **`RegExpRouter` (Primary Engine - Ultra High Throughput)**:
   - Mengompilasi seluruh rute statis dan bertipe parameter ke dalam **satu Regular Expression monolitik** saat inisialisasi aplikasi.
   - Pencocokan berlangsung dalam waktu deterministik $\mathcal{O}(1)$ langsung di level native C++/Rust regex engine JavaScript runtime (V8, JavaScriptCore).
   - Parameter diekstrak melalui pre-computed offset mapping table tanpa parsing string berulang per-request.
2. **`TrieRouter` (Fallback Engine - Universal Compatibility)**:
   - Menggunakan struktur data Radix Trie ($\mathcal{O}(k)$ proporsional kedalaman segmen URL).
   - Menangani pola rute kompleks, overlapping wildcards, atau custom dynamic regex yang tidak dapat dikompilasi ke dalam single regex.
3. **`SmartRouter` (Adaptive Meta-Router)**:
   - Menguji kompabilitas rute pada fase bootstrap. Jika rute kompatibel, `RegExpRouter` digunakan; jika terdeteksi konflik ambiguitas, rute dialihkan otomatis ke `TrieRouter`.
4. **`LinearRouter` (Minimal Cold-Start)**:
   - Menggunakan iterasi array linear $\mathcal{O}(n)$. Meniadakan overhead fase kompilasi; ideal untuk fungsi serverless per-request cold execution.

### Rules to Guarantee `RegExpRouter` Compilation:
- **Daftarkan Rute Statis Mendahului Rute Dinamis**:
  ```ts
  // BENAR: Statis didaftarkan lebih dahulu
  app.get('/users/active', (c) => c.json({ status: 'active' }))
  app.get('/users/:id', (c) => c.json({ id: c.req.param('id') }))
  ```
- **Hindari Colliding Parameter Patterns pada Segmen yang Sama**:
  ```ts
  // SALAH (memicu fallback ke TrieRouter):
  app.get('/api/:id{[0-9]+}', handleNumber)
  app.get('/api/:slug{[a-z]+}', handleSlug)

  // BENAR (namespace terpisah, 100% RegExpRouter):
  app.get('/api/id/:id{[0-9]+}', handleNumber)
  app.get('/api/slug/:slug{[a-z]+}', handleSlug)
  ```
- **Gunakan Sub-Apps (`app.route`) untuk Modular Monolith**:
  `app.route('/prefix', subApp)` menggabungkan route tree langsung ke root router tanpa overhead proxy layer.

---

## 3. Context (`c`) Lifecycle & Asynchronous Execution

### Context Invariants:
- **Per-Request Scope**: Objek `c` (Context) diinstansiasi setiap HTTP tick dan dilepas ke Garbage Collector segera setelah response selesai dikirim.
- **Dilarang Menyimpan Objek `c` ke Global State**: Menyimpan referensi `c` ke array global atau asynchronous closure jangka panjang memicu severe memory leaks.
- **Lazy Evaluation**: `c.req.param()`, `c.req.query()`, dan headers di-parse secara *lazy* (hanya saat dibaca pertama kali, lalu di-cache pada internal dictionary per-request).
- **Single-Pass Stream Consumption**: `c.req.raw.body` adalah WHATWG `ReadableStream`. Pembacaan stream ganda tanpa kloning eksplisit (`c.req.raw.clone()`) akan melempar error stream terkunci (*locked stream*).

### Background Execution via `c.executionCtx.waitUntil`:
Tugas non-blocking (audit logging, metrics, invalidasi cache) wajib didelegasikan ke `waitUntil` agar tidak menahan Time-to-First-Byte (TTFB) klien:

```ts
app.post('/api/orders', async (c) => {
  const order = await orderService.createOrder(await c.req.json())

  // Delegasi tugas background tanpa menunda response HTTP
  if (c.executionCtx) {
    c.executionCtx.waitUntil(telemetryService.recordMetric('order_created', order.id))
  }

  return c.json({ success: true, orderId: order.id }, 201)
})
```

---

## 4. Server-Sent Events (SSE) & Streaming Hygiene

Gunakan modul resmi `hono/streaming`:
- **Mandatory `stream.onAbort()`**: Wajib mendaftarkan lifecycle teardown saat koneksi klien terputus guna membersihkan interval timer, database cursor, atau message broker subscription.

```ts
import { Hono } from 'hono'
import { streamSSE } from 'hono/streaming'

const app = new Hono()

app.get('/api/events', (c) => {
  return streamSSE(c, async (stream) => {
    let active = true

    stream.onAbort(() => {
      active = false
      console.log('Client disconnected, cleaning up stream resources.')
    })

    let id = 0
    while (active) {
      await stream.writeSSE({
        data: JSON.stringify({ tick: id++, time: Date.now() }),
        event: 'heartbeat',
        id: String(id),
      })
      await stream.sleep(1000)
    }
  })
})
```

---

## 5. Middleware Onion Architecture & Centralized Error Handling

### Middleware Execution Model:
- Kode sebelum `await next()` berjalan pada fase downstream (pre-handler).
- Kode setelah `await next()` berjalan pada fase upstream (post-handler/header mutation).
- Middleware dapat memutus rantai eksekusi (*short-circuiting*) dengan langsung mengembalikan objek `Response`.

### Recommended Middleware Suite:
```ts
import { Hono } from 'hono'
import { secureHeaders } from 'hono/secure-headers'
import { cors } from 'hono/cors'
import { timeout } from 'hono/timeout'
import { HTTPException } from 'hono/http-exception'

const app = new Hono()

// Security hardening
app.use('*', secureHeaders())

// Controlled CORS
app.use(
  '/api/*',
  cors({
    origin: ['https://app.domain.com'],
    allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowHeaders: ['Content-Type', 'Authorization'],
    credentials: true,
    maxAge: 86400,
  })
)

// SLA Guard: Timeout 5 detik
app.use(
  '/api/*',
  timeout(5000, () => new HTTPException(504, { message: 'Service Gateway Timeout' }))
)

// Centralized 404
app.notFound((c) => {
  return c.json({ code: 'NOT_FOUND', message: `Route ${c.req.path} not found` }, 404)
})

// Centralized Error Boundary
app.onError((err, c) => {
  if (err instanceof HTTPException) {
    return c.json(
      {
        code: 'HTTP_EXCEPTION',
        status: err.status,
        message: err.message,
      },
      err.status
    )
  }

  // Sentry / Logging internal
  console.error('[CRITICAL_UNHANDLED_ERROR]', err)

  return c.json(
    {
      code: 'INTERNAL_SERVER_ERROR',
      message: 'An unexpected internal error occurred',
    },
    500
  )
})
```

---

## 6. Type-Safe Validation & End-to-End RPC (`hc`)

### Validation dengan `@hono/zod-validator`:
- Validasi target spesifik: `json`, `query`, `param`, `header`, `form`.
- Data yang tervalidasi diakses secara type-safe via `c.req.valid('target')`.

### RPC Architecture (`hono/client`):
- Meniadakan code generator terpisah (seperti OpenAPI generator atau tRPC code-gen).
- Cukup ekspor tipe rantai rute: `export type AppType = typeof routes`.
- Front-end / consumer mengimpor `AppType` via `hc<AppType>` untuk mendapatkan full type completion (endpoints, query params, request bodies, response payloads, dan HTTP status codes).

```ts
// ==================== SERVER: api.ts ====================
import { Hono } from 'hono'
import { zValidator } from '@hono/zod-validator'
import { z } from 'zod'

const CreateUserSchema = z.object({
  username: z.string().min(3).max(32),
  email: z.string().email(),
  role: z.enum(['ADMIN', 'ENGINEER', 'ANALYST']),
})

const apiRoutes = new Hono()
  .post(
    '/users',
    zValidator('json', CreateUserSchema, (result, c) => {
      if (!result.success) {
        return c.json({ code: 'VALIDATION_ERROR', errors: result.error.flatten() }, 422)
      }
    }),
    async (c) => {
      const payload = c.req.valid('json')
      // Interface handoff ke query/repository layer
      const createdUser = { id: crypto.randomUUID(), ...payload, createdAt: Date.now() }
      return c.json(createdUser, 201)
    }
  )
  .get('/users/:id', async (c) => {
    const id = c.req.param('id')
    return c.json({ id, username: 'noviar', role: 'ENGINEER' as const }, 200)
  })

export type ApiRoutes = typeof apiRoutes
export default apiRoutes

// ==================== CLIENT: client.ts ====================
import { hc } from 'hono/client'
import type { ApiRoutes } from './api'

const client = hc<ApiRoutes>('https://api.omniroute.net')

// Full compile-time autocompletion & safety:
const response = await client.users.$post({
  json: {
    username: 'voldemort',
    email: 'voldemort@omniroute.net',
    role: 'ENGINEER',
  },
})

if (response.ok) {
  const user = await response.json() // Inferred type: { id: string; username: string; email: string; role: 'ADMIN' | 'ENGINEER' | 'ANALYST'; createdAt: number }
  console.log('User created:', user.id)
}
```

---

## 7. Runtime Deployment & Performance Tuning

### 1. Bun Production Tuning
Bun mengeksekusi Hono secara native tanpa adapter:
```ts
import app from './app'

export default {
  port: process.env.PORT || 3000,
  fetch: app.fetch,
  reusePort: true, // Kernel-level SO_REUSEPORT multi-process load balancing
}
```

### 2. Node.js (`@hono/node-server`) Production Tuning
- **Reverse Proxy Race Condition Fix**: Konfigurasi `keepAliveTimeout = 65000` dan `headersTimeout = 66000` (wajib lebih tinggi dari upstream reverse proxy Nginx/Traefik timeout yang biasanya 60 detik) untuk mencegah insiden `502 Bad Gateway / ECONNRESET`.
- **Graceful Shutdown**: Wajib menangani sinyal OS `SIGTERM` dan `SIGINT`.

```ts
import { serve } from '@hono/node-server'
import app from './app'

const server = serve(
  {
    fetch: app.fetch,
    port: 3000,
  },
  (info) => {
    console.log(`Hono server listening on http://localhost:${info.port}`)
  }
)

// Anti 502 Bad Gateway / ECONNRESET tuning
server.keepAliveTimeout = 65000
server.headersTimeout = 66000

// Graceful shutdown
const shutdown = () => {
  console.log('Initiating graceful shutdown...')
  server.close(() => {
    console.log('Server process terminated safely.')
    process.exit(0)
  })
}

process.on('SIGTERM', shutdown)
process.on('SIGINT', shutdown)
```

### 3. Cloudflare Workers Production Tuning
- Konfigurasi `placement: { mode: "smart" }` di `wrangler.jsonc` untuk auto-co-locating compute dekat dengan origin database.
- Hindari inisialisasi computational heavy di root global file agar cold start tetap instan (< 5 ms).
- Manfaatkan Web Cache API native via `hono/cache` untuk sub-request caching di level global CDN edge.

---

## 8. Memory Hygiene & Zero-Allocation Checklist

1. **Static Scope Constants**: Deklarasikan static headers, regex pattern, dan Zod schemas di level root module (di luar handler) agar tidak dialokasikan ulang pada setiap HTTP request tick.
2. **Strict Import Paths**: Selalu gunakan direct sub-path import (`import { cors } from 'hono/cors'`), dilarang menggunakan generic barrel import (`hono/middleware`) agar tree-shaking berjalan 100% optimal.
3. **No Unbounded Memory Caching**: Dilarang menggunakan in-memory Map sebagai cache tanpa eviction policy (LRU / TTL) pada proses long-running.
4. **Clean Stream Lifecycle**: Pasang `stream.onAbort()` pada setiap SSE / streaming response.
5. **Database Connection Safety**: Delegasikan seluruh operasi SQL / migrasi / query pool eksklusif ke `query` agent dengan connection pool terkendali (WAL mode untuk SQLite, pooled client untuk PostgreSQL/MySQL).
