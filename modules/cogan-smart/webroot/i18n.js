/* Shared ID/EN catalog. Templates use {0}, {1}, ... for values from the device.
 * Translate UI text only; never rewrite code, paths, form values or module evidence. */
(() => {
  'use strict';
  const entries = [
    ['Daya', 'Power'], ['Suhu', 'Temperature'], ['Modul', 'Modules'], ['Bagian', 'Sections'],
    ['Tentang', 'About'], ['Tentang & kredit', 'About & credits'], ['Mode', 'Mode'],
    ['aktif', 'active'], ['berhenti', 'stopped'], ['mencatat', 'recording'],
    ['data terlambat', 'sample delayed'], ['menyiapkan sampel', 'collecting sample'],
    ['tanpa root', 'no root'], ['gagal membaca', 'read failed'], ['Memuat…', 'Loading…'],
    ['Memeriksa dukungan…', 'Checking support…'], ['membaca sensor…', 'reading sensors…'],
    ['Data belum berhasil dibaca', 'Could not read data'], ['Coba lagi', 'Retry'],
    ['Buka halaman ini dari WebUI modul di KernelSU, KernelSU Next atau BakaSU.', 'Open this page from the module WebUI in KernelSU, KernelSU Next or BakaSU.'],
    ['Detail kernel', 'Kernel details'], ['Info build lengkap', 'Full build information'],
    ['Cooling kernel', 'Kernel cooling'], ['Buka untuk membaca.', 'Expand to read.'],
    ['Suhu & CPU', 'Temperature & CPU'], ['Cas', 'Charging'], ['Setelan mode', 'Mode settings'],
    ['Hemat', 'Power saver'], ['Performa', 'Performance'], ['Kernel Default', 'Kernel Default'],
    ['CPU besar maks {0}%, ambang {1} °C', 'Big CPU cap {0}%, threshold {1} °C'],
    ['Ambang kendali {0} °C', 'Control threshold {0} °C'],
    ['Performa penuh, rem di {0} °C', 'Full performance, limit at {0} °C'],
    ['CPU besar maks {0}%, Badan HP ≤ {1} °C', 'Big CPU cap {0}%, phone body ≤ {1} °C'],
    ['Badan HP dijaga ≤ {0} °C', 'Phone body kept ≤ {0} °C'],
    ['Performa penuh, rem di Badan HP {0} °C', 'Full performance, limit at phone body {0} °C'],
    ['batas {0} °C', 'limit {0} °C'], ['batas Badan HP {0} °C', 'phone body limit {0} °C'], ['Sensor langsung', 'Live sensors'],
    ['Prosesor {0}°', 'Processor {0}°'], ['target batas CPU besar {0}%', 'big CPU target cap {0}%'],
    ['rem darurat prosesor ≥ {0} °C', 'processor emergency brake ≥ {0} °C'], ['Baterai (tanpa sensor Badan HP)', 'Battery (no phone body sensor)'],
    ['Sensor langsung · {0} dtk lalu', 'Live sensors · {0} s ago'],
    ['sensor {0} dtk lalu', 'sensors {0} s ago'], ['sensor tidak tersedia', 'sensors unavailable'],
    ['Sensor tidak tersedia', 'Sensors unavailable'],
    ['Terhubung ke pencatat', 'Connected to the recorder'],
    ['penyebab sekarang: {0}', 'current cause: {0}'],
    ['Pencatat Suhu masih hidup, tetapi sampelnya terlambat ({0} dtk). Suhu langsung tetap dibaca; periksa atau mulai ulang di tab Suhu.', 'The temperature recorder is running, but its sample is delayed ({0} s). Live sensors are still read; check or restart it in the Temperature tab.'],
    ['Pencatat Suhu sedang menyiapkan sampel pertama. Suhu langsung tetap dibaca.', 'The temperature recorder is collecting its first sample. Live sensors are still read.'],
    ['Pencatat Suhu berhenti. Tekan Mulai di tab Suhu. Suhu langsung tetap dibaca.', 'The temperature recorder is stopped. Tap Start in the Temperature tab. Live sensors are still read.'],
    ['Modul dinonaktifkan; Kernel Default memakai sensor sendiri.', 'The module is disabled; Kernel Default uses its own sensors.'],
    ['Target batas CPU besar {0}% · lihat hasil kontrol kernel', 'Big CPU target cap {0}% · see kernel control results'],
    ['Penyebab: {0}', 'Cause: {0}'], ['Aplikasi: {0}', 'App: {0}'],
    ['Boost Performa aktif', 'Performance boost active'], ['Cooling CPU kernel aktif', 'Kernel CPU cooling active'],
    ['pengendali berhenti', 'controller stopped'], ['Pengendali berhenti.', 'Controller stopped.'],
    ['mengecas', 'charging'], ['penuh', 'full'], ['tidak dicas', 'not charging'], ['cas berhenti', 'charging stopped'],
    ['dihentikan', 'stopped'], ['batas isi', 'charge limit'], ['baterai panas', 'hot battery'],
    ['cas bikin HP panas', 'charging heats the phone'], ['Auto cut charging mati.', 'Automatic charge cutoff is off.'],
    ['Cas dihentikan: {0}', 'Charging paused: {0}'], ['Cas normal', 'Normal charging'],
    ['berhenti di {0}%, lanjut {1}%', 'stop at {0}%, resume at {1}%'],
    ['saklar: {0}', 'switch: {0}'], ['saklar tidak ditemukan', 'switch not found'], ['saklar belum dicari', 'switch not detected yet'],
    ['Berhenti di (%)', 'Stop at (%)'], ['Lanjut cas di (%)', 'Resume charging at (%)'],
    ['Jeda bila baterai ≥ (°C)', 'Pause if battery ≥ (°C)'],
    ['Jeda cas karena suhu oleh modul', 'Module temperature-based charging pauses'],
    ['Bawaan: mati. Suhu cas diatur sistem HP (HyperCharge). Nyalakan untuk jeda tambahan dari modul: cas dijeda bila baterai terlalu panas atau, di Kernel Default, bila cas membuat Badan HP panas; lanjut setelah turun 3 °C.', 'Default: off. The phone (HyperCharge) manages charging temperature. Turn on for extra module pauses: charging pauses when the battery is too hot or, in Kernel Default, when charging heats the phone body; it resumes 3 °C lower.'],
    ['Bawaan: pengaturan suhu cas diserahkan ke sistem HP. Modul hanya mengatur batas isi. Aktifkan opsi ini jika ingin jeda suhu tambahan dari modul. Kolom di bawah aktif setelah opsi ini dinyalakan.', 'Default: the phone manages charging temperature. The module only controls charge level limits. Enable this option for additional temperature pauses from the module. The fields below become active when enabled.'],
    ['Suhu cas: sistem HP + jeda tambahan dari modul.', 'Charging temperature: phone system + additional module pauses.'],
    ['Kontrol cas modul nonaktif. Suhu cas mengikuti sistem HP.', 'Module charging controls are off. Charging temperature follows the phone system.'],
    ['Suhu cas: sistem HP. Jeda suhu modul nonaktif; HyperCharge mengikuti sistem HP.', 'Charging temperature: phone system. Module temperature pauses are off; HyperCharge follows the phone system.'],
    ['Pencarian saklar mematikan dan menyalakan cas sebentar. Jika saklar sudah ditemukan, tidak perlu mencari ulang saat HyperCharge berjalan.', 'Switch detection briefly turns charging off and on. If a switch has already been found, there is no need to detect it again during HyperCharge.'],
    ['Kernel Default: jeda cas bila cas bikin panas', 'Kernel Default: pause charging when it causes heat'],
    ['Cari saklar cas', 'Detect charging switch'], ['colokkan charger dulu', 'connect the charger first'],
    ['Kernel Default: ambang kendali (°C)', 'Kernel Default: control threshold (°C)'],
    ['Performa: rem darurat di (°C)', 'Performance: emergency limit (°C)'],
    ['Kernel Default: ambang Badan HP (°C)', 'Kernel Default: phone body threshold (°C)'],
    ['Performa: rem di Badan HP (°C)', 'Performance: phone body limit (°C)'],
    ['Ambang mode dibaca dari suhu Badan HP (yang terasa di tangan). Hemat 2 °C di bawah Kernel Default. Langkah halus: mulai 1 °C sebelum ambang, CPU besar turun 10% per langkah sampai 60%, CPU kecil (yang menjaga UI tetap lancar) paling akhir dan tidak di bawah 80%. CPU hanya diturunkan saat prosesor bekerja (≥ 60 °C); panas dari cas atau ruangan tidak membuat CPU diturunkan. Di semua mode ada rem darurat bila prosesor ≥ 95 °C.', 'Mode thresholds read the phone body temperature (what your hand feels). Power saver is 2 °C below Kernel Default. Smooth steps: from 1 °C before the threshold, the big CPU cores drop 10% per step down to 60%; the little cores, which keep the interface fluid, come last and stay at 80% or more. The CPU is only lowered while the processor works (60 °C or more); heat from charging or the room does not lower the CPU. Every mode brakes when the processor reaches 95 °C.'],
    ['prosesor santai: CPU tidak diturunkan', 'processor idle: CPU not lowered'],
    ['kecil {0}%', 'little {0}%'], ['GPU {0}: {1} / maks {2}', 'GPU {0}: {1} / max {2}'], ['{0} langkah', '{0} steps'],
    ['bisa diatur', 'adjustable'], ['tidak bisa ditulis', 'not writable'], ['gpufreqv2 ada', 'gpufreqv2 present'],
    ['Node GPU belum ditemukan.', 'No GPU node found yet.'],
    ['Baca saja: batas GPU dipasang setelah node ini terbukti di HP.', 'Read only: a GPU limit comes once these nodes are proven on the phone.'],
    ['Hemat: CPU besar maks (%)', 'Power saver: big CPU cap (%)'],
    ['Performa: boost aplikasi di layar', 'Performance: boost foreground app'],
    ['Cek tiap (detik)', 'Check every (seconds)'], ['Terapkan ulang tiap interval', 'Reapply at each interval'],
    ['Simpan: simpan setelan (pengendali aktif membaca pada interval berikutnya). Paksa: simpan, mulai, terapkan sekarang dan ulangi tiap interval. Henti dan Reset melepaskan kontrol milik modul. Reset memakai cas 95/90 dan berhenti sampai Mulai.', 'Save stores settings; a running controller reads them at the next interval. Force saves, starts, applies now and reapplies at each interval. Stop and Reset release the module’s controls. Reset restores 95/90 charging and waits for Start.'],
    ['Simpan', 'Save'], ['Paksa / Terapkan', 'Force / Apply'], ['Reset default', 'Reset defaults'],
    ['Hentikan', 'Stop'], ['Mulai', 'Start'], ['Kontrol kernel', 'Kernel controls'],
    ['Belum diterapkan.', 'Not applied yet.'], ['Kontrol', 'Control'], ['Diminta → terbaca', 'Requested → read back'],
    ['Angka CPU adalah batas maksimum, bukan frekuensi tetap. Batas vendor/termal yang lebih rendah tetap berlaku. Ambang suhu mengatur kapan modul bertindak; tidak menjamin suhu fisik tetap pada angka itu.', 'CPU values are maximum limits, not fixed frequencies. Lower vendor and thermal limits still apply. The temperature threshold determines when the module acts; it does not guarantee that physical temperature stays at that value.'],
    ['Aktivitas', 'Activity'], ['Belum ada.', 'None yet.'], ['Belum ada hasil penerapan.', 'No control results yet.'],
    ['Henti melepaskan kontrol milik modul', 'Stop releases the module’s controls'],
    ['Cogan Smart · Henti melepaskan kontrol milik modul', 'Cogan Smart · Stop releases the module’s controls'],
    ['Cogan Smart {0} · Henti memulihkan kontrol milik modul', 'Cogan Smart {0} · Stop restores the module’s controls'],
    ['menunggu penerapan', 'waiting to apply'], ['terapkan ulang aktif', 'reapply enabled'],
    ['hasil {0} dtk lalu', 'results {0} s ago'], ['diterima', 'accepted'],
    ['dibatasi lebih rendah', 'limited further'], ['berubah/ditolak', 'changed/rejected'],
    ['gagal ditulis', 'write failed'], ['tidak didukung', 'unsupported'],
    ['Pemulihan belum selesai; tekan Henti setelah node dapat ditulis.', 'Restore is incomplete; tap Stop after the node becomes writable.'],
    ['Membaca ulang…', 'Reading again…'], ['Mengganti mode…', 'Changing mode…'], ['Mode {0}', 'Mode: {0}'],
    ['Menyimpan setelan…', 'Saving settings…'], ['Setelan disimpan', 'Settings saved'],
    ['Menerapkan dan memeriksa kontrol…', 'Applying and checking controls…'],
    ['Sudah dicoba; lihat kontrol yang belum diterima.', 'Attempt complete; check controls that were not accepted.'],
    ['Diterapkan. Nilai terbaca tersedia di Kontrol kernel.', 'Applied. Readback values are available under Kernel controls.'],
    ['Pulihkan setelan bawaan (cas 95/90) dan hentikan pengendali?', 'Restore defaults (95/90 charging) and stop the controller?'],
    ['Memulihkan setelan bawaan…', 'Restoring defaults…'],
    ['Setelan bawaan dipulihkan. Tekan Mulai untuk aktif kembali.', 'Defaults restored. Tap Start to activate again.'],
    ['Menghentikan dan memulihkan kontrol…', 'Stopping and restoring controls…'], ['Memulai pengendali…', 'Starting controller…'],
    ['Kontrol daya aktif', 'Power control active'], ['Dihentikan: kontrol milik modul dipulihkan', 'Stopped: module controls restored'],
    ['Mencari saklar cas. Halaman tetap bisa digulir…', 'Detecting the charging switch. You can still scroll…'],
    ['Mencoba saklar satu per satu; cas akan mati-nyala sebentar…', 'Testing switches one by one; charging will briefly switch off and on…'],
    ['Saklar ditemukan: {0}', 'Switch found: {0}'], ['Saklar tidak ditemukan di HP ini.', 'No charging switch found on this phone.'],
    ['Saklar cas ditemukan', 'Charging switch found'], ['Pencarian selesai; lihat hasil.', 'Detection complete; see results.'],
    ['sudah dikontrol', 'already controlled'], ['tidak bisa ditulis', 'not writable'], ['tidak lanjut', 'did not resume'],
    ['tidak berpengaruh', 'no effect'],
    ['Sekarang', 'Now'], ['Prosesor/GPU terpanas · sensor langsung', 'Hottest CPU/GPU · live sensors'],
    ['Catatan terakhir ({0} menit lalu)', 'Last recording ({0} min ago)'], ['mode {0}', 'mode {0}'],
    ['mengecas {0} mA', 'charging at {0} mA'],
    ['belum ada sampel; pencatat mengisi tiap beberapa detik', 'no samples yet; the recorder samples at the configured interval'],
    ['Semua sensor', 'All sensors'], ['Semua sensor ({0})', 'All sensors ({0})'],
    ['Prosesor', 'Processor'], ['Baterai', 'Battery'], ['Badan HP', 'Phone body'], ['Lainnya', 'Other'],
    ['Tidak diketahui', 'Unknown'], ['tidak diketahui', 'unknown'], ['Layar mati', 'Screen off'],
    ['Layar utama (launcher)', 'Home screen (launcher)'], ['Kamera', 'Camera'], ['Sistem Android', 'Android system'],
    ['SurfaceFlinger (tampilan)', 'SurfaceFlinger (display)'], ['Kontrol daya mati', 'Power control off'],
    ['Ringkasan', 'Summary'], ['Salin ringkasan', 'Copy summary'], ['Salin untuk dibagikan', 'Copy to share'],
    ['Simpan log', 'Save logs'], ['Ringkasan (.txt) dan semua sampel (.csv) disimpan ke', 'The summary (.txt) and all samples (.csv) are saved to'],
    ['Menit', 'Minutes'], ['menit', 'minutes'], ['Setelan', 'Settings'], ['Cek suhu tiap (detik)', 'Sample temperature every (seconds)'],
    ['Panas bila Badan HP ≥ (°C)', 'Hot when phone body ≥ (°C)'], ['Simpan riwayat (hari)', 'Keep history (days)'],
    ['Notifikasi saat panas', 'Notify when hot'], ['Notifikasi bila Badan HP ≥ (°C)', 'Notify when phone body ≥ (°C)'],
    ['Terapkan sekarang', 'Apply now'], ['Hapus riwayat', 'Clear history'],
    ['Panas diukur dari suhu Badan HP (yang terasa di tangan), bukan prosesor yang saat santai pun sekitar 50 °C. Ambang ini hanya untuk pencatatan. Kendali CPU dan cas ada di tab Daya. Reset mempertahankan riwayat dan berhenti sampai Mulai.', 'Heat is measured on the phone body (what your hand feels), not the processor, which sits around 50 °C even at rest. These thresholds only affect recording. CPU and charging controls are in the Power tab. Reset keeps history and waits for Start.'],
    ['Badan HP · sensor langsung', 'Phone body · live sensors'], ['Baterai · HP tanpa sensor badan', 'Battery · no phone body sensor'],
    ['Grafik suhu Badan HP', 'Phone body temperature chart'], ['Badan HP - - {0} °C', 'Phone body - - {0} °C'],
    ['Cogan Smart · Suhu & log hanya membaca sensor', 'Cogan Smart · Temperature & logs only read sensors'],
    ['Cogan Smart {0} · Suhu & log hanya membaca sensor', 'Cogan Smart {0} · Temperature & logs only read sensors'],
    ['Riwayat: {0} hari (sejak {1}), {2} KB', 'History: {0} days (since {1}), {2} KB'], ['Riwayat masih kosong.', 'History is empty.'],
    ['{0} mnt', '{0} min'], ['{0} menit', '{0} min'], ['{0} jam', '{0} h'], ['{0} hari', '{0} days'],
    ['Atur sendiri…', 'Custom…'], ['Grafik suhu', 'Temperature chart'],
    ['Belum ada data pada rentang ini.', 'No data in this range yet.'],
    ['Tertinggi ({0})', 'Peak ({0})'], ['Waktu panas (≥ {0} °C)', 'Time hot (≥ {0} °C)'],
    ['Waktu panas (Badan HP ≥ {0} °C)', 'Time hot (phone body ≥ {0} °C)'],
    ['{0} sampel', '{0} samples'], ['Penyebab panas', 'Heat causes'], ['Tidak ada momen panas. 👍', 'No hot samples. 👍'],
    ['Per aplikasi', 'By app'], ['rata-rata / tertinggi', 'average / peak'],
    ['Badan HP rata-rata / tertinggi', 'Phone body average / peak'], ['Per kernel', 'By kernel'],
    ['Per mode', 'By mode'], ['panas {0}%', 'hot {0}%'], ['Bagian HP', 'Phone components'],
    ['CPU rata-rata {0}%', 'Average CPU {0}%'], ['proses kernel {0}%', 'kernel processes {0}%'],
    ['Memuat ringkasan…', 'Loading summary…'], ['Ringkasan disalin', 'Summary copied'], ['Gagal menyalin', 'Copy failed'],
    ['Isi 1 sampai 44640 menit', 'Enter 1 to 44640 minutes'], ['Menyiapkan log…', 'Preparing logs…'],
    ['Tersimpan ({0} sampel):', 'Saved ({0} samples):'], ['Log tersimpan di {0}', 'Logs saved to {0}'],
    ['Menerapkan setelan pencatatan…', 'Applying recording settings…'], ['Setelan pencatatan diterapkan', 'Recording settings applied'],
    ['Reset setelan pencatatan dan berhenti? Riwayat serta log tersimpan tetap ada.', 'Reset recording settings and stop? History and saved logs will be kept.'],
    ['Setelan bawaan dipulihkan; riwayat tetap ada. Tekan Mulai untuk mencatat.', 'Defaults restored; history kept. Tap Start to record.'],
    ['Menghentikan pencatat…', 'Stopping recorder…'], ['Memulai pencatat…', 'Starting recorder…'],
    ['Pencatat berjalan', 'Recorder running'], ['Pencatat dihentikan', 'Recorder stopped'],
    ['Hapus semua riwayat suhu? Log yang sudah disimpan di Download tidak ikut terhapus.', 'Delete all temperature history? Logs already saved in Download will be kept.'],
    ['Menghapus riwayat…', 'Clearing history…'], ['Riwayat dihapus', 'History cleared'],
    ['Data kernel belum dapat dibaca.', 'Kernel data could not be read yet.'],
    ['Bridge native aktif', 'Native bridge active'], ['Kompatibilitas 6.1 · sysfs', '6.1 compatibility · sysfs'],
    ['Akses sysfs perangkat', 'Device sysfs access'], ['Identitas asli · terverifikasi', 'Original identity · verified'],
    ['Identitas dari {0} · belum terverifikasi', 'Identity from {0} · unverified'],
    ['terverifikasi', 'verified'], ['belum terverifikasi', 'unverified'], ['Tidak tersedia', 'Unavailable'],
    ['berbeda dari sumber di atas', 'differs from the source above'],
    ['Fitur bawaan belum dikonfirmasi.', 'Built-in features are not confirmed yet.'], ['Info build tidak tersedia.', 'Build information unavailable.'],
    ['aktif ({0} dtk)', 'active ({0} s)'], ['belum aktif', 'not active yet'],
    ['Dikenali kernel: Power {0}', 'Recognised by kernel: Power {0}'],
    ['Bridge native memerlukan driver Cogan Bridge dalam build kernel 6.1. Kontrol sysfs tetap mengikuti dukungan perangkat.', 'The native bridge requires the Cogan Bridge driver in the kernel 6.1 build. Sysfs controls depend on device support.'],
    ['belum terpasang', 'not installed'], ['Perangkat', 'Device'], ['kernel dibuat untuk HP ini', 'kernel built for this phone'],
    ['nama kernel menyebut HP ini · belum terverifikasi', 'kernel name mentions this phone · unverified'],
    ['nama kernel menyebut HP ini', 'kernel name mentions this phone'],
    ['kernel dibuat untuk {0}', 'kernel built for {0}'], ['kernel belum menyebut perangkat target', 'kernel does not identify its target device'],
    ['modul belum diuji di HP ini', 'module not tested on this phone'],
    ['Cooling kernel · {0} aktif', 'Kernel cooling · {0} active'], ['Tidak ada cooling device yang dapat dibaca.', 'No readable cooling devices.'],
    ['Buka tab Daya sekali agar identitas terbaca · Open the Power tab once to read it.', 'Open the Power tab once to read the identity.'],
    ['Memindai modul…', 'Scanning modules…'], ['Modul yang kamu percaya', 'Modules you trust'],
    ['Modul di whitelist tidak dihitung mencurigakan dan tidak bisa dihapus sebelum dilepas dari whitelist. Root manager, metamodule dan Cogan Smart selalu dilindungi.', 'Whitelisted modules are not counted as suspicious and cannot be removed until taken off the whitelist. The root manager, metamodule and Cogan Smart are always protected.'],
    ['Skrip boot di luar modul', 'Boot scripts outside modules'],
    ['Berjalan saat boot tanpa terlihat di daftar modul root manager. Bisa sengaja dipasang modul, bisa juga sisa modul lama atau penyusup.', 'These run at boot without appearing in the root manager’s module list. They may be installed by a module, left by an old module, or unwanted.'],
    ['Isi /data/adb', '/data/adb contents'],
    ['Folder dan file milik root manager, data modul, atau sisa yang tidak dipakai lagi.', 'Root manager files, module data, or unused leftovers.'],
    ['Pindai ulang', 'Rescan'],
    ['Cogan Smart · Penanda risiko adalah dugaan dari isi modul; baca buktinya sebelum menghapus.', 'Cogan Smart · Risk flags are inferred from module contents; read the evidence before removing anything.'],
    ['tidak ada tanda bahaya', 'no warning signs'], ['perlu dicek', 'needs review'], ['berbahaya', 'dangerous'],
    ['nonaktif', 'disabled'], ['dihapus saat reboot', 'removed at reboot'], ['dipasang saat reboot', 'installed at reboot'],
    ['skrip awal boot', 'early boot script'], ['skrip setelah mount', 'post-mount script'], ['skrip layanan boot', 'boot service script'],
    ['skrip setelah boot selesai', 'boot-completed script'], ['skrip pemasang', 'installer script'], ['skrip saat dicopot', 'uninstall script'],
    ['tombol Action', 'Action button'], ['properti sistem', 'system properties'], ['aturan SELinux', 'SELinux rules'],
    ['Bukti ({0} baris)', 'Evidence ({0} lines)'], ['update menunggu reboot', 'update pending reboot'], ['Memakai: {0}', 'Uses: {0}'],
    ['Mengganti/menambah {0} file sistem', 'Replaces/adds {0} system files'], ['{0} proses berjalan', '{0} processes running'],
    ['Inti: diatur dari root manager.', 'Core: managed by the root manager.'], ['Lepas dari whitelist', 'Remove from whitelist'],
    ['Percaya', 'Trust'], ['Batal hapus', 'Cancel removal'], ['Aktifkan', 'Enable'], ['Nonaktifkan', 'Disable'],
    ['Hapus sampai akar', 'Remove completely'], ['{0} file', '{0} files'],
    ['Inti root manager · dilindungi', 'Root manager core · protected'], ['Di whitelist · dipercaya', 'Whitelisted · trusted'],
    ['File sistem ({0})', 'System files ({0})'], ['…dan {0} lagi', '…and {0} more'], ['Proses ({0})', 'Processes ({0})'],
    ['Akar di luar folder:', 'Files outside the module:'], ['{0} modul', '{0} modules'],
    ['{0} berbahaya', '{0} dangerous'], ['{0} perlu dicek', '{0} need review'], ['{0} skrip boot luar', '{0} external boot scripts'],
    ['{0} isi /data/adb tak dikenal', '{0} unknown /data/adb entries'], ['{0} ikut mengatur CPU/cas/termal', '{0} also control CPU/charging/thermals'],
    ['bisa bentrok dengan mode Cogan Smart', 'may conflict with Cogan Smart modes'],
    ['{0} proses dari /data/adb di luar modul', '{0} /data/adb processes outside modules'], ['aman', 'clear'],
    ['{0} inti', '{0} core'], ['{0} dipercaya', '{0} trusted'], ['tidak terdeteksi', 'not detected'], ['Modul ini', 'This module'],
    ['Modul ini:', 'This module:'],
    ['Belum ada. Tekan 🛡️ Percaya di kartu modul.', 'None yet. Tap 🛡️ Trust on a module card.'],
    ['{0} skrip', '{0} scripts'], ['tidak ada', 'none'], ['Memakai modul: {0}', 'Uses modules: {0}'],
    ['Tidak menyebut modul mana pun', 'Does not reference any modules'], ['Hapus skrip', 'Delete script'],
    ['Tidak ada skrip di post-fs-data.d, post-mount.d, service.d atau boot-completed.d.', 'No scripts in post-fs-data.d, post-mount.d, service.d or boot-completed.d.'],
    ['{0} tak dikenal', '{0} unknown'], ['{0} isi', '{0} entries'], ['root manager / inti', 'root manager / core'],
    ['dipakai {0}', 'used by {0}'], ['tidak dikenal', 'unknown'], ['Hapus', 'Delete'],
    ['Hapus {0} sampai ke akar?', 'Remove {0} completely?'], ['• Proses modul dihentikan sekarang', '• Module processes will be stopped now'],
    ['• Paket yang menunggu dipasang dibuang', '• The pending install package will be discarded'],
    ['• Root manager menghapus foldernya saat reboot (setelah uninstall.sh modul berjalan)', '• The root manager deletes the folder at reboot (after the module’s uninstall.sh runs)'],
    ['• Update yang menunggu reboot dibuang', '• The update pending reboot will be discarded'],
    ['• Skrip boot di luar modul dihapus: {0}', '• External boot scripts will be deleted: {0}'],
    ['Hapus juga data modul di /data/adb/{0} setelah reboot?\nSetelan atau kunci di dalamnya hilang permanen. Pilih Batal untuk menyimpannya.', 'Also delete module data in /data/adb/{0} after reboot?\nSettings or keys inside will be permanently lost. Choose Cancel to keep them.'],
    ['Menambah ke whitelist…', 'Adding to whitelist…'], ['Masuk whitelist', 'Whitelisted'], ['Melepas dari whitelist…', 'Removing from whitelist…'],
    ['Dilepas dari whitelist', 'Removed from whitelist'], ['Menonaktifkan…', 'Disabling…'], ['Nonaktif mulai reboot berikutnya', 'Disabled from next reboot'],
    ['Mengaktifkan…', 'Enabling…'], ['Aktif mulai reboot berikutnya', 'Enabled from next reboot'],
    ['Membatalkan hapus…', 'Cancelling removal…'], ['Batal dihapus', 'Removal cancelled'], ['Menghapus sampai akar…', 'Removing completely…'],
    ['Menghapus skrip…', 'Deleting script…'], ['Skrip dihapus', 'Script deleted'], ['Menghapus…', 'Deleting…'],
    ['Dihapus dari /data/adb', 'Deleted from /data/adb'], ['Pemindaian selesai', 'Scan complete'],
    ['Hapus skrip boot {0}? Prosesnya ikut dihentikan.', 'Delete boot script {0}? Its processes will also be stopped.'],
    ['Hapus /data/adb/{0}? Tidak ada modul terpasang yang memakainya. Tidak bisa dibatalkan.', 'Delete /data/adb/{0}? No installed module uses it. This cannot be undone.'],
    ['Dihapus: {0} proses dihentikan', 'Removed: {0} processes stopped'], ['{0} skrip boot dihapus', '{0} boot scripts deleted'],
    ['. Reboot untuk menuntaskan.', '. Reboot to finish.'], ['Data dihapus setelah reboot.', 'Data will be deleted after reboot.'],
    ['Butuh akses root.', 'Root access required.'],
    ['Hasil pindaian {0} dtk lalu · tekan Pindai ulang untuk memperbarui.', 'Scan from {0} s ago · tap Rescan to update.'],
    ['Memindai ulang… (sementara menampilkan hasil sebelumnya)', 'Rescanning… (showing previous results for now)'], ['Pemindaian gagal.', 'Scan failed.'],
    ['Mematikan perlindungan SELinux', 'Disables SELinux protection'], ['Aturan SELinux membuka hampir semua akses', 'SELinux rules allow almost all access'],
    ['Mengunduh lalu menjalankan kode dari internet', 'Downloads and runs code from the internet'], ['Menjalankan kode tersembunyi (base64)', 'Runs hidden code (base64)'],
    ['Mengubah file root manager', 'Modifies root manager files'], ['Menulis langsung ke partisi', 'Writes directly to partitions'],
    ['Membawa su sendiri (root di luar root manager)', 'Includes its own su (root outside the root manager)'],
    ['Bentrok dengan Cogan Smart: ikut mengatur CPU, cas atau termal', 'May conflict with Cogan Smart: also controls CPU, charging or thermals'],
    ['Aturan SELinux luas (*)', 'Broad SELinux rules (*)'], ['Menghubungi internet/server', 'Contacts the internet/server'],
    ['Membuka data tersandi (base64)', 'Decodes data (base64)'], ['Mengubah modul lain', 'Modifies other modules'],
    ['Menaruh skrip boot di luar foldernya (tertinggal bila modul dihapus)', 'Adds boot scripts outside its folder (left behind when the module is removed)'],
    ['Membuka izin file untuk semua (777)', 'Makes files accessible to everyone (777)'], ['Mencopot/membekukan aplikasi', 'Uninstalls/freezes apps'],
    ['Mengubah properti keamanan/boot (umum di modul spoof)', 'Changes security/boot properties (common in spoof modules)'],
    ['Menyuntik kode ke aplikasi (Zygisk)', 'Injects code into apps (Zygisk)'], ['Menambah layanan init sistem (.rc)', 'Adds system init services (.rc)'],
    ['Mengganti/menambah program sistem', 'Replaces/adds system programs'], ['Identitas modul tidak lengkap', 'Incomplete module identity'],
    ['Membawa program biner (isinya tidak terbaca)', 'Includes binaries (contents cannot be read)'], ['Mengganti/menambah file sistem', 'Replaces/adds system files'],
    ['Mengubah properti sistem', 'Changes system properties'], ['Menambah aturan SELinux', 'Adds SELinux rules'],
    ['Mengatur firewall/jaringan', 'Configures firewall/network'], ['Mengubah setelan Android', 'Changes Android settings'], ['Proses sedang berjalan', 'Processes running'],
    ['Gagal: {0}', 'Failed: {0}'], ['Gagal menyimpan setelan', 'Could not save settings'], ['Gagal menyimpan', 'Could not save'],
    ['Perintah lain sedang berjalan', 'Another command is running'], ['Perintah belum berhasil', 'Command unsuccessful'],
    ['Nilai tidak valid', 'Invalid value'], ['Argumen tidak valid', 'Invalid argument'],
    ['Buka dari WebUI root manager', 'Open from the root manager WebUI'],
    ['Perintah belum selesai; periksa status sebelum mencoba lagi', 'Command has not finished; check status before trying again'],
    ['Perintah gagal', 'Command failed'], ['API shell root manager tidak tersedia', 'Root manager shell API unavailable'],
    ['Perintah {0} gagal (kode {1}): {2}', 'Command {0} failed (code {1}): {2}'], ['tanpa keterangan', 'no details'],
    ['Respons {0} bukan JSON lengkap: {1}', 'Response from {0} is not complete JSON: {1}'], ['Respons {0} tidak valid', 'Invalid response from {0}'],
    ['Nilai tidak valid; tidak ada setelan disimpan', 'Invalid value; no settings saved'],
    ['Nilai tidak valid; tidak ada perubahan', 'Invalid value; no changes made'],
    ['Nilai tidak valid atau resume tidak lebih rendah dari stop; tidak ada setelan disimpan', 'Invalid value or resume is not lower than stop; no settings saved'],
    ['Pengendali gagal mulai', 'Controller failed to start'], ['Pencatat gagal mulai', 'Recorder failed to start'],
    ['Pengendali belum berhenti', 'Controller has not stopped'], ['Pencatat belum berhenti', 'Recorder has not stopped'],
    ['Penerapan masih berjalan; periksa status kontrol', 'Application is still running; check control status'],
    ['Colokkan charger dulu: saklar hanya bisa dicari saat HP sedang mengecas', 'Connect the charger first: switches can only be detected while the phone is charging'],
    ['Pengendali sedang bekerja', 'Controller is busy'], ['Reset dibatalkan: pencatat belum berhenti', 'Reset cancelled: recorder has not stopped'],
    ['Pengendali belum berhenti; status kontrol belum dipulihkan', 'Controller has not stopped; controls have not been restored'],
    ['Pengendali belum berhenti; reset dibatalkan', 'Controller has not stopped; reset cancelled'],
    ['Berhenti, tetapi setelan berhenti gagal disimpan untuk reboot', 'Stopped, but could not save the stopped state for reboot'],
    ['Nama modul tidak valid', 'Invalid module name'], ['Modul tidak ditemukan', 'Module not found'],
    ['Inti root manager dan Cogan Smart tidak dihapus dari sini', 'Root manager core and Cogan Smart cannot be removed here'],
    ['Modul ada di whitelist; lepaskan dulu', 'Module is whitelisted; remove it from the whitelist first'],
    ['Gagal menandai modul untuk dihapus', 'Could not mark module for removal'], ['Gagal menyimpan whitelist', 'Could not save whitelist'],
    ['Root manager, metamodule dan Cogan Smart selalu dipercaya', 'Root manager, metamodule and Cogan Smart are always trusted'],
    ['Modul baru dipasang setelah reboot', 'The new module will be installed after reboot'],
    ['Inti root manager dan Cogan Smart tidak dinonaktifkan dari sini', 'Root manager core and Cogan Smart cannot be disabled here'],
    ['Gagal mengubah modul', 'Could not change module'], ['Update modul sudah dibuang; pasang ulang dari root manager', 'Module update was discarded; reinstall from the root manager'],
    ['Folder skrip tidak valid', 'Invalid script folder'], ['Nama skrip tidak valid', 'Invalid script name'], ['Skrip tidak ditemukan', 'Script not found'],
    ['Gagal menghapus skrip', 'Could not delete script'], ['Nama tidak valid', 'Invalid name'], ['Milik root manager; tidak dihapus', 'Owned by root manager; will not be deleted'],
    ['Tidak ditemukan', 'Not found'], ['Data modul terpasang; hapus modulnya', 'Data belongs to an installed module; remove the module first'],
    ['Masih dipakai modul terpasang', 'Still used by an installed module'], ['Gagal menghapus', 'Could not delete'], ['Perintah tidak dikenal', 'Unknown command'],
    ['Cas cepat', 'Fast charging'], ['Grafis berat: {0}', 'Heavy graphics: {0}'], ['Latar belakang: {0}', 'Background: {0}'],
    ['Proses kernel', 'Kernel processes'], ['Data seluler berat (modem)', 'Heavy cellular traffic (modem)'],
    ['Mengecas (layar mati)', 'Charging (screen off)'], ['Layar mati (proses latar belakang)', 'Screen off (background processes)'],
    ['Aplikasi berat: {0}', 'Heavy app: {0}'], ['Mengecas', 'Charging'], ['Pemakaian ringan: {0}', 'Light use: {0}'],
    ['Modem (data seluler): {0}', 'Modem (cellular data): {0}'], ['Layar & pemakaian: {0}', 'Screen & use: {0}'],
    ['CPU diturunkan karena panas {0}% waktu (terendah CPU besar {1}%, kecil {2}%)', 'CPU lowered for heat {0}% of the time (lowest big CPU {1}%, little {2}%)'],
    ['CPU tidak diturunkan karena panas', 'CPU not lowered for heat'], ['batas mode Hemat {0}% waktu', 'Power saver cap {0}% of the time'],
    ['Sensor macet, tidak dihitung: {0}', 'Stuck sensors, left out: {0}'], ['macet, tidak dihitung', 'stuck, left out'],
    ['Rem HyperOS', 'HyperOS brakes'], ['Suhu papan HyperOS', 'HyperOS board temperature'], ['Profil termal (sconfig)', 'Thermal profile (sconfig)'],
    ['Status suhu (temp_state)', 'Temperature state (temp_state)'], ['Batas CPU HyperOS', 'HyperOS CPU limits'], ['Batas modem', 'Modem limit'],
    ['Batas Wi-Fi', 'Wi-Fi limit'], ['Kecerahan maks', 'Maximum brightness'], ['Mode video', 'Video mode'], ['Node HyperOS kosong.', 'HyperOS nodes are empty.'],
    ['Baca saja: batas yang dipasang HyperOS sendiri (thermal_message). Modul tidak mengubahnya. Suhu papan HyperOS juga dicatat di tab Suhu sebagai sensor hyperos_board (Badan HP).', 'Read only: limits HyperOS sets by itself (thermal_message). The module does not change them. The HyperOS board temperature is also logged in the Temperature tab as the sensor hyperos_board (phone body).'],
    ['Cogan Smart · Power mulai: mode {0}', 'Cogan Smart · Power started: mode {0}'],
    ['Cogan Smart · Power berhenti: kontrol milik modul dipulihkan', 'Cogan Smart · Power stopped: module controls restored'],
    ['Cogan Smart · Power berhenti: ada pemulihan tertunda, periksa status', 'Cogan Smart · Power stopped: restoration pending; check status'],
    ['Mode: {0}', 'Mode: {0}'], ['Mencari saklar cas…', 'Detecting charging switch…'], ['Saklar cas ditemukan: {0}', 'Charging switch found: {0}'],
    ['Saklar cas tidak ditemukan di HP ini', 'No charging switch found on this phone'],
    ['Saklar cas tidak ditemukan di HP ini: auto cut charging tidak bisa dipakai', 'No charging switch found: automatic charge cutoff is unavailable'],
    ['Saklar cas belum menerima perintah; status jeda tidak diklaim aktif', 'Charging switch has not accepted the command; pause is not reported as active'],
    ['Cas dilanjutkan (baterai {0}%, {1} °C)', 'Charging resumed (battery {0}%, {1} °C)'],
    ['Panas {0} °C karena cas: cas dijeda sampai {1} °C', 'Charging heat at {0} °C: charging paused until {1} °C'],
    ['Badan HP {0} °C karena cas: cas dijeda sampai {1} °C', 'Phone body {0} °C from charging: charging paused until {1} °C'],
    ['Baterai {0} °C: cas dijeda sampai {1} °C', 'Battery {0} °C: charging paused until {1} °C'],
    ['Baterai {0}%: cas dihentikan, lanjut di {1}%', 'Battery {0}%: charging stopped, resume at {1}%'],
    ['Suhu {0} °C ≥ {1} °C{2}: CPU dibatasi {3}%', 'Temperature {0} °C ≥ {1} °C{2}: CPU capped at {3}%'],
    ['Suhu turun ke {0} °C: CPU {1}%', 'Temperature down to {0} °C: CPU {1}%'],
    ['Badan HP {0} °C (batas {1} °C){2}: CPU besar {3}%, kecil {4}%', 'Phone body {0} °C (limit {1} °C){2}: big CPU {3}%, little {4}%'],
    ['Badan HP turun ke {0} °C: CPU besar {1}%, kecil {2}%', 'Phone body down to {0} °C: big CPU {1}%, little {2}%'],
    ['Rem darurat: prosesor {0} °C ≥ {1} °C: CPU besar {2}%, kecil {3}%', 'Emergency brake: processor {0} °C ≥ {1} °C: big CPU {2}%, little {3}%'],
    ['Ada kontrol yang belum pulih; periksa izin node lalu Henti lagi', 'Some controls are not restored; check node permissions and tap Stop again'],
    ['Pemulihan CPU gagal: {0}', 'CPU restore failed: {0}'],
    ['Reset: setelan bawaan dipulihkan (cas 95/90), pengendali dihentikan', 'Reset: defaults restored (95/90 charging), controller stopped']
  ];
  const catalog = new Map(entries), originals = new WeakMap();
  const escapeRE = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const rules = entries.filter(([s]) => /\{\d+\}/.test(s)).sort((a,b) => b[0].length - a[0].length).map(([source, target]) => {
    const ids = [];
    const parts = source.split(/(\{\d+\})/).map(part => /^\{\d+\}$/.test(part) ? (ids.push(part.slice(1,-1)), '([\\s\\S]*?)') : escapeRE(part));
    return {re: new RegExp('^' + parts.join('') + '$'), target, ids};
  });
  const language = () => document.documentElement.lang === 'en' ? 'en' : 'id';
  function translate(value, depth = 0) {
    const raw = String(value ?? '');
    if (language() !== 'en' || depth > 6) return raw;
    const s = raw.trim();
    let result = catalog.get(s);
    if (result === undefined) {
      for (const rule of rules) {
        const match = s.match(rule.re);
        if (!match) continue;
        const values = Object.fromEntries(rule.ids.map((id, i) => [id, translate(match[i + 1], depth + 1)]));
        result = rule.target.replace(/\{(\d+)\}/g, (_, id) => values[id]);
        break;
      }
    }
    if (result === undefined) {
      const prefix = s.match(/^([^A-Za-z0-9]+)([A-Za-z][\s\S]*)$/);
      if (prefix) result = prefix[1] + translate(prefix[2], depth + 1);
      else {
        const chunks = s.split(/( · |, |\n)/);
        if (chunks.length > 1) result = chunks.map((p, i) => i % 2 ? p : translate(p, depth + 1)).join('');
        else {
          const colon = s.match(/^([A-Za-z]+: )([\s\S]*)$/);
          result = colon ? colon[1] + translate(colon[2], depth + 1) : s;
        }
      }
    }
    return raw.slice(0, raw.indexOf(s)) + result + raw.slice(raw.indexOf(s) + s.length);
  }
  function update(owner, key, value, put) {
    let saved = originals.get(owner);
    if (!saved) originals.set(owner, saved = new Map());
    const old = saved.get(key), source = old && value === old.output ? old.source : value;
    const output = translate(source);
    saved.set(key, {source, output});
    if (value !== output) put(output);
  }
  function apply(root = document.body) {
    if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let node; (node = walker.nextNode());) {
      if (!node.textContent.trim() || node.parentElement?.closest('script,style,code,pre,[lang]:not(html),[translate="no"]')) continue;
      update(node, 'text', node.textContent, value => node.textContent = value);
    }
    for (const el of root.querySelectorAll('[title],[aria-label]')) {
      if (el.closest('[translate="no"],code,pre')) continue;
      for (const attr of ['title', 'aria-label']) if (el.hasAttribute(attr)) update(el, attr, el.getAttribute(attr), value => el.setAttribute(attr, value));
    }
  }
  function setLanguage(value) {
    document.documentElement.lang = value === 'en' ? 'en' : 'id';
    try { localStorage.setItem('cogan.lang', language()); } catch (_) { /* storage disabled */ }
    apply();
    window.dispatchEvent(new Event('coganlanguagechange'));
  }
  try { document.documentElement.lang = localStorage.getItem('cogan.lang') === 'en' ? 'en' : 'id'; } catch (_) { document.documentElement.lang = 'id'; }
  window.CoganI18n = {t: translate, apply, setLanguage, language, locale: () => language() === 'en' ? 'en-GB' : 'id-ID'};
  document.addEventListener('DOMContentLoaded', () => apply());
})();
