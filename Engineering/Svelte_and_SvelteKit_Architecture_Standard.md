---
tags:
  - engineering/standards
  - frontend
  - svelte
  - sveltekit
  - typescript
  - architecture
  - performance
title: "Svelte 5 & SvelteKit 2+ Architecture and Performance Maximization Standard"
---

# Svelte 5 & SvelteKit 2+ Architecture and Performance Maximization Standard

> **Document Scope**: Panduan arsitektur kanonikal, konvensi teknis reaktivitas Runes (Svelte 5), file-based routing SvelteKit 2+, lifecycle teardown, mitigasi memory leak, dan optimasi performa murni untuk squad web (`builder-web`, `analyst`, `scout`, `reviewer`).

---

## 1. Core Reactivity & Runes Architecture (Svelte 5)

Svelte 5 beralih total dari reaktivitas berbasis compiler magic legacy (`let`, `$:`, `createEventDispatcher`, Svelte Stores) ke arsitektur **Fine-Grained Signals** berbasis **Runes**:
- **Bukan Virtual DOM**: Pembaruan DOM terjadi secara granular langsung ke simpul DOM target ($\mathcal{O}(1)$), mengeliminasi overhead rekonsiliasi VDOM dan tree diffing.
- **Universal Reactivity**: Reaktivitas tidak lagi terisolasi di dalam file komponen `.svelte`. Logika state reaktif dapat didefinisikan secara universal di dalam modul `.svelte.ts` atau `.svelte.js` menggunakan class atau factory functions murni.

### Runes Kanonikal & Penggunaan Presisi:

1. **`$state(initialValue)`**:
   - Membungkus objek atau array ke dalam deep reactive `Proxy`.
   - Mutasi properti langsung (`user.name = 'Dika'`) otomatis terdeteksi tanpa perlu assignment ulang referensi.
2. **`$state.raw(initialValue)` (High-Performance Shallow Reactivity)**:
   - Membuat referensi reaktif dangkal (*shallow*). Isi objek/array di dalamnya **tidak** dibungkus oleh `Proxy`.
   - Mengeliminasi alokasi ribuan proxy wrappers pada dataset besar (misal: 50.000 titik telemetri/grafik). Pembaruan hanya dipicu ketika seluruh referensi diganti (`points = newBatch`).
3. **`$derived(expression)` & `$derived.by(fn)`**:
   - Menghitung nilai turunan (*memoized computation*). Dievaluasi secara *lazy* dan di-cache hingga dependensi signal-nya berubah nilai secara nyata.
   - Gunakan `$derived.by` untuk blok logika multi-baris dengan percabangan kompleks.
4. **`$effect(fn)` (Client-Side Teardown)**:
   - Berjalan murni di client-side setelah DOM di-mount/di-render. **Tidak pernah berjalan di SSR**.
   - Wajib mengembalikan fungsi pembersih (*teardown callback*) jika menginisialisasi timer, listener DOM, atau stream network.
5. **`$effect.pre(fn)`**:
   - Berjalan tepat sebelum DOM dimutasi. Krusial untuk mengukur geometri elemen (scroll position, layout offset) sebelum layout berubah.
6. **`$props()` & `$bindable()`**:
   - Menggantikan `export let` legacy. Props dideklarasikan dengan destrukturisasi bertipe statis.
   - `$bindable()` menandai props yang diizinkan untuk two-way binding (`bind:value`).

---

## 2. Snippets & Typed Composition (Replacing Slots)

Svelte 5 menghapus `<slot />` dan `slot-scope` legacy demi **`Snippet<[...T]>`** dan **`{@render}`**:
- Menghilangkan *boilerplate* wrapper komponen.
- Menjamin *type safety* compile-time penuh pada parameter yang dilewatkan ke template anak.

```svelte
<!-- src/lib/components/DataGrid.svelte -->
<script lang="ts" generics="T">
  import type { Snippet } from 'svelte';

  interface Props {
    items: T[];
    row: Snippet<[item: T, index: number]>;
    emptyState?: Snippet;
  }

  let { items, row, emptyState }: Props = $props();
</script>

{#if items.length === 0 && emptyState}
  {@render emptyState()}
{:else}
  {#each items as item, i (i)}
    <div class="grid-row">
      {@render row(item, i)}
    </div>
  {/each}
{/if}
```

---

## 3. SvelteKit 2+ Architecture & Web Standards

SvelteKit 2+ beroperasi di atas native Web Platform (`Request`, `Response`, `FormData`, `Headers`, `fetch`).

### Directory Routing Hierarchy
```
src/routes/
├── +layout.svelte         # Shell UI global (Navbar, Footer)
├── +layout.server.ts      # Server session/auth loader untuk seluruh cabang anak
├── +page.svelte           # Page UI view
├── +page.server.ts        # Server-only load (direct DB/ORM access, secrets terisolasi)
├── +page.ts               # Universal load (berjalan di server & client saat navigasi)
├── +server.ts             # REST/Webhook endpoint handler (GET/POST/PUT/DELETE)
└── nodes/
    ├── +page.server.ts    # Node management actions & load
    └── +page.svelte
```

### Server Load Streaming (Zero TTFB Blocking)
Jangan biarkan query lambat (misal: agregasi statistik) memblokir rendering awal halaman. Kembalikan *unresolved Promise* dari server load dan tangani dengan `{#await}` di komponen:

```typescript
// src/routes/dashboard/+page.server.ts
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, depends }) => {
  depends('dashboard:stats');

  return {
    // Immediate data (di-await di server sebelum kirim HTML)
    user: await fetch('/api/me').then((r) => r.json()),
    // Non-blocking streaming promise (HTML langsung dikirim ke browser)
    heavyAnalytics: fetch('/api/analytics/yearly').then((r) => r.json())
  };
};
```

```svelte
<!-- src/routes/dashboard/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';
  let { data }: { data: PageData } = $props();
</script>

<h1>Welcome, {data.user.name}</h1>

{#await data.heavyAnalytics}
  <div class="skeleton">Loading long-range telemetry analytics...</div>
{:then analytics}
  <div class="chart-view">Total Events: {analytics.total}</div>
{:catch error}
  <div class="error-badge">Failed to load analytics: {error.message}</div>
{/await}
```

### Form Actions & Progressive Enhancement (`use:enhance`)
Formulir HTML standar berfungsi tanpa JavaScript (fallback 100% fungsional), dan diperkaya secara instan (*optimistic UI* & animasi) saat JS aktif:

```typescript
// src/routes/settings/+page.server.ts
import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions: Actions = {
  updateProfile: async ({ request, locals }) => {
    const formData = await request.formData();
    const username = formData.get('username')?.toString().trim();

    if (!username || username.length < 3) {
      return fail(422, { message: 'Username must be at least 3 characters', username });
    }

    // Eksekusi mutasi via query/repository layer
    return { success: true, updatedUsername: username };
  }
};
```

```svelte
<!-- src/routes/settings/+page.svelte -->
<script lang="ts">
  import { enhance } from '$app/forms';
  import { invalidateAll } from '$app/navigation';

  let isSubmitting = $state(false);
</script>

<form
  method="POST"
  action="?/updateProfile"
  use:enhance={() => {
    isSubmitting = true;
    return async ({ result, update }) => {
      isSubmitting = false;
      await update(); // Mengisi form value & status default SvelteKit
    };
  }}
>
  <input name="username" placeholder="New username" required />
  <button type="submit" disabled={isSubmitting}>
    {isSubmitting ? 'Saving...' : 'Update Profile'}
  </button>
</form>
```

---

## 4. Anti-Memory Leak & Lifecycle Teardown

### 1. Mandatory Cleanup di `$effect`
Setiap listener eksternal, interval waktu, subscription WebSocket, atau `AbortController` wajib dibersihkan di closure balik `$effect`:

```svelte
<script lang="ts">
  let { socketUrl }: { socketUrl: string } = $props();

  $effect(() => {
    const ws = new WebSocket(socketUrl);
    const controller = new AbortController();

    ws.onmessage = (event) => console.log('Socket message:', event.data);

    // Teardown dipanggil otomatis sebelum re-run atau saat unmount:
    return () => {
      ws.close();
      controller.abort();
    };
  });
</script>
```

### 2. SSR State Leakage Prevention (The Cross-User Leak Hazard)
- **Akar Masalah**: Pada Node.js/Bun server long-running, variabel mutable yang dideklarasikan di *module top-level* (luar fungsi load) dibagi bersama (*shared state*) di antara seluruh koneksi HTTP dari user yang berbeda.
- **DILARANG KERAS**:
  ```typescript
  // ⚠️ BAHAYA FATAL: State bocor antar user di SSR!
  let currentSession: SessionData | null = null;

  export const load = ({ locals }) => {
    currentSession = locals.session; // User B akan membaca session User A!
    return { session: currentSession };
  };
  ```
- **BENAR**:
  Simpan request-scoped data murni di `event.locals` pada `hooks.server.ts` atau lewat konteks hierarki komponen via `setContext()` dan `getContext()`.

---

## 5. Performance Maximization & Zero-Overengineering

| Aspek | Praktik Buruk (Overengineering & Lambat) | Standar Emas Svelte/SvelteKit (High Performance) |
| :--- | :--- | :--- |
| **State Management** | Menginstal Redux/Zustand atau membuat custom Store layer bertingkat. | Gunakan class TypeScript reaktif dengan Runes `$state` di file `.svelte.ts`. |
| **Dataset Besar** | Memasukkan 100.000 row data ke `$state([...])` (memicu ribuan alokasi deep Proxy). | Gunakan **`$state.raw([...])`** untuk shallow reactivity berkecepatan native. |
| **Navigasi Client** | Melakukan full page request atau menunggu klik tautan. | Tambahkan atribut **`data-sveltekit-preload-data="hover"`** pada `<body>` atau kontainer links. |
| **Data Fetching** | Menulis API controller manual di Express lalu fetch di `onMount` browser. | Gunakan **`+page.server.ts` `load`** dengan SSR langsung atau streaming Promise. |
| **Form Handling** | Memasang library form state eksternal yang rumit. | Gunakan native **HTML Forms + Form Actions + `use:enhance`**. |

---

## 6. SRE Production Deployment Checklist

1. **Preload Data on Hover**: Pasang `data-sveltekit-preload-data="hover"` pada `<body data-sveltekit-preload-data="hover">` di `app.html` untuk memangkas latensi navigasi ke zero perceptibility.
2. **Adapter Selection**:
   - Node.js (VPS/Docker): Gunakan `@sveltejs/adapter-node` dengan `ORIGIN=https://domain.com` untuk proteksi CSRF form submissions.
   - Cloudflare Workers/Pages: Gunakan `@sveltejs/adapter-cloudflare`.
   - Static/Client-Only SPA: Gunakan `@sveltejs/adapter-static` dengan `prerender = true`.
3. **Graceful Error Recovery**: Sediakan `+error.svelte` di root `src/routes/` agar uncaught error tidak menampilkan raw crash screen ke pengguna.
