---
title: Standalone Android Face Recognition & Anti-Spoofing Architecture (Zero Google ML Kit)
category: Architecture Blueprint
tags:
  - android
  - flutter
  - computer-vision
  - anti-spoofing
  - biometrics
  - security
date: "2026-09-13"
---

# 🛡️ Standalone Android Face Recognition & Anti-Spoofing Blueprint
> **Design Target**: 60 FPS, Zero Google Play Services (GMS/ML Kit) dependency, Enterprise/Custom ROM support, ISO/IEC 30107-3 compliant PAD (Presentation Attack Detection).

---

## 📌 Architectural Tenets (The Ponytail Mindset)
1. **Zero Google ML Kit Dependency**: App harus bisa jalan di non-GMS devices (Huawei HarmonyOS, enterprise warehouse tablets, AOSP custom ROMs) tanpa runtime crash.
2. **Native Deep Engine, Flutter Glass View**: Raw camera frames (`ImageProxy` / YUV420) **dilarang keras** menyeberang ke Dart VM / `MethodChannel`. Frame diproses on-device di native thread C++/Kotlin. Flutter hanya bertindak sebagai rendering canvas & event receiver via **Pigeon**.
3. **Multi-Layer Defense-in-Depth**: Menghadapi ancaman Level 1 (print/photo/display replay) dan Level 2 (3D mask, video injection, deepfake) tanpa mengorbankan UX dengan gerakan aktif yang menyebalkan (*active liveness*).

---

## 🏗️ End-to-End Processing Pipeline

```
[CameraX / NDK Camera2 Frame (YUV_420_888)]
                       │
                       ▼ (Zero Memory Copy in C++/Kotlin)
[Stage 0: Pre-filter Quality & Blur Engine]
  - Laplacian Variance (Blur rejection threshold: var < 100.0)
  - Ambient Luminance Check (Mean pixel intensity: 40 < Y < 220)
                       │ Passed
                       ▼
[Stage 1: Standalone Face Detector & 3D Mesh]
  - BlazeFace INT8 (Bounding box + 6 canonical landmarks) OR
  - MediaPipe FaceMesh (468 3D landmarks for monocular depth)
                       │ Crop & Canonical Affine Align (112x112 / 80x80)
                       ▼
[Stage 2: Passive FAS (Presentation Attack Detection)]
  - MiniFASNetV2 INT8 / Silent-Face (Dual-scale 2.7x + 4.0x crop)
  - Detects: Moiré pattern, print boundary, specular reflection
                       │ Liveness Score >= 0.92
                       ▼
[Stage 3: Physical Challenge-Response (Dynamic Screen Flash)]
  - Trigger Flutter fullscreen flash (Cyan -> Magenta: 250ms)
  - Verify corneal specular reflection & non-planar curvature change
                       │ Passed
                       ▼
[Stage 4: Feature Extraction & Embedding]
  - ArcFace / MobileFaceNet INT8 (512-D L2-normalized float vector)
                       │
                       ▼
[Stage 5: Verification & Anti-Replay Payload Sign]
  - 1:1 Verification: Cosine Similarity >= 0.70
  - Security Attestation: Sign (Embedding + Nonce + Timestamp) with Android Keystore TEE
```

---

## 🔬 Component Breakdown & Model Selection

| Phase | Model / Engine | Model Size (INT8) | Latency (NNAPI / GPU) | Role |
| :--- | :--- | :--- | :--- | :--- |
| **Detection** | **BlazeFace** (TFLite) | ~220 KB | ~4 - 6 ms | Ultra-light anchor-based face detection & 6-point pose alignment. |
| **Passive Liveness** | **MiniFASNetV2** (TFLite/ONNX) | ~2.8 MB | ~15 - 22 ms | Frequency-domain & spatial texture classification (Fake vs Genuine). |
| **Depth / Mesh** *(Optional)* | **MediaPipe FaceMesh** | ~3.2 MB | ~12 - 18 ms | Relative Z-depth monocular evaluation for curvature validation. |
| **Embedding** | **ArcFace MobileNetV3** | ~4.5 MB | ~18 - 25 ms | Generates robust 512-dimensional biometric feature embeddings. |

Total model package footprint: **< 10 MB** directly bundled in `assets/models/`.

---

## ⚡ IPC Contract: Pigeon Interface

Menghindari overhead serialisasi string `MethodChannel`:

```dart
// pigeons/face_auth_contract.dart
import 'package:pigeon/pigeon.dart';

@ConfigurePigeon(PigeonOptions(
  dartOut: 'lib/src/generated/face_auth_api.g.dart',
  kotlinOut: 'android/app/src/main/kotlin/com/example/app/FaceAuthApi.kt',
  kotlinOptions: KotlinOptions(package: 'com.example.app'),
))

enum FlashColor { cyan, magenta, white, off }

class FaceScanResult {
  double? livenessScore;
  List<double>? embedding; // 512 float vector
  bool isSpoof;
  String? error;
}

@FlutterApi()
abstract class FaceScannerCallbackApi {
  void onStatusHint(String message);
  void onTriggerFlash(FlashColor color);
  void onScanFinished(FaceScanResult result);
}

@HostApi()
abstract class FaceScannerNativeApi {
  void startCameraSession();
  void stopCameraSession();
}
```

---

## 🔒 Security & Anti-Camera-Injection Hardening

1. **Anti-Virtual Camera Injection (Hook Defense)**:
   - Evaluasi `CameraCharacteristics.LENS_FACING` dan metadata hardware device.
   - Deteksi dynamic hooking framework (Frida, Xposed, Substrate) pada symbol memory native level (`/proc/self/maps`).
   - Cek `android.hardware.camera2.CameraMetadata.REQUEST_AVAILABLE_CAPABILITIES_LOGICAL_MULTI_CAMERA` untuk memverifikasi sensor fisik riil.
2. **Hardware Attestation (TEE / Secure Enclave)**:
   - Private key di-generate di dalam `AndroidKeyStore` dengan flag `PURPOSE_SIGN` dan `FLAG_STRONG_BOX_BACKED` (jika hardware mendukung).
   - Embedding vector digabung dengan server-issued cryptographic nonce lalu di-sign di native level sebelum dikirim ke backend. Replay attack di network layer mustahil dilakukan.

---

## 📐 Vector Similarity Verification (1:1 Auth)

Formula komparasi vector di Flutter / Native:

$$\text{Similarity}(A, B) = \frac{\sum_{i=1}^{512} A_i \cdot B_i}{\sqrt{\sum_{i=1}^{512} A_i^2} \cdot \sqrt{\sum_{i=1}^{512} B_i^2}}$$

- **Score $\ge 0.70$**: Genuine Match (FAR $< 0.001\%$).
- **Score $< 0.70$**: Impostor Rejected.
