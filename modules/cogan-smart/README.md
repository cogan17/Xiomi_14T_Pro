# Cogan Smart Kernel (modul)

**Versi terbaru: v2.9.0** (`versionCode` 17): mode mengikuti Badan HP, langkah halus, CPU hanya diturunkan saat prosesor bekerja, penyebab panas per bagian HP dengan saran, rem HyperOS. v2.9.1 (satu angka Badan HP dari HyperOS, nama aplikasi asli, batas CPU di log, sensor macet) menunggu uji HP. Catatan perubahan lengkap ada di [`CHANGELOG.md`](CHANGELOG.md).

## ⬇️ Unduh

| Versi | versionCode | ZIP siap pasang | Catatan | Salinan di repo | SHA256 ZIP |
|---|---|---|---|---|---|
| **v2.9.0** (terbaru) | 17 | [Cogan-Smart-Kernel-v2.9.0.zip](https://github.com/cogan17/Cogan-Kernel/releases/download/cogan-smart-v2.9.0/Cogan-Smart-Kernel-v2.9.0.zip) | [What's New](https://github.com/cogan17/Cogan-Kernel/releases/download/cogan-smart-v2.9.0/Cogan-Smart-v2.9.0-Whats-New-and-Fixes.txt) | [`rilis/v2.9.0`](rilis/v2.9.0) | `7d15a729ce184aef8a3f870d5c0837010e22ccf69b910309c7f208b870057522` |
| v2.8.2 | 16 | [Cogan-Smart-Kernel-v2.8.2.zip](https://github.com/cogan17/Cogan-Kernel/releases/download/cogan-smart-v2.8.2/Cogan-Smart-Kernel-v2.8.2.zip) | [What's New](https://github.com/cogan17/Cogan-Kernel/releases/download/cogan-smart-v2.8.2/Cogan-Smart-v2.8.2-Whats-New-and-Fixes.txt) | [`rilis/v2.8.2`](rilis/v2.8.2) | `73f6d9c9a167d1528057ff84c65d6db371a5cde63e1435ca6e5e4f14bfc367d5` |
| v2.8.1 | 15 | [Cogan-Smart-Kernel-v2.8.1.zip](https://github.com/cogan17/Cogan-Kernel/releases/download/cogan-smart-v2.8.1/Cogan-Smart-Kernel-v2.8.1.zip) | [What's New](https://github.com/cogan17/Cogan-Kernel/releases/download/cogan-smart-v2.8.1/Cogan-Smart-v2.8.1-Whats-New-and-Fixes.txt) | [`rilis/v2.8.1`](rilis/v2.8.1) | `441e0780d77480f6642a84f5478ce61d659110a640ca6b025f51d2c718ce594f` |

- ZIP di Pre-release ([`cogan-smart-v2.9.0`](https://github.com/cogan17/Cogan-Kernel/releases/tag/cogan-smart-v2.9.0), [`cogan-smart-v2.8.2`](https://github.com/cogan17/Cogan-Kernel/releases/tag/cogan-smart-v2.8.2), [`cogan-smart-v2.8.1`](https://github.com/cogan17/Cogan-Kernel/releases/tag/cogan-smart-v2.8.1)) dan di folder `rilis/` adalah file yang sama, byte per byte.
- Pasang lewat root manager sebagai pembaruan modul, lalu reboot. Setelan dan riwayat tetap dipakai (ID `cogan_smart` sama).
- Kernel tujuan: **r1** repo ini (ACK 6.1.176). Diuji owner di Xiaomi 14T Pro:
  - **v2.9.0** (24 Okt 2026): dipakai owner 7 jam (15.38–22.38 WIB) dengan kernel r2 dan r3, mode Kernel Default dan Hemat; CPU penuh hampir sepanjang waktu, panas terbanyak saat HyperCharge. Suhu Badan HP masih terasa tidak konsisten (diperbaiki di v2.9.1);
  - **v2.8.2 dengan r1** (24 Okt 2026): identitas kernel terverifikasi lewat Cogan Bridge ("kernel dibuat untuk HP ini"), mode Kernel Default, pencatat suhu, mengecas cepat 3868 mA, penjaga modul "aman";
  - v2.8.1 dan v2.8.2 dengan kernel arsip r6 (6.1.176, 23 Okt 2026); v2.8.2 juga saat pengisian HyperCharge.
- Versi baru: taruh ZIP dan catatannya di `rilis/<versi>/`, lalu jalankan tombol **Cogan Smart Release** di tab Actions.

Satu modul KernelSU / KernelSU Next / BakaSU / Magisk yang menggabungkan **Cogan Power Mode v1.2** dan **Cogan Thermal Monitor v1.3** (issue #21, fondasi Smart Kernel). Kode kedua bagian tetap sama; yang berubah hanya cara keduanya dipasang dan saling menemukan.

| Bagian | Folder | Tugas |
|---|---|---|
| Daya | `power/` | Mode, batas CPU, boost aplikasi di layar, auto cut charging, readback kontrol |
| Suhu | `thermal/` | Sensor tiap 20 detik (termasuk suhu papan HyperOS), dugaan penyebab panas per bagian HP dengan saran, riwayat 7 hari, simpan log |
| Modul | `guard/` | Penjaga modul: perilaku modul lain, whitelist, hapus sampai ke akar |
| Bersama | `bridge.sh`, `webroot/client.js` | Cogan Bridge ABI 1, transport WebUI |

WebUI punya tiga tab: **⚡ Daya**, **🌡️ Suhu** dan **🧩 Modul**, plus halaman **ℹ️ Tentang & kredit** (`about.html`, bahasa Indonesia dengan pilihan English) dari tautan di bawah tiap tab. Dua tema bergaya Material You di `webroot/theme.css`: **Terang hangat** dan **Gelap OLED** (hitam murni); bawaannya mengikuti mode gelap HP, pilihan tetap disimpan dari halaman Tentang. Setiap kartu bisa dilipat; posisi buka/tutup diingat per tab.
Tiap tab adalah halaman sendiri, jadi `client.js` menyimpan jawaban baca terakhir (dan identitas kernel/HP) di `localStorage` WebView: pindah tab langsung menampilkan nilai terakhir (angka redup, ↻ di pojok) sampai bacaan baru datang. Tab Modul memakai hasil pindaian yang berumur < 2 menit apa adanya; Pindai ulang untuk memperbarui.

## Mode

| Di layar | Nilai internal | Perilaku |
|---|---|---|
| 🌿 Hemat | `hemat` | CPU besar dibatasi `SAVER_CAP` %, ambang Badan HP 2 °C di bawah Kernel Default (39 °C) |
| 🧠 Kernel Default | `seimbang` | Bawaan. CPU diturunkan bertahap bila Badan HP ≥ `TARGET_TEMP` (41 °C) |
| 🎮 Performa | `game` | Performa penuh, CPU diturunkan bila Badan HP ≥ `GAME_LIMIT` (44 °C), boost aplikasi di layar |

Sejak v2.9.0 ambang mode dibaca dari suhu **Badan HP** (sensor kulit HP, yang terasa di tangan), bukan prosesor. Prosesor Dimensity HP ini saat santai pun sekitar 50 °C, sehingga ambang 42 °C pada prosesor (v2.8) membatasi CPU hampir sepanjang waktu. Badan HP memakai angka badan milik HyperOS sendiri (`board_sensor_temp`, dicatat sebagai `hyperos_board`) bila ada, lalu sensor kulit terpanas, lalu suhu baterai; semua kartu memakai angka yang sama (v2.9.1). "Panas" di tab Suhu juga berarti Badan HP ≥ 41 °C. Ambang 41/44 °C dipilih owner setelah uji HP (41 °C sudah terasa hangat menuju panas).

Langkah halus (Kernel Default dan Performa):

| Langkah | CPU besar (X4) | CPU kecil (A720) |
|---|---|---|
| 0 | 100 % | 100 % |
| 1–4 | 90 → 60 % | 100 % |
| 5–6 | 60 % | 90 → 80 % |

Mulai 1 °C sebelum ambang dengan langkah 1–2 saja; tiap langkah ditunggu tiga kali cek (Badan HP berubah pelan); naik lagi setelah tiga kali cek ≥ 1,5 °C di bawah ambang. CPU hanya diturunkan saat prosesor bekerja (≥ 60 °C): panas dari cas, ruangan atau HP yang santai tidak membuat CPU diturunkan, dan saat prosesor santai batasnya dilepas bertahap. Hemat turun 10 % dari `SAVER_CAP`. Di semua mode ada **rem darurat** bila prosesor ≥ 95 °C. Cogan Bridge ABI 1 memberi satu batas untuk semua inti X4 dan satu untuk A720.

Jeda cas karena suhu (`CHARGE_THERMAL`) tetap **mati secara bawaan**: HyperCharge dan sistem HP yang mengatur suhu cas. GPU dibaca saja (Kontrol kernel); batas GPU menyusul setelah node-nya terbukti di HP.

Kartu **🧯 Rem HyperOS** di tab Daya menampilkan batas yang dipasang HyperOS sendiri (`/sys/class/thermal/thermal_message`: suhu papan, `sconfig`, `temp_state`, batas CPU, modem, Wi-Fi, kecerahan maks, mode video). Baca saja; modul tidak menulis node itu.

Tab Suhu menjelaskan tiap momen panas dari ±3 menit terakhir, per bagian HP, dengan saran: cas cepat, cas, grafis (GPU), modem (data seluler), prosesor, proses latar belakang, proses kernel, layar mati, atau layar & pemakaian biasa.

**Henti** melepas semua kontrol milik modul sehingga pengaturan vendor (HyperOS/MediaTek) berjalan sendiri. Tombol Action di root manager berpindah ke mode berikutnya.

## 🧩 Modul (penjaga modul, v2.2)

`guard/report.sh scan` membaca `/data/adb` (tanpa menjalankan apa pun dari modul lain) dan `guard/guard.awk` menyusun laporannya:

- **Tiap modul:** identitas, status (aktif, nonaktif, dihapus/dipasang saat reboot, update tertunda), ukuran, hook yang dipakai (skrip boot, `system.prop`, `sepolicy.rule`, Action, WebUI), file sistem yang diganti, program biner, proses yang sedang berjalan, dan **akar di luar foldernya** (skrip di `service.d` dan sejenisnya yang memakai modul itu).
- **Penanda risiko** dari isi skrip, `system.prop` dan `sepolicy.rule`, dengan bukti `file:baris`. ⛔ berbahaya: mematikan SELinux, aturan SELinux `* * * *`, unduh-lalu-jalankan, kode base64 yang dijalankan, mengubah file root manager, menulis partisi, membawa `su` sendiri. ⚠️ perlu dicek: internet, Zygisk, ganti program sistem, layanan init, skrip boot di luar folder, mengubah modul lain, prop keamanan, izin 777, mencopot aplikasi. Penanda ini **dugaan**, bukan antivirus; modul spoof yang sah pun bisa ditandai.
- **Terintegrasi perangkat ⇄ kernel ⇄ modul (D-023):** tab ini memuat kartu Kernel yang sama dengan tab lain (identitas asli dari Cogan Bridge, ✓ kernel dibuat untuk HP ini). Modul lain yang menulis node yang dikendalikan Cogan Smart (cpufreq, uclamp, saklar cas, termal, `stop` layanan termal) ditandai ⚔️ **bentrok**: dua pengendali di node yang sama saling tarik, seperti alasan Power Mode dan Thermal Monitor digabung.
- **Di luar modul:** skrip di `post-fs-data.d`, `post-mount.d`, `service.d`, `boot-completed.d`; isi `/data/adb` beserta pemakainya; proses dari `/data/adb` yang bukan milik modul mana pun.
- **Whitelist:** root manager, metamodule (NoMount) dan Cogan Smart selalu dilindungi. Modul yang ditandai 🛡️ Percaya tidak dihitung mencurigakan dan tidak bisa dihapus sebelum dilepas. Daftar: `/data/adb/cogan_smart/guard/trusted`.
- **Hapus sampai ke akar:** proses modul dihentikan, modul ditandai `disable` + `remove` (root manager menjalankan `uninstall.sh`-nya lalu menghapus folder saat reboot), update tertunda dan skrip boot luar yang memakainya langsung dihapus. Data `/data/adb/<id>` hanya dihapus bila dipilih, **setelah** reboot (`service.sh` → `guard/report.sh boot`), karena `uninstall.sh` modul mungkin masih memerlukannya. ↩ Batal hapus tersedia sebelum reboot.
- Nonaktifkan/aktifkan memakai berkas `disable` seperti root manager (berlaku setelah reboot). Isi `/data/adb` yang tidak dikenal dan tidak dipakai modul terpasang bisa dihapus.

## Pasang

- Data: `/data/adb/cogan_smart/power`, `/data/adb/cogan_smart/thermal` dan `/data/adb/cogan_smart/guard` (whitelist); log yang disimpan ada di `/sdcard/Download/CoganThermal`.
- Bila **Cogan Power Mode** atau **Cogan Thermal Monitor** lama masih terpasang, installer menyalin setelan dan riwayatnya (tanpa `run/`) lalu menandai modul lama untuk dihapus saat reboot. Dua pengendali di node CPU/cas yang sama akan saling tarik.
- Reboot sekali setelah memasang.

## Perangkat ⇄ kernel ⇄ modul

Ketiganya saling mengenal (D-023). Kartu Kernel di kedua tab WebUI menampilkan hasilnya.

| Arah | Tanpa Cogan Bridge (kernel r2) | Dengan Cogan Bridge (r3) |
|---|---|---|
| Modul → perangkat | `ro.product.device`, nama, `ro.board.platform`; modul diuji untuk `rothko` (`CB_DEVICES`) | Sama |
| Modul → kernel | Identitas dari `/proc` (kandidat, **belum terverifikasi**) | `release`/`banner` asli dari kernel, di balik spoof SUSFS |
| Kernel → perangkat | Nama kernel menyebut `rothko` (`…-Cogan-Rothko-…`) = kandidat | Atribut `device` (target build) dan `soc` (dari device tree) = terverifikasi |
| Kernel → modul | Tidak ada | Heartbeat `power_client`/`thermal_client`, lease CPU QoS dilepas kernel bila modul berhenti |

`device_json` (di `bridge.sh`) melaporkan `match`: 1 kernel dibuat untuk HP ini, 0 untuk HP lain, -1 belum diketahui. Pada HP selain `rothko` modul tetap berjalan dengan kontrol sysfs, tetapi menandai "belum diuji".

**Untuk build r3**, driver Cogan Bridge menambah dua atribut opsional ABI 1 (modul ini sudah membacanya): `device` = `TARGET_DEVICE` saat kompilasi (`rothko`), `soc` = platform dari device tree saat boot (mis. `mt6989`). Atribut lain ABI 1 tidak berubah.

## Uji dan paket

```sh
cd tests && python3 -m unittest test_cogan_smart_power test_cogan_smart_thermal test_cogan_smart_bridge test_cogan_smart_android test_cogan_smart_module test_cogan_smart_guard
node --test tests/test_cogan_smart_webui.cjs
python3 scripts/package_module.py modules/cogan-smart OUT_DIR   # ZIP siap pasang, tanpa README dan folder rilis/
```

Tes memakai `mksh` dan `original-awk` bila terpasang (shell dan awk Android).
