---
tags:
  - engineering/mobile
  - flutter
  - performance
  - design-system
title: "Flutter ScreenUtil Plus v1.6.0 High-Performance Responsive Standard"
---

# Flutter ScreenUtil Plus v1.6.0 High-Performance Responsive Standard

> **Source**: https://pub.dev/packages/flutter_screenutil_plus (v1.6.0+)  
> **Target Persona**: `builder-mobile`, `reviewer`  
> **Core Mandate**: High-Performance, Zero Memory Waste, Const Preservation, 60 FPS Fluid Responsiveness.

---

## 1. Core Architecture & Mental Model

`flutter_screenutil_plus` (v1.6.0+) adalah evolusi modern dari screen utility Flutter yang mengintegrasikan:
1. **InheritedWidget Architecture (`ScreenUtilPlusScope`)**: Menghubungkan metrik layar ke context tree secara reaktif.
2. **Context-Aware Extensions**: Mengeliminasi ketergantungan singleton statis saat menggunakan granular rebuilds.
3. **RenderObject Responsive Widgets (`RSizedBox`, `RPadding`, `RContainer`, `REdgeInsets`)**: Menerapkan scaling di level render pipeline, memungkinkan preservasi kata kunci `const` pada widget tree Flutter.
4. **CSS-like Breakpoints & Size Classes**: Adaptasi layout multi-faktor (Mobile, Tablet, Desktop) tanpa hardcoded conditional checks.

---

## 2. High-Performance Best Practices

### A. Const Preservation with RenderObject Widgets
Saat menggunakan ekstensi biasa (`16.r`, `12.h`), kode berikut **kehilangan kata kunci `const`**:
```dart
// ❌ Suboptimal: Memaksa evaluasi instansiasi objek baru pada setiap frame rebuild
Padding(
  padding: EdgeInsets.all(16.r),
  child: SizedBox(height: 12.h),
)
```

**Standar Performa Tinggi `builder-mobile`**:
Gunakan `REdgeInsets` dan `RSizedBox` untuk mempertahankan deklarasi `const`. Kalkulasi skala ditangani di dalam `RenderPadding` dan `RenderConstrainedBox`:
```dart
// ✅ Optimal: Widget tree bersifat const, perhitungan terjadi di RenderObject
const RPadding(
  padding: REdgeInsets.all(16),
  child: RSizedBox.vertical(12),
)
```

### B. Targeted Rebuilds vs Global Tree Invalidation
- **`autoRebuild: true` (Default)**: Setiap perubahan `MediaQuery` (misalnya munculnya virtual keyboard) memicu rebuild seluruh widget tree di bawah `ScreenUtilPlusInit`.
- **`autoRebuild: false` (Targeted Mode)**: Widget tree tidak di-rebuild secara masif. Hanya widget yang secara eksplisit memanggil context extensions (`context.w()`, `context.h()`, `context.sp()`, `context.edgeInsets()`, atau `context.su`) yang akan di-rebuild via `ScreenUtilPlusScope`.

```dart
// Pola Context-Aware untuk granular reactivity
final width = context.w(120);
final height = context.h(48);
final padding = context.edgeInsets(horizontal: 16, vertical: 8);
```

### C. Defensive Typography (`spMin` vs `sp`)
Untuk mencegah *text overflow*, *clipping*, atau tombol terdorong keluar layar saat pengguna mengaktifkan font accessibility OS atau membuka layar lebar:
- Gunakan `context.spMin(14)` atau `14.spMin`.
- Formula `spMin` menjamin bahwa ukuran font **tidak akan pernah melebihi ukuran desain dasar**, menjaga keselarasan proporsi form dan interactive buttons.

```dart
Text(
  'MASUK KE AKUN',
  style: TextStyle(
    fontSize: context.spMin(14), // Mencegah overflow pada device density ekstrem
    fontWeight: FontWeight.w700,
  ),
)
```

### D. Interactive Touch Target Accessibility (>= 48dp)
Material Design & iOS Human Interface Guidelines mewajibkan target sentuh interaktif berukuran minimal 48x48 dp:
- Untuk widget visual kecil (misalnya Checkbox 24x24 dp atau mini icon 20x20 dp), jangan biarkan hit area hanya 24 dp.
- Bungkus dengan hit area transparan minimum 48x48 dp (`context.r(48)`):

```dart
SizedBox(
  width: context.r(48),
  height: context.r(48),
  child: Center(
    child: SizedBox(
      width: context.r(24),
      height: context.r(24),
      child: Checkbox(...),
    ),
  ),
)
```

---

## 3. Widget Testing Standard

Setiap pengujian widget (`testWidgets`) yang menyertakan komponen berbasis `flutter_screenutil_plus` **WAJIB**:
1. Dibungkus dengan `ScreenUtilPlusInit(designSize: const Size(390, 844), builder: ...)`.
2. Mengatur ukuran fisik viewport dan pixel ratio di `WidgetTester` untuk merefleksikan canvas desain Figma acuan:

```dart
void setupTestViewport(WidgetTester tester) {
  tester.view.physicalSize = const Size(390 * 3, 844 * 3);
  tester.view.devicePixelRatio = 3.0;
  addTearDown(() {
    tester.view.resetPhysicalSize();
    tester.view.resetDevicePixelRatio();
  });
}
```

---

## 4. Adversarial Audit Checklist (`reviewer`)

| No | Parameter | Syarat Lolos Audit | Tindakan Bila Gagal |
| :--- | :--- | :--- | :--- |
| 1 | **Import Canonical** | `package:flutter_screenutil_plus/flutter_screenutil_plus.dart` | REJECT |
| 2 | **Root Wrapper** | `ScreenUtilPlusInit` (Bukan `ScreenUtilInit`) | REJECT |
| 3 | **Zero Raw Double** | Tidak ada hardcoded double pada sizing/padding/margin/radius | REJECT |
| 4 | **Const Preservation** | Menggunakan `RSizedBox` / `REdgeInsets` untuk layout statis | WARN / REFACTOR |
| 5 | **Typography Guard** | Form & bounded buttons menggunakan `spMin` | REJECT jika berisiko overflow |
| 6 | **Touch Target** | Touch target interaktif >= 48dp | REJECT |
| 7 | **Test Harness** | Widget tests dibungkus `ScreenUtilPlusInit` + physicalSize | REJECT |
