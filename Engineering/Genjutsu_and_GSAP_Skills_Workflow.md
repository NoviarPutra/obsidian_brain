---
title: "Genjutsu & GSAP Creative Engineering Skills Engine"
tags:
  - ai/skills
  - ai/workflow
  - engineering/guidelines
  - genjutsu
  - gsap
  - ui-ux
  - motion-design
date: 2026-09-05
updated: 2026-09-05
type: reference
---

# 🎨 Genjutsu & GSAP Creative Coding & Motion Engine

Panduan komprehensif dan operasional untuk seluruh skill **Genjutsu** (Creative UI/UX, Motion, Anti-AI-Slop Visual Systems) dan **GSAP** (GreenSock Animation Platform) di ekosistem agen AI Kilo. Dokumen ini adalah **single source of truth** untuk standar implementasi animasi, interaksi mikro, dan visual design system lintas platform (Web, Jetpack Compose, SwiftUI).

---

## ⚡ 1. Filosofi & Core Directives

1. **Anti-AI-Slop Doctrine**:
   - Dilarang keras menghasilkan UI generik murahan: hindari gradient pelangi acak, glassmorphism berlebihan tanpa hierarki, atau layout "modern & sleek" klise.
   - Setiap elemen visual dan motion harus memiliki **Interaction Thesis** yang terarah dan fungsional.

2. **Performance First (60 FPS Non-Negotiable)**:
   - Gunakan selalu hardware-accelerated transforms (`transform`, `translate3d`, `opacity`, `scale`) bukan animasi layout properties (`width`, `height`, `top`, `left`, `margin`).
   - Prioritaskan zero-dependency native CSS jika kebutuhan motion sangat ringan, naikkan ke GSAP/Framer Motion hanya ketika dibutuhkan kontrol timeline atau fisika interaktif.

3. **Two-Register Communication**:
   - **Saat Eksekusi**: Narasi ringkas, percaya diri, light ninja flair ("*Scanning stack...*", "*Casting parallax on hero scroll.*").
   - **Saat Laporan / Deliverable**: 100% teknis, factual, plain, tanpa metafora (file paths, benchmark FPS, CLS/LCP impact).

---

## 🌀 2. Genjutsu Suite (The Illusionist & Painter)

Genjutsu terbagi menjadi dua pipeline utama: **`cast`** (enhancement) dan **`paint`** (brand new visual identity), didukung oleh 15 sub-modul (*jutsu*).

### 🛠️ Pipeline Selection Matrix

| Parameter | `/genjutsu:cast` | `/genjutsu:paint` |
|---|---|---|
| **Fokus Utama** | Mempercantik & menghidupkan UI yang sudah ada | Membangun visual universe dari nol |
| **Titik Masuk** | Adaptasi ke codebase & tech stack eksisting | Brainstorming art direction & token design |
| **Deliverable** | Smooth micro-interactions, spring animations, transitions | `MASTER.md`, design tokens (`tokens.css`), style guide |
| **Audit** | Fast smoke-test & motion check | Full comprehensive `design-audit` |
| **Default Trigger** | "animate this modal", "smooth scroll", "bikin snappy" | "from scratch", "design system baru", "visual identity" |

### 🥷 Katalog Sub-Modul (Jutsu Skills)

#### A. Web & Cross-Platform Engine
1. **`ui-ux-pro-max`**: Design system intelligence core (database terstruktur berisi 84 style visual, 192 palette warna, 74 font pairing, 99 pedoman UX, 25 jenis chart lintas 22 tech stack + CLI Python search engine).
2. **`css-native`**: Animasi modern zero-dependency (Scroll-Driven Animations, View Transitions API, `@starting-style`, CSS Houdini).
3. **`framer-motion`**: Motion orchestration untuk React/Next.js (`AnimatePresence`, layout animation, drag/gesture physics).
4. **`canvas-generative`**: Algorithmic & generative art di HTML5 Canvas 2D (partikel, flow fields, Perlin noise, fractals, L-systems).
5. **`threejs-r3f`**: WebGL 3D scenes, custom GLSL shaders, lighting, post-processing dengan Three.js & React Three Fiber.

#### B. Native Mobile & Platform Foundations
6. **`compose-motion`**: Jetpack Compose foundational animations (`animate*AsState`, `updateTransition`, `SharedTransitionLayout`).
7. **`compose-graphics`**: Advanced visual Compose (Material 3 Expressive motion physics, AGSL custom shaders Android 13+, `DrawScope` generative).
8. **`compose-multiplatform`**: Compose Multiplatform (KMP) shared UI, expect/actual composables, density & font scaling antar target (Desktop/Android/iOS).
9. **`swiftui-motion`**: Apple ecosystem motion (`withAnimation`, `matchedGeometryEffect`, `PhaseAnimator`, `KeyframeAnimator`, Spring physics).
10. **`swiftui-graphics`**: Metal shaders (`.colorEffect`, `.layerEffect`, `.distortionEffect`), iOS Liquid Glass, Canvas effects.

#### C. Experience & Interaction Principles
11. **`motion-principles`**: Standar fundamental motion design (easing curves, enter/exit hierarchy, durasi 150-400ms, reduced motion compliance).
12. **`mobile-principles`**: Ergonomi mobile (touch target min 48x48dp, thumb zone routing, safe area insets, no hover reliance).
13. **`desktop-principles`**: Desktop UX precision (keyboard shortcuts, multi-window focus, rich hover states, cursor interactions).
14. **`design-audit`**: Checklist review visual (motion gaps, WCAG 2.1 AA accessibility, contrast ratio, visual hierarchy, reflow jank).

---

## 💎 3. Deep Dive: `ui-ux-pro-max` (Design System Intelligence)

`ui-ux-pro-max` adalah sub-modul otak kecerdasan desain Genjutsu yang menyediakan rekomendasi instan, tokenisasi tema, dan validasi heuristik UX berbasis dataset CSV + CLI tool.

### 📊 Dataset Anatomy
- **84 Styles**: Neo-brutalism, Glassmorphism, Minimalist, Cyberpunk, Bento grid, Material You, iOS Liquid, dsb.
- **192 Color Palettes**: Semantic tokens (primary, surface, accent, destructive) dengan kalkulasi contrast WCAG teruji.
- **74 Font Pairings**: Kombinasi heading/body untuk berbagai persona produk (SaaS, Luxury, Editorial, Developer Tool).
- **99 UX Guidelines**: Aturan heuristik dengan prioritas ketat (P1 Accessibility & Touch -> P8 Charts).
- **22 Stacks Support**: React, Next.js, Vue, Nuxt, Svelte, Tailwind, Shadcn UI, SwiftUI, Compose, Flutter, Three.js, dsb.

### ⌨️ CLI Query & Intelligence Tools
Agen AI dapat mengeksekusi script query langsung di `~/.agents/skills/genjutsu/_jutsu/ui-ux-pro-max/scripts/`:
```bash
# Search UX guidelines atau style
python3 ~/.agents/skills/genjutsu/_jutsu/ui-ux-pro-max/scripts/search.py "dark mode contrast"

# Generate complete design system tokens untuk stack tertentu
python3 ~/.agents/skills/genjutsu/_jutsu/ui-ux-pro-max/scripts/design_system.py --stack react --style modern-saas
```

---

## 🟢 4. GSAP Suite (Official Animation Engine)

Paket resmi 8 skill terspesialisasi untuk orkestrasi animasi kelas industri dengan GreenSock Animation Platform.

### 📜 Katalog GSAP Skills

1. **`gsap-core`**
   - **Fungsi**: Dasar animasi tween (`gsap.to()`, `gsap.from()`, `gsap.fromTo()`), kurva easing (`power2.out`, `back.out`), staggers, default settings, dan responsive handling (`gsap.matchMedia()`).
   - **Kapan Digunakan**: Single tweens, animasi interaksi standar, pergerakan DOM/SVG sederhana.

2. **`gsap-timeline`**
   - **Fungsi**: Koreografi timeline multi-step (`gsap.timeline()`), position parameter control (`"<"`, `"-=0.2"`, `"+=0.5"`), nested timelines, sync label, dan reverse/scrub playback.
   - **Kapan Digunakan**: Sekuens animasi kompleks, multi-element orchestration, intro/outro scenes.

3. **`gsap-scrolltrigger`**
   - **Fungsi**: Animasi terikat scroll (*scroll-linked*), pin container, scrub physics, trigger callbacks, snapping sections, dan parallax.
   - **Kapan Digunakan**: Landing page interaktif, storytelling scroll, sticky header transitions, horizontal scroll sections.

4. **`gsap-react`**
   - **Fungsi**: Integrasi aman React/Next.js menggunakan hook resmi `@gsap/react` (`useGSAP()`), scoping refs container, pencegahan memory leak dengan auto-cleanup unmount, dan SSR guards.
   - **Kapan Digunakan**: Seluruh project React, Next.js (App/Pages Router), Remix.

5. **`gsap-frameworks`**
   - **Fungsi**: Integrasi siklus hidup (lifecycle hooks) non-React: Vue/Nuxt (`onMounted`/`onUnmounted`), Svelte/SvelteKit (`onMount`/`onDestroy`), serta Vanilla Web Components.
   - **Kapan Digunakan**: Pengembangan UI dengan Vue, Nuxt, Svelte, atau Astro.

6. **`gsap-plugins`**
   - **Fungsi**: Pemanfaatan plugin resmi: `Flip` (layout state morphing), `Draggable` (touch/mouse dragging & inertia), `ScrollToPlugin` (smooth scroll to anchor/coordinate), `ScrollSmoother`, `SplitText`, `CustomEase`.
   - **Kapan Digunakan**: Transformasi layout morphing kompleks, drag & drop UI, teks animasi karakter/kata.

7. **`gsap-performance`**
   - **Fungsi**: Optimasi 60 FPS bulletproof: wajib GPU-accelerated props (`x`, `y`, `scale`, `rotation`, `autoAlpha`), eliminasi layout thrashing, manajemen `will-change`, batching read/write layout.
   - **Kapan Digunakan**: Mengatasi jank, frame drop, animasi stuttering pada perangkat low-end.

8. **`gsap-utils`**
   - **Fungsi**: Helper matematika & utility: `gsap.utils.clamp()`, `mapRange()`, `interpolate()`, `random()`, `snap()`, `pipe()`, `toArray()`.
   - **Kapan Digunakan**: Pemetaan koordinat kursor, normalisasi value sensor/scroll, procedural random variation.

---

## 🎯 5. Decision Matrix: Kapan Pakai Apa?

```
Kebutuhan Visual / Motion
│
├──> Ingin desain sistem / visual identity baru dari nol?
│    └──> Jalankan `/genjutsu:paint` (query `ui-ux-pro-max` -> tokens -> MASTER.md -> audit)
│
├──> Ingin riset style, palette, typography, atau aturan UX?
│    └──> Query modul `ui-ux-pro-max` (via search.py / design_system.py)
│
├──> Ingin mempercantik komponen / halaman yang sudah ada?
│    └──> Jalankan `/genjutsu:cast`
│         ├──> Animasi CSS / Scroll sederhana -> `css-native`
│         ├──> React component transitions -> `framer-motion` atau `gsap-react`
│         ├──> Android Jetpack Compose UI -> `compose-motion` / `compose-graphics`
│         └──> Apple SwiftUI -> `swiftui-motion` / `swiftui-graphics`
│
└──> Kebutuhan Timeline Kompleks / Scroll Storytelling di Web?
     └──> Gunakan GSAP Suite:
          ├──> React / Next.js -> `gsap-react` + `useGSAP`
          ├──> Parallax / Scroll Pinning -> `gsap-scrolltrigger`
          ├──> Sekuens Banyak Elemen -> `gsap-timeline`
          └──> Morphing Layout / Drag -> `gsap-plugins` (Flip, Draggable)
```

---

## 🔒 6. Checklist Verifikasi Sebelum Deliver

- [ ] **FPS Benchmark**: Konstan 60 FPS tanpa jank di DevTools Performance panel.
- [ ] **Reduced Motion**: Mendukung `prefers-reduced-motion: reduce` (animasi dimatikan/disederhanakan untuk a11y).
- [ ] **Cleanup Guard**: Tidak ada listener scroll liar atau timeline yang tertinggal setelah unmount.
- [ ] **Zero AI Slop**: Desain kohesif, warna harmonis, tipografi terbaca jelas, kontras lolos standard WCAG AA.
