---
tags:
  - engineering
  - template
  - curriculum
  - pdf-generator
date: "2026-09-11"
title: "Technical Curriculum Module PDF Generator Engine"
---

# 📚 Technical Curriculum Module PDF Generator

> **Skill**: `curriculum-module-generator`  
> **Master Script**: `/home/voldemort/templates/curriculum_pdf_generator.py`  
> **Primary Role**: [[Draft|Draft (The Scribe)]]

---

## 🎯 Pedagogical Architecture: BDBF
Setiap modul kurikulum teknik wajib mengikuti formula **Breach-Deconstruct-Break-Fix (BDBF)**:
1. **Breach (Incident Study)**: Kasus riil pembobolan / kebocoran data di dunia industri (studi kasus kerugian finansial/reputasi).
2. **Deconstruction**: Pembedahan akar masalah teknis pada level protokol, byte stream, atau kernel.
3. **Break (Offensive Lab)**: Simulasi penetrasi langsung di terminal lab terisolasi.
4. **Fix (Defensive Hardening)**: Remediasi kode nyata (Pydantic validation, boundary delimiters, gVisor sandboxing).
5. **Proof of Work (Exit Ticket)**: Repositori proyek nyata dan uji otomatis sebelum peserta dinyatakan lulus.

---

## 🎨 Visual & Typography Engine Specs
- **Page Size**: A4 dengan margin seimbang `40pt` (Content width: `515pt`).
- **Running Header & Footer**: Two-pass canvas (`NumberedCanvas`) menghitung otomatis "Halaman X dari Y" dan garis batas tipis `#CBD5E1`.
- **Palette**:
  - Primary / Headings: Deep Navy Slate (`#0F172A`)
  - Accent / Subtitle: Royal Blue (`#2563EB`)
  - Breach Box: Background `#FEF2F2`, Border `#DC2626`
  - Break Box: Background `#FFFBEB`, Border `#D97706`
  - Fix Box: Background `#F0FDF4`, Border `#16A34A`
- **Zero-Tofu Enforced**: Bebas emoji mentah pada ReportLab canvas untuk mencegah glyph kotak hitam. Seluruh badge di-render via tag table geometris berlatar warna solid.

---

## 🚀 Cara Menghasilkan Modul Baru
Gunakan class `CurriculumPDFBuilder` dari `/home/voldemort/templates/curriculum_pdf_generator.py`:

```python
from curriculum_pdf_generator import CurriculumPDFBuilder

builder = CurriculumPDFBuilder(
    filename="/home/voldemort/Modul_2_Cloud_Native_Security.pdf",
    module_code="MODUL 2",
    title="CLOUD-NATIVE & CONTAINER SECURITY",
    subtitle="Kubernetes Exploitation, Container Breakout & eBPF Telemetry"
)

builder.add_header_block()
builder.add_meta_table([
    ["<b>Target Peserta:</b> Cloud Sec, SRE", "<b>Metodologi:</b> BDBF Framework"],
    ["<b>Rasio Belajar:</b> 30% Teori, 70% Lab", "<b>Standar:</b> CIS Kubernetes & NIST"],
    ["<b>Tech Stack:</b> K8s, Docker, Cilium, eBPF", "<b>Status:</b> Zero-Gap Certified"]
])

# Tambahkan Callouts
builder.add_callout_breach("Tesla Kubernetes Cryptojacking", "Deskripsi breach...")
builder.add_callout_break("Lab 2.1: Escape to Host via privileged container", "Langkah lab...")
builder.add_callout_fix("Mitigasi 2.1: Pod Security Standards & seccomp", "Cara patch...")

builder.save()
```
