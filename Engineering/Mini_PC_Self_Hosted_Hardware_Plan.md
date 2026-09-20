---
tags:
  - engineering/hardware
  - infrastructure
  - sre
  - homelab
title: "🖥️ Mini PC Self-Hosted Infrastructure & Hardware Migration Plan"
date: "2026-09-20"
---

# 🖥️ Mini PC Self-Hosted Infrastructure & Hardware Migration Plan

> **Related**: [[Engineering/Index|⚡ Engineering MOC]] | [[Engineering/DevOps_Isolation_Policy|🔒 DevOps Isolation Policy]] | [[Home|🌌 Home]]

---

## 🧭 Executive Summary & Baseline

Dokumen ini memuat spesifikasi teknis, evaluasi komparatif, dan panduan pengadaan hardware Mini PC untuk migrasi atau penambahan node on-premise mandiri yang menggantikan/melengkapi workload **vps-voldemort**.

### Baseline vps-voldemort (Cloud Production Reference)
- **vCPU**: 2 vCPU (Intel Broadwell architecture, x86_64)
- **RAM**: 4.0 GB (3.8 GiB usable + 2.0 GB Swap)
- **Storage**: ~60 GB SSD (NVMe / Virtual Block Device)
- **Workload**: 24/7 continuous operation, Docker containers (Telegram bots, OmniRoute LLM proxy router, Obsidian Sync stack, background daemons).

---

## 📊 Komparasi Tiering Mini PC

### 1. Tier Entry: Ultra-Budget & Fanless Node (1:1 VPS Replacement)
- **Model**: Dell Wyse 5070 / HP T630 (Refurbished Thin Client)
- **CPU**: Intel Celeron J4105 (4C/4T, base 1.5 GHz, boost up to 2.5 GHz, Goldmont Plus)
- **RAM**: 8 GB DDR4 SODIMM
- **Storage**: 128 GB - 256 GB M.2 SATA SSD
- **Rentang Harga**: Rp 950.000 – Rp 1.450.000
- **Kelebihan**:
  - Fanless design: 100% senyap, bebas sirkulasi debu, durabilitas tinggi untuk operasi nonstop.
  - Sangat hemat listrik: Idle ~4W - 6W, full load ~12W.
  - Solusi termurah untuk arsitektur x86_64 dedicated.
- **Kekurangan**:
  - IPC rendah, kurang memadai untuk compile atau task CPU-heavy.
  - Terbatas pada jalur storage SATA (bukan NVMe kecepatan tinggi).

---

### 2. Tier Sweet Spot SRE: Intel Alder Lake-N (Rekomendasi Utama)
- **Model**: GMKtec NucBox G3 / Beelink Mini S12 Pro
- **CPU**: Intel N100 12th Gen (4C/4T Gracemont cores, up to 3.4 GHz, 6W TDP)
- **RAM**: 16 GB DDR4 3200MHz SODIMM (1 slot)
- **Storage**: 512 GB M.2 NVMe PCIe 3.0 SSD
- **Networking**: 1x 2.5GbE LAN (GMKtec G3) / 1GbE LAN (Beelink S12), WiFi 6, Bluetooth 5.2
- **Rentang Harga**:
  - Barebone: Rp 1.600.000 – Rp 1.850.000
  - Konfigurasi Siap Pakai (16GB RAM / 512GB NVMe): Rp 2.350.000 – Rp 2.750.000 (Unit Baru)
- **Kelebihan**:
  - Single-core IPC modern: Mengungguli performa single-thread vCPU Broadwell.
  - Resource 4x lipat: 16 GB RAM memungkinkan deploy 30+ Docker containers secara bersamaan.
  - Efisiensi energi tertinggi: Idle ~6W, load ~15W (biaya listrik PLN < Rp 10.000/bulan).
  - Port 2.5GbE pada GMKtec G3 ideal untuk pipeline throughput tinggi di jaringan lokal.
- **Kekurangan**:
  - Memory single-channel (1 slot SODIMM).
  - Jalur PCIe terbatas (PCIe 3.0 x1 / x2).

---

### 3. Tier Enterprise 1-Liter Desktop: Modularity & High Durability
- **Model**: Lenovo ThinkCentre M710q / M720q Tiny atau Dell OptiPlex 3050/7050 Micro (Refurbished)
- **CPU**: Intel Core i5-7400T / i5-7500T (Gen 7) atau i5-8400T / i5-8500T (Gen 8, 6 Cores)
- **RAM**: 16 GB DDR4 (2x SODIMM slot, Dual-Channel, upgradeable hingga 64 GB)
- **Storage**: 1x M.2 NVMe SSD (256GB - 512GB) + 1x Bay 2.5" SATA (untuk internal backup drive)
- **Rentang Harga**:
  - Core i5 Gen 7: Rp 1.950.000 – Rp 2.500.000
  - Core i5 Gen 8: Rp 2.800.000 – Rp 3.600.000
- **Kelebihan**:
  - Durabilitas enterprise: Dirancang untuk duty-cycle korporat 24/7 selama bertahun-tahun.
  - Dual storage: Mendukung NVMe sistem + SATA 2.5" untuk data/backup terisolasi.
  - Dual-channel memory support.
  - Ketersediaan spare part dan aksesoris melimpah.
- **Kekurangan**:
  - Konsumsi daya idle sedikit lebih tinggi (~12W - 18W).
  - Form factor sedikit lebih besar (volume ~1 Liter).
  - Membutuhkan inspeksi kebersihan dan penggantian thermal paste pada unit second.

---

### 4. Tier Heavyweight: AMD Ryzen Multi-Threading & Virtualization
- **Model**: Beelink SER5 / GMKtec NucBox M5
- **CPU**: AMD Ryzen 5 5560U / 5600H (6C/12T, up to 4.2 GHz)
- **RAM**: 16 GB / 32 GB DDR4 Dual-Channel
- **Storage**: 512 GB NVMe PCIe 3.0 x4 + 1x Bay 2.5" SATA
- **Rentang Harga**: Rp 3.400.000 – Rp 4.200.000
- **Kelebihan**:
  - 12 thread eksekusi: Mampu menjalankan Proxmox VE dengan multi-VM/LXC cluster.
  - Mampu menjalankan model LLM quantized ringan (Ollama Qwen 2.5 1.5B/3B) secara lokal.
- **Kekurangan**:
  - TDP dan suhu operasional lebih tinggi (idle 15W, peak 35W - 45W).
  - Biaya investasi awal tertinggi.

---

## 🛒 Rekomendasi Merchant & Sumber Terpercaya (Marketplace Indonesia)

### GMKtec NucBox G3
- **Tokopedia (Official Store)**: [GMKtec ID Tokopedia](https://www.tokopedia.com/gmktec-id)
- **Katalog Produk Tokopedia**: [GMKtec G3 Pencarian Tokopedia](https://www.tokopedia.com/find/gmktec-g3)
- **Shopee Direct Search**: [GMKtec G3 Shopee Indonesia](https://shopee.co.id/search?keyword=gmktec%20g3%20n100)
- **Garansi**: 1 Tahun Garansi Resmi GMKtec ID

### Beelink Mini S12 Pro
- **Tokopedia Distributor Utama**: [JURAGANTABLET](https://www.tokopedia.com/juragantablet)
  - Direct Listing: [Beelink Mini S12 Pro 16GB/500GB NVMe](https://www.tokopedia.com/juragantablet/beelink-mini-s12-pro-n100-intel-alderlake-16-500gb-nvme-windows-11-pro)
- **Tokopedia Official Store**: [Beelink.Official](https://www.tokopedia.com/beelinkofficial)
  - Direct Listing: [Beelink Mini S12 Pro NVMe Store Link](https://tokopedia.com/beelinkofficial/beelink-pc-mini-s12-pro-n100-intel-alderlake-16-500gb-nvme-windows-11)
- **Garansi**: 1 Tahun Garansi Resmi Beelink International / Distributor

---

## 🖥️ Arsitektur Operasional: Headless Server (Zero-Monitor)

Dalam deployment server SRE standar, **monitor fisik tidak diperlukan**. Server beroperasi murni secara Headless melalui jaringan remote.

### 1. Day-0 Setup (Instalasi Awal)
- **Opsi Praktis**: Sambungkan unit ke TV/monitor via HDMI selama 10–15 menit hanya untuk initial setup OS (Ubuntu Server 24.04 LTS / Debian 12 Minimal).
- **Konfigurasi Kunci Sebelum Display Dicabut**:
  1. Aktifkan SSH daemon:
     ```bash
     sudo systemctl enable --now ssh
     ```
  2. Alokasikan IP statis atau DHCP Static Reservation di router rumah.
  3. Konfigurasi BIOS: Set `State After G3` / `Restore on AC Power Loss` ke `Always On`.
- **Opsi Zero-Display**: Flash USB installer menggunakan format **cloud-init / autoinstall** (otomatis melakukan provisioning OS, akun user, dan public key SSH tanpa input monitor).

### 2. Day-2 Operations (Akses Produksi Jarak Jauh)
- **Akses Jaringan Lokal**: `ssh voldemort@<ip-lokal>`
- **Akses Jaringan Publik Aman (Zero Open Port)**:
  - Menggunakan mesh VPN **Tailscale** atau **Cloudflare Tunnel** (`cloudflared`).
  - Tidak memerlukan IP publik statis atau port forwarding berbahaya pada router ISP.

### 3. Break-Glass Procedure (Penanganan Darurat)
- Jika SSH hang atau terjadi kegagalan network total, Mini PC cukup dipindahkan sementara ke meja TV untuk dihubungkan via HDMI guna troubleshooting tty console.

---

## 🛠️ Deployment & Commissioning Checklist

1. **Burn-in Stress Testing**:
   - Jalankan tool `stress-ng` atau `mprime` selama 1-2 jam di Linux untuk memvalidasi stabilitas modul RAM dan efektivitas pendinginan heatsink/fan.
2. **Thermal Monitoring Baseline**:
   - Verifikasi suhu idle berada di kisaran 38°C – 48°C menggunakan `sensors` (`lm-sensors`).
3. **Backup Strategy**:
   - Pasang daily rsync/restic snapshot ke Cloudflare R2 atau target secondary NAS.
