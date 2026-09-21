---
title: "Voldemort Route — Industrial Telemetry Design System (Tactile, Non-Monotonous & Anti-AI-Slop)"
tags:
  - engineering/ui
  - design-system
  - voldemort-route
  - anti-ai-slop
  - svelte
date: 2026-09-20
---

# 📐 Voldemort Route — Industrial Telemetry Design System (Zero-Gap)

Dokumen ini menetapkan spesifikasi desain antarmuka, token visual, komponen, dan interaksi untuk **Voldemort Route Web Dashboard & Control Plane** (Svelte 5 + Vite).

Menganut filosofi **Tactile Industrial Telemetry & Bauhaus Functionalism** (terinspirasi dari estetika perangkat keras audio presisi tinggi seperti *Nagra, Braun by Dieter Rams, dan Teenage Engineering* dipadukan dengan konsol avionik *Apollo Flight Telemetry*).

> **Arah Desain**: Anti-AI-Slop murni (tanpa blur murahan, tanpa gradien ungu/cyan neon) tetapi **Sama Sekali Tidak Monoton** (memiliki kedalaman visual taktil, tekstur mikro-grid terkalibrasi, aksen warna fungsional berkarakter, dan hierarki tipografi instrumen presisi).

---

## 1. Core Visual Principles & Hard Blacklist

### 🚫 Hardcore Blacklist (Zero Tolerance):
1. **Zero Fake Glassmorphism**: Dilarang menggunakan `backdrop-filter: blur()`, kartu semi-transparan buram yang membebani GPU, atau border frosted glass palsu.
2. **Zero Radioactive Cyberpunk**: Dilarang menggunakan warna ungu neon (`#8B5CF6`), cyan radioaktif (`#06B6D4`), atau hot pink gradien 2021.
3. **Zero Organic / Bouncy Physics**: Dilarang menggunakan animasi elastis membal (*spring bounce / rubber-band* ala aplikasi sosial media).
4. **Zero Rounded Bubble Cards**: Dilarang menggunakan border-radius di atas `4px` (bubble cards).
5. **Zero Flat Monotony**: Dilarang membuat antarmuka hanya berupa kotak hitam-putih polos tanpa kedalaman relief mekanikal dan hirarki taktilitas.

### 📐 Mandatory Aesthetics (Karakter Non-Monoton):
1. **Tactile Instrument Depth (Milled Metal Relief)**: Menggunakan border terukir (*milled bezel*) dengan kombinasi highlight atas 1px (`rgba(255,255,255,0.05)`) dan bayangan tegas bawah 1px (`rgba(0,0,0,0.6)`), memberikan sensasi panel fisik rack-mount server atau synth hardware.
2. **Subtle Phosphor Matrix Grid**: Latar belakang panel kerja memiliki pola grid titik mikroskopis (`radial-gradient` 1px dengan jarak 16px, opasitas 3%) yang memberi dimensi ruang tanpa mengganggu keterbacaan data.
3. **High-Density Avionics Typography**: Mengombinasikan font monospaced angka tabular (`tabular-nums`) untuk data metrik dengan label sans-serif teknikal DIN/Grotesk untuk navigasi.
4. **Oscilloscope Step-Line Metrics**: Grafik telemetri tidak menggunakan kurva bezier meliuk-liuk yang tidak realistis, melainkan step-line grafis (`step-after`) bergaya osiloskop laboratorium presisi tinggi.

---

## 2. Design Tokens & CSS Variables (`tokens.css`)

```css
:root {
  /* Surface Palette (Tactile Obsidian & Milled Metal) */
  --vr-bg-void: #070A0D;            /* Ruang terdalam chassis */
  --vr-bg-base: #0B0F14;            /* Background utama aplikasi */
  --vr-bg-panel: #111720;           /* Surface kartu instrumen (Matte Metal) */
  --vr-bg-panel-hover: #17202B;     /* State hover terkalibrasi */
  --vr-bg-panel-sunken: #06080B;    /* Area sink / code editor / log terminal */
  --vr-bg-subtle-grid: radial-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 0);

  /* Bezel & Structural Borders (Milled Edge Relief) */
  --vr-border-subtle: #1C2633;      /* Divider struktural */
  --vr-border-strong: #2B3A4D;      /* Garis luar panel aktif */
  --vr-border-highlight: rgba(255, 255, 255, 0.07); /* Bezel highlight atas */
  --vr-border-shadow: rgba(0, 0, 0, 0.7);           /* Bezel bayangan bawah */
  --vr-border-focus: #F59E0B;       /* Keyboard focus amber ring (Industrial) */

  /* Typographic System (WCAG 2.2 AAA Compliant) */
  --vr-text-primary: #F4F7FA;       /* Kontras 17.8:1 terhadap bg-base */
  --vr-text-secondary: #94A3B8;     /* Kontras 8.1:1 terhadap bg-panel */
  --vr-text-muted: #5B6B7F;         /* Label sekunder & timestamps */
  --vr-text-dim: #384656;           /* Garis bantu & unit non-aktif */

  /* Functional Telemetry Spectrum (Karakter Warna Berdaya Guna) */
  --vr-color-emerald: #10B981;      /* Normal Route / HTTP 200 / 99.9% Uptime */
  --vr-color-emerald-glow: rgba(16, 185, 129, 0.15);
  --vr-color-amber: #F59E0B;        /* Throttling / Rate-Limit Queue / Standby */
  --vr-color-amber-glow: rgba(245, 158, 11, 0.15);
  --vr-color-crimson: #F43F5E;      /* Circuit Breaker Open / Provider Dead */
  --vr-color-crimson-glow: rgba(244, 63, 94, 0.18);
  --vr-color-cobalt: #3B82F6;       /* Active Compression / Context Token Savings */
  --vr-color-cobalt-glow: rgba(59, 130, 246, 0.15);
  --vr-color-tangerine: #FF6B00;    /* Air-Gap Local Fallback Active (Ollama) */
  --vr-color-tangerine-glow: rgba(255, 107, 0, 0.18);

  /* Spacing Scale (4px Baseline Grid System) */
  --vr-sp-1: 2px;
  --vr-sp-2: 4px;
  --vr-sp-3: 8px;
  --vr-sp-4: 12px;
  --vr-sp-5: 16px;
  --vr-sp-6: 24px;
  --vr-sp-7: 32px;
  --vr-sp-8: 48px;

  /* Typography Scales */
  --vr-font-mono: 'JetBrains Mono', 'Geist Mono', SFMono-Regular, monospace;
  --vr-font-label: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

  --vr-size-micro: 10px;  /* Telemetry tags, units, status pills */
  --vr-size-data: 12px;   /* Standard table cells, log entries */
  --vr-size-ui: 13px;     /* Button labels, dropdown items */
  --vr-size-header: 15px; /* Panel titles, section headers */
  --vr-size-hero: 26px;   /* Metric numbers (bold tabular-nums) */

  /* Bevel & Radius */
  --vr-radius-sharp: 0px; /* Data tables, code blocks */
  --vr-radius-panel: 2px; /* Metric panels & modals */
  --vr-radius-pill: 3px;  /* Status badges & interactive toggles */

  /* Mechanical Transitions */
  --vr-dur-instant: 0ms;
  --vr-dur-snap: 75ms;
  --vr-dur-normal: 120ms;
  --vr-ease-mechanical: cubic-bezier(0, 0, 0.15, 1);
}
```

---

## 3. Component Anatomy & Mechanical UI Patterns

### A. The Telemetry HUD Metric Card
- **Dimensi**: Height `92px`, padding `12px 14px`.
- **Relief Taktil**:
  ```css
  background: var(--vr-bg-panel);
  border-top: 1px solid var(--vr-border-highlight);
  border-left: 1px solid var(--vr-border-subtle);
  border-right: 1px solid var(--vr-border-subtle);
  border-bottom: 2px solid var(--vr-border-shadow);
  border-radius: var(--vr-radius-panel);
  ```
- **Struktur Konten**:
  - `Header Line`: Ikon LED status kecil 6px (berwarna solid sesuai kondisi) + Label teks 10px Uppercase tracking `0.06em` (`--vr-text-secondary`).
  - `Main Number`: Font monospace 26px Bold dengan `font-variant-numeric: tabular-nums` (`--vr-text-primary`).
  - `Sub-Line`: Delta trend (misal: `▲ 89.2% saved`) dengan warna aksen fungsional yang relevan + p95 latency counter.

### B. Hardware-Feel Toggle Switch (Physical Rocker Switch)
- Menggantikan switch bulat generic bergaya iOS.
- **Visual**: Tombol rocker persegi panjang berukuran `36px x 18px` dengan relief bevel ganda.
- **Status ON**: Panel dalam menyala dengan warna latar fungsional (e.g. Amber atau Cobalt) dengan inset box-shadow tegas (`inset 0 1px 2px rgba(0,0,0,0.8)`).
- **Status OFF**: Panel dalam berwarna abu-abu gelap mekanis (`#0F141C`) dengan posisi switch di sebelah kiri.

### C. Live Terminal Log Drawer & Oscilloscope Streamer
- Area sink monospaced berlatar `--vr-bg-panel-sunken` (`#06080B`) dengan border atas 1px solid `--vr-border-strong`.
- **Virtual Windowing**: Hanya me-render 60 baris DOM aktif pada viewport untuk mempertahankan frame rate 60 FPS pada throughput 500 token/detik.
- **Controls Bar**:
  - `Auto-Scroll Lock`: Tombol persegi bertuliskan `[LOCK AUTO-SCROLL]` dengan status LED aktif.
  - `Grep Input`: Input bar monospaced dengan prefix prompt `grep >` tanpa border rounded.
  - `Throughput Gauge`: Mini visual bar meter bergaya VU-meter analog yang mengindikasikan beban token/detik.

### D. Lightweight Native SVG DAG Visualizer (Pengganti @xyflow/react)
- **Eliminasi Bloat**: Menghilangkan 5 MB dependensi React Flow dengan custom Svelte 5 SVG engine (<15 KB).
- **Node Taktil**: Persegi panjang berdimensi `144px x 40px` dengan border tajam 1px.
- **Connection Pipeline**: Garis orthogonal (patah 90 derajat) dengan warna `--vr-border-strong`.
- **Packet Pulse Effect**: Titik LED mikro 3px bergerak mulus di sepanjang jalur yang sedang aktif menyalurkan request HTTP, memberikan visibilitas langsung terhadap rute provider yang sedang melayani traffic.

### E. Status Indicators (Multi-State Signals)
Setiap status wajib memadukan warna + simbol bentuk geometris (memenuhi kepatuhan *Colorblind Accessibility*):
- `[●] HEALTHY`: Lingkaran solid Emerald (`#10B981`)
- `[▲] THROTTLED`: Segitiga solid Amber (`#F59E0B`)
- `[■] CIRCUIT OPEN`: Kotak solid Crimson (`#F43F5E`)
- `[✦] AIR-GAP LOCAL`: Diamond solid Tangerine (`#FF6B00`)
- `[◆] COMPRESSION`: Segienam Cobalt (`#3B82F6`)

---

## 4. Responsive Hierarchy & Multi-Device Adaptive Layout

```
Desktop Master HUD (>1280px)
┌───────────┬─────────────────────────────────────────────────────────────┐
│ Side Rail │ Top Bar: Global Status LED | Virtual Keys | Token Ledger    │
│ 180px     ├───────────────────────────────┬─────────────────────────────┤
│ Modular   │ Metric HUD (4 Grid Cards)     │ Routing DAG Visualizer      │
│ Iconic    ├───────────────────────────────┴─────────────────────────────┤
│ & Labels  │ Data Matrix: Active Providers, Combos & Failover Priority   │
│           ├─────────────────────────────────────────────────────────────┤
│           │ Virtualized Live Log Terminal Drawer (Collapsible)          │
└───────────┴─────────────────────────────────────────────────────────────┘

Tablet HUD (768px – 1279px)
┌─────┬───────────────────────────────────────────────────────────────────┐
│ 52px│ Top Bar: Global Summary & Emergency Circuit Kill Switch           │
│ Rail├───────────────────────────────────────────────────────────────────┤
│ Icon│ 2x2 Metric HUD Grid -> Active Provider Stack -> Terminal          │
└─────┴───────────────────────────────────────────────────────────────────┘

Mobile & Telegram WebApp (<768px)
┌─────────────────────────────────────────────────────────────────────────┐
│ ⚡ VOLDEMORT ROUTE [● HEALTHY] [≡ MENU]                                  │
├─────────────────────────────────────────────────────────────────────────┤
│ Active Route: Anthropic Claude-3.5-Sonnet via OpenRouter                │
│ Spend: $2.40 / $10.00 [████░░░░░░░░] 24%                                │
├─────────────────────────────────────────────────────────────────────────┤
│ [ 1-Tap Copy Endpoint: https://127.0.0.1:20128/v1 ]                     │
├─────────────────────────────────────────────────────────────────────────┤
│ Single Column Monospace Telemetry Feed                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Performance Budget & Rendering Rules

1. **Zero CSS-in-JS Calculation**: Seluruh styling dieksekusi via CSS custom variables yang dikompilasi statis saat build time.
2. **DOM Update Batching**: Saat stream token tiba dengan kecepatan tinggi, update DOM pada log terminal dan byte counters dibatch menggunakan `requestAnimationFrame` untuk menghindari layout thrashing.
3. **Total CSS Bundle Cap**: Ukuran total CSS produksi (minified + gzipped) dibatasi ketat di bawah **45 KB**.
4. **Zero Layout Shift (CLS = 0)**: Seluruh metric card dan visualizer DAG memiliki dimensi `min-height` dan `aspect-ratio` eksplisit untuk mencegah pergeseran tampilan saat data telemetri pertama kali dimuat.
