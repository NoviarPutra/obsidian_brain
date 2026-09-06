---
title: "Anti-AI-Slop Visual Tuning & Image Generation Architecture"
tags:
  - ai/visual
  - visual/design
  - anti-ai-slop
  - design-system
  - guidelines
date: 2026-09-07
updated: 2026-09-07
type: reference
---

# 🎨 Anti-AI-Slop Visual Tuning & Image Generation Protocol

Dokumen ini adalah **single source of truth** untuk agen visual (`visual`) dan perancangan prompt/aset visual di ekosistem Kilo dan Hermes agar terbebas dari artefak klise/generik AI (*plastic look, oversaturated neon, cliché compositions*).

---

## 🚫 1. Hardcore Blacklist (Zero Tolerance)

| Kategori | Dilarang Keras (Banned Tropes) | Alasan / Dampak Buruk |
| :--- | :--- | :--- |
| **Cliché Buzzwords** | `"photorealistic"`, `"hyperrealistic"`, `"8k"`, `"octane render"`, `"unreal engine"`, `"masterpiece"`, `"trending on artstation"`, `"volumetric lighting"`, `"cinematic glowing lights"` | Memicu filter denoise murahan model AI, menghasilkan tekstur plastik dan highlight terlalu tajam. |
| **Radioactive Palettes** | Cyan + Magenta neon, purple cyber glows, oversaturated primary tones, unnatural glowing skin. | Menghancurkan hierarki visual UI dan terkesan seperti template murahan 2021. |
| **Cliché Compositions** | Bola sirkuit bercahaya di tengah, tangan robot menyentuh jari manusia, laptop melayang di ruang angkasa, background clutter tanpa fungsi. | Tidak memiliki nilai guna editorial, membingungkan pembaca, dan langsung terbaca sebagai AI generik. |

---

## 📐 2. Real-World Optical & Physical Anchoring

Setiap kali merancang prompt visual, agen wajib menyandarkan deskripsi pada **parameter optik dan fisika nyata**:

1. **Kamera & Lensa (Optical Glass)**:
   - Gunakan focal length presisi: `35mm f/1.8`, `50mm f/2 Leica Summicron`, `85mm f/1.4 medium format Hasselblad`.
   - Gunakan emulasi grain film nyata: `Kodak Portra 400 fine grain`, `Ilford HP5 Plus monochrome contrast`, `Fujifilm Pro 400H soft greens`.

2. **Pencahayaan Alami & Studio (Directional Lighting)**:
   - `North-facing diffused soft window daylight`
   - `Raking low-angle golden hour sunlight with elongated soft shadows`
   - `Single-source overhead softbox with matte diffusion flag`
   - `High-key minimalist editorial daylight`

3. **Materialitas & Tekstur Taktil (Tactile Surfaces)**:
   - `Uncoated 300gsm archival cotton paper with matte finish`
   - `Brushed natural anodized aluminum`
   - `Raw open-weave linen texture`
   - `Two-color risograph printing with subtle dot screen overlay`

---

## 🏛️ 3. Art Direction & Composition Discipline

1. **Aturan Ruang Negatif (>= 30% Negative Space)**:
   - Sisakan ruang kosong minimal 30–40% untuk penempatan tipografi editorial, header web, atau layout pernapasan.
2. **Disiplin Warna (Max 3 Tones)**:
   - 2 warna dominan harmonis (e.g. *Warm Brutalist Slate & Sand, Scandinavian Sage & Off-White*) + 1 aksen fungsional kontras.
3. **Gerakan Desain Kurasi**:
   - *Swiss Style / International Typographic Style*
   - *Bauhaus Minimalist Functionalism*
   - *Architectural Digest Minimalist Interior Photography*
   - *Contemporary Editorial Print & Risograph*
   - *Neo-Brutalist Flat Vector*

---

## 🛠️ 4. Asset Routing & Production

- **Agent Name**: `visual` (Kilo primary agent) & `hermes-visual` (diagrams/Excalidraw/video).
- **Target Folder**: `public/assets/images/` atau direct code (SVG / HTML5 Canvas).
- **Aspect Ratio Mapping**:
  - Web Hero Banner: `16:9` / `21:9`
  - Cards & Social Feed: `4:5` / `1:1`
  - Mobile Vertical: `9:16`
