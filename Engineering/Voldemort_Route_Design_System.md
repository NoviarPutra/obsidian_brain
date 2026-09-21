---
title: "Voldemort Route — Industrial Telemetry Design System Spec"
tags:
  - engineering/ui
  - design-system
  - voldemort-route
  - anti-ai-slop
  - svelte
date: 2026-09-20
---

# 📐 Voldemort Route — Industrial Telemetry Design System (Zero-Gap Spec)

Dokumen ini adalah spesifikasi desain antarmuka, token, komponen, dan interaksi untuk **Voldemort Route Web Dashboard & Control Plane** (Svelte 5 + Vite).

Menganut filosofi **Bauhaus Brutalism & Industrial Telemetry**: antarmuka diperlakukan layaknya instrumen avionik atau SCADA industri. Menolak segala bentuk klise *AI-slop* (efek glow ungu/cyan, rounded corner berlebih, animasi pegas lambat, dan dekorasi tanpa fungsi).

---

## 1. Core Visual Principles & Blacklist

### 🚫 Blacklist (Dilarang Keras):
1. **Zero Glassmorphism**: Dilarang menggunakan `backdrop-filter: blur()`, semi-transparent gradient cards, atau border frosted glass.
2. **Zero Radioactive / Cyberpunk Palettes**: Dilarang keras menggunakan kombinasi ungu neon (`#8B5CF6`), cyan radioaktif (`#06B6D4`), atau hot pink.
3. **Zero Organic / Bouncy Physics**: Dilarang menggunakan animasi elastis atau spring bounce (`framer-motion` style).
4. **Zero Rounded Bubble Cards**: Dilarang menggunakan border radius di atas `4px`.
5. **Zero Decorative Illustrations**: Dilarang menampilkan maskot 3D, ilustrasi kartun, atau gambar robot melayang.

### 📐 Mandatory Anchor:
1. **Instrument-Grade Information Density**: Menampilkan data sebanyak mungkin dalam ruang pandang tanpa mengorbankan keterbacaan (dense data packing).
2. **Functional Color Exclusivity**: Warna hanya digunakan sebagai indikator telemetri (kesehatan rute, tingkat latensi, peringatan keamanan).
3. **Monospaced Data Precision**: Seluruh angka, nilai numerik, tabel, metrik latensi, dan log wajib menggunakan font monospaced dengan fitur OpenType `tabular-nums`.

---

## 2. Design Tokens & CSS Variables

File CSS inti didefinisikan secara independen tanpa dependensi runtime CSS-in-JS (`src/ui/src/styles/tokens.css`):

```css
:root {
  /* Surface & Background Hierarchy */
  --vr-bg-base: #090D10;           /* Deep Obsidian Void */
  --vr-bg-surface: #0E141B;        /* Matte Industrial Slate */
  --vr-bg-surface-elevated: #131B24; /* Interactive/Hover Panel */
  --vr-bg-surface-sunken: #06090C;   /* Code blocks & Terminal sinks */

  /* Structural Borders (1px Sharp Solid) */
  --vr-border-subtle: #1A232E;     /* Panel dividers */
  --vr-border-strong: #2A3644;     /* Active card outlines & table headers */
  --vr-border-focus: #3B82F6;      /* Keyboard accessibility focus ring */

  /* High-Contrast Typographic System (WCAG AAA >= 7:1) */
  --vr-text-primary: #F0F4F8;      /* Primary labels & metrics (Contrast 17.5:1) */
  --vr-text-secondary: #94A3B8;    /* Field descriptions & table headers */
  --vr-text-muted: #64748B;        /* Timestamps & minor metadata */
  --vr-text-disabled: #334155;     /* Inactive elements */

  /* Telemetry Status Accents (Functional Semantics) */
  --vr-status-healthy: #10B981;    /* Emerald: Normal operations / HTTP 200 */
  --vr-status-healthy-bg: #064E3B; /* 15% opacity background tint */
  --vr-status-warning: #F59E0B;    /* Amber: Throttling / Rate-limited / Retrying */
  --vr-status-warning-bg: #78350F; /* 15% opacity background tint */
  --vr-status-critical: #EF4444;   /* Crimson: Circuit Open / Provider Down / Error */
  --vr-status-critical-bg: #7F1D1D;/* 15% opacity background tint */
  --vr-status-accent: #3B82F6;     /* Cobalt: Active compression / Selected state */
  --vr-status-accent-bg: #1E3A8A;  /* 15% opacity background tint */

  /* Spacing Scale (4px Baseline Grid) */
  --vr-space-1: 2px;
  --vr-space-2: 4px;
  --vr-space-3: 8px;
  --vr-space-4: 12px;
  --vr-space-5: 16px;
  --vr-space-6: 24px;
  --vr-space-7: 32px;
  --vr-space-8: 48px;

  /* Typography Scale */
  --vr-font-mono: 'JetBrains Mono', 'Geist Mono', ui-monospace, monospace;
  --vr-font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

  --vr-text-xs: 10px;  /* Micro tags & telemetry units */
  --vr-text-sm: 12px;  /* Standard UI text & table rows */
  --vr-text-md: 14px;  /* Panel headers & inputs */
  --vr-text-lg: 18px;  /* Section headers */
  --vr-text-xl: 24px;  /* Metric hero numbers */

  /* Strict Radii (No Bubbles) */
  --vr-radius-none: 0px;
  --vr-radius-sm: 2px; /* Focus rings & small tags only */
  --vr-radius-md: 3px; /* Input boxes & buttons */

  /* Transitions (Ultra-fast, Non-bouncy) */
  --vr-duration-instant: 0ms;
  --vr-duration-micro: 80ms;
  --vr-duration-normal: 150ms;
  --vr-ease-snappy: cubic-bezier(0, 0, 0.2, 1);
}
```

---

## 3. Component Specifications (Anatomy & Behavior)

### A. Telemetry Metric Card (Single Metric HUD)
- **Dimensi & Grid**: Tinggi tetap `88px`, padding `12px`.
- **Anatomy**:
  1. `Label Header`: 10px Monospace, Uppercase, warna `--vr-text-muted`, tracking `0.05em`.
  2. `Value Display`: 24px Monospace, Bold, Tabular Nums, warna `--vr-text-primary`.
  3. `Sub-Metric / Delta`: 10px Monospace, menampilkan trend (e.g. `+12.4%` atau `42ms p95`).
  4. `Border State`: 1px solid `--vr-border-subtle`. Jika status provider critical, border otomatis berubah ke `1px solid var(--vr-status-critical)`.
- **Zero Glassmorphism**: Background flat solid `--vr-bg-surface`.

### B. Live SSE Log Streamer (Terminal Drawer)
- **Performance Budget**: Mampu merender hingga 500 token/detik tanpa lag.
- **Rendering Strategy**:
  - Menggunakan **Virtual Windowing** (hanya 50 baris DOM yang dirender secara aktif).
  - Buffer in-memory maksimal 1,000 baris sebelum rotasi otomatis (*circular buffer*).
  - Background: `--vr-bg-surface-sunken` (`#06090C`).
  - Fitur: `Auto-Scroll Lock` (toggle button), `Grep Filter` input bar, dan `Latency Stamp` di tiap baris.

### C. Lightweight Routing Visualizer (Zero-Dependency SVG DAG)
- **Eliminasi Bloat**: Membuang library `@xyflow/react` (menghemat ~5 MB bundle size).
- **Implementasi**: Custom Svelte 5 SVG renderer berbasis algoritma Sugiyama sederhana:
  - Node Provider: Kotak persegi panjang berukuran `140x36px`, border 1px solid.
  - Connection Lines: Garis lurus patah (`stroke-width: 1.5px`, dashed saat standby, solid saat aktif).
  - Dynamic Pulse: Titik kecil 3px meluncur di sepanjang jalur SVG aktif untuk merepresentasikan aliran data secara real-time.

### D. Data Table (Dense Grid Standard)
- **Baris & Spasi**: Ketinggian baris `28px` (compact) atau `32px` (standard).
- **Header**: Sticky `top: 0`, background `--vr-bg-surface`, text 11px uppercase `--vr-text-secondary`, border-bottom 1px solid `--vr-border-strong`.
- **Alternating Rows**: Tanpa warna zebra stripes mencolok; hanya border horizontal 1px subtle `--vr-border-subtle`.
- **Hover State**: Warna latar berubah instan ke `--vr-bg-surface-elevated` (durasi 0ms).

---

## 4. Interaction & Motion Protocol

```
Tipe Aksi               Durasi       Easing                 Transformasi
────────────────────────────────────────────────────────────────────────────
Button Click / Active   0ms          None                   translateY(1px)
Dropdown / Menu Open    80ms         cubic-bezier(0,0,.2,1) opacity (0.9 -> 1)
Modal Backdrop          120ms        linear                 opacity (0 -> 1)
Card Hover Outline      80ms         linear                 border-color swap
SSE Token Arrival       0ms          None                   Direct text append
```

- **Per-Token Streaming Rendering**: Dilarang menerapkan efek transisi *fade-in* atau *typing animation cursor* pada setiap token streaming di dashboard. Teks langsung di-append ke DOM node secara raw demi efisiensi CPU.

---

## 5. Responsive Hierarchy & Viewports

```
Desktop HUD (>1280px)      Tablet / Split (768–1279px)  Mobile / Telegram MiniApp (<768px)
┌───────┬───────────────┐  ┌───────┬─────────────────┐  ┌─────────────────────────────┐
│ Side  │ HUD Metrics   │  │ Mini  │ HUD Metrics     │  │ [≡ Menu] Top Summary        │
│ Nav   ├───────────────┤  │ Nav   ├─────────────────┤  ├─────────────────────────────┤
│ 200px │ Providers &   │  │ 56px  │ Stacked Cards   │  │ Active Route Indicator      │
│       │ Routing Graph │  │ Icons ├─────────────────┤  ├─────────────────────────────┤
│       ├───────────────┤  │       │ Bottom Terminal │  │ Monospace Health Feed       │
│       │ Live Terminal │  │       │ Drawer          │  │ (Single Column Stack)       │
└───────┴───────────────┘  └───────┴─────────────────┘  └─────────────────────────────┘
```

1. **Desktop (>1280px)**: 3-Pane telemetry layout (Persistent Nav, Core Control Panel, Live Traffic/Error Terminal).
2. **Tablet (768px – 1279px)**: Collapsed icon navigation, auto-stacking metric cards.
3. **Mobile & Telegram MiniApp (<768px)**:
   - Single-column linear layout.
   - Header statis dengan status indikator LED tunggal.
   - 1-tap copyable endpoint URL dan API key display.
   - Mendukung penuh viewport webview Telegram tanpa horizontal scrolling.

---

## 6. Accessibility & High-Contrast Compliance

- **Contrast Validation (WCAG 2.2 AAA)**:
  - Teks Utama (`#F0F4F8`) di atas Latar Belakang (`#090D10`): Rasio **17.5:1** (Syarat AAA minimal 7:1).
  - Teks Muted (`#94A3B8`) di atas Surface (`#0E141B`): Rasio **7.8:1** (Memenuhi AAA).
  - Emerald Healthy (`#10B981`) di atas Surface: Rasio **8.2:1** (Memenuhi AAA).
- **Focus States**: Seluruh tombol, input, dan link interaktif memiliki outline keyboard fokus `2px solid var(--vr-border-focus)` dengan offset `2px`.
- **Zero Color-Only Signaling**: Setiap indikator status warna wajib disertai label teks atau ikon SVG eksplisit (e.g. Lingkaran Emerald + teks `HEALTHY` atau Segitiga Amber + teks `THROTTLED`), memastikan pengguna dengan keterbatasan penglihatan warna (color blindness) dapat mengoperasikan sistem secara akurat.
