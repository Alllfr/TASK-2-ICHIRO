<div align=center>

|    NRP     |           Nama             | Bagian             |
| :--------: |       :------------:       | :----------------: |
| 2043261062 |  Alfihra Putri Syahbania   | Miru               |
| 5054261015 |  Arya Wijaya               | Navigator          |

# Laporan Pengerjaan Task 2

## A. Setup Workspace

### Langkah-langkah
1. **Menyiapkan lingkungan ROS 2 Jazzy** dengan memuat konfigurasi ROS 2 melalui terminal.
2. **Membangun workspace** menggunakan `colcon build --symlink-install` untuk mengompilasi paket dan menyiapkan executable.
3. **Memuat workspace** menggunakan `source install/setup.bash` agar paket `rally_wasit`, `rally_navigator`, dan `rally_miru` dapat dijalankan.
4. **Mengatur format log terminal** menggunakan variabel `RCUTILS_CONSOLE_OUTPUT_FORMAT` agar setiap pesan menampilkan nama node dan isi log.
5. **Menjalankan node turtlesim** pada terminal pertama sebagai lingkungan simulasi gerakan Miru.
6. **Menjalankan node wasit** pada terminal kedua dengan parameter `seed:=7` untuk mengatur konfigurasi lomba.
7. **Menjalankan node navigator** pada terminal ketiga untuk menerima peta lomba, menentukan rute, dan mengirimkan instruksi gerakan kepada Miru.
8. **Menjalankan node Miru** pada terminal keempat untuk menerima instruksi dari navigator, menjalankan gerakan pada turtlesim, dan melaporkan statusnya.
9. **Memverifikasi komunikasi antarnode** dengan memastikan keempat node aktif dan topik komunikasi ROS 2 yang diperlukan tersedia.

### Screenshot
![Hasil Setup Workspace](assets/setupresult.png)
![Relasi Node](assets/node.png)

# 1. Paket Rally Miru

Miru adalah pembalap yang menjalankan instruksi dari navigator. Miru menerima instruksi melalui ROS 2, menggerakkan turtle menggunakan turtlesim, dan melaporkan statusnya secara berkala.

Implementasi paket `rally_miru` mencakup pengelolaan antrean instruksi, komunikasi ROS 2, pengaturan kecepatan, gerak maju, belokan, dan laporan status. Task bonus berfokus pada peningkatan akurasi penghentian gerakan.

## A. Antrean Instruksi
Implementasi `InstructionQueue` menyimpan instruksi dalam antrean FIFO (*First In, First Out*). Setiap instruksi memiliki `instruction_id`, `distance`, dan `turn`.
Instruksi hanya diterima apabila ID-nya lebih besar daripada ID terakhir yang diterima. Instruksi dengan ID duplikat atau lebih kecil akan diabaikan.
Langkah-langkah implementasi:
1. Membuat class `InstructionQueue` dengan antrean berbasis `deque`.
2. Mengimplementasikan `add()` untuk menerima instruksi baru dan menolak ID yang tidak memenuhi aturan.
3. Mengimplementasikan `pop()` untuk mengambil instruksi paling awal.
4. Mengimplementasikan `__len__()` untuk mendapatkan jumlah instruksi yang masih menunggu.
5. Menghubungkan subscriber `/navigator/instruction` dengan callback `on_instruction()`.
6. Menampilkan log informasi untuk instruksi yang diterima dan log debug untuk instruksi yang diabaikan.

Implementasi antrean:
![Implementasi Instruction Queue](assets/instruction_queue.png)

Pengujian antrean:
![Pengujian Instruction Queue](assets/test_queue.png)

## B. Pose dan Perintah Gerak
Miru menggunakan publisher dan subscriber ROS 2 untuk berkomunikasi dengan turtlesim.
Langkah-langkah implementasi:
1. Membuat publisher bertipe `Twist` pada `/turtle1/cmd_vel`.
2. Membuat subscriber bertipe `Pose` pada `/turtle1/pose`.
3. Menyimpan pose terbaru melalui callback `on_pose()`.
4. Mengimplementasikan `publish_velocity()` untuk mengatur `linear.x` sebagai kecepatan maju dan `angular.z` sebagai kecepatan rotasi.

Implementasi perhitungan gerak:
![Implementasi Motion](assets/motion.png)

Pemeriksaan komunikasi dilakukan menggunakan `ros2 node info /miru` untuk memastikan publisher dan subscriber terhubung ke topik yang sesuai.

## C. Aba-aba GO dan Parameter Kecepatan
Miru menyimpan status lomba terbaru melalui subscriber `/race/state`. Gerakan dimulai ketika status lomba menunjukkan `GO`.
Kecepatan gerak dikendalikan melalui parameter `speed`, dengan batas minimum 0,1 m/s dan maksimum 2,5 m/s.
Langkah-langkah implementasi:
1. Mendaftarkan parameter `speed` dengan nilai awal 1,0 m/s.
2. Mendaftarkan callback `on_parameter_change()` untuk memvalidasi perubahan parameter.
3. Menolak nilai di luar rentang yang diperbolehkan.
4. Membuat subscriber `/race/state` dengan callback `on_race_state()`.
5. Menyimpan status lomba terbaru untuk digunakan oleh state machine.

Implementasi GO dan parameter:
![Implementasi GO dan Parameter](assets/go_parameter.png)
Pengujian GO dan parameter:
![Pengujian GO dan Parameter](assets/test_go_parameter.png)

Pengujian parameter mencakup nilai yang ditolak, seperti 3,0 dan 0,05, serta nilai batas 2,5 m/s yang diterima.

## D. Gerak Maju
Miru bergerak maju berdasarkan koordinat rencana, yaitu `planned_x`, `planned_y`, dan `planned_heading`.
Langkah-langkah implementasi:
1. Menggunakan `target_point()` untuk menghitung koordinat tujuan berdasarkan posisi rencana, arah hadap, dan jumlah kotak.
2. Menyimpan koordinat tujuan pada `target_x` dan `target_y`.
3. Menggunakan `remaining_distance()` untuk menghitung sisa jarak pada arah gerak.
4. Mengirim perintah maju selama sisa jarak masih positif.
5. Mengirim kecepatan nol ketika sisa jarak mencapai nol atau negatif.
6. Memperbarui posisi rencana setelah gerakan selesai.

Implementasi gerak maju:
![Implementasi Gerak Maju](assets/drive.png)
Simulasi gerak maju:
![Simulasi Gerak Maju](assets/drive_simulation.png)

## E. Belokan
Miru mendukung belokan 90 derajat ke kiri dan ke kanan.
Langkah-langkah implementasi:
1. Menggunakan `turn_target()` untuk menentukan arah tujuan.
2. Menambahkan sudut sebesar π/2 untuk belok kiri.
3. Mengurangi sudut sebesar π/2 untuk belok kanan.
4. Menggunakan `wrap_angle()` agar sudut berada dalam rentang −π hingga π.
5. Menghitung selisih sudut antara heading tujuan dan orientasi turtle aktual.
6. Menggunakan `turn_rate()` untuk menentukan kecepatan rotasi.
7. Menghentikan rotasi ketika selisih sudut berada dalam toleransi yang ditentukan.

Implementasi belokan:
![Implementasi Belokan](assets/turn.png)

Simulasi belokan:
![Simulasi Belokan](assets/turn_simulation.png)

## F. Laporan Status
Miru melaporkan status kepada navigator melalui `/miru/status` dengan interval 0,05 detik atau sekitar 20 Hz.
Langkah-langkah implementasi:
1. Membuat publisher bertipe `DriverStatus` pada `/miru/status`.
2. Membuat timer dengan interval `STATUS_PERIOD` sebesar 0,05 detik.
3. Memastikan pose pertama telah diterima sebelum menerbitkan status.
4. Mengisi pesan dengan state Miru, koordinat `x` dan `y`, orientasi `theta`, `current_id`, `done_id`, dan jumlah antrean.
5. Menerbitkan pesan menggunakan `self.status_publisher.publish(msg)`.
Implementasi publisher dan timer:
![Implementasi Publisher dan Timer Status](assets/status.png)
Implementasi fungsi laporan status:
![Implementasi Publish Status](assets/status_topic.png)

Verifikasi dilakukan menggunakan `ros2 topic echo /miru/status` dan `ros2 topic hz /miru/status`.

## G. Bonus: Berhenti Lebih Tepat
Pengukuran dilakukan pada kecepatan 0,5 m/s, 1,0 m/s, dan 2,5 m/s.

### Hasil Pengujian

Tabel berikut membandingkan nilai referensi implementasi lama dengan hasil pengukuran implementasi baru.

| Kecepatan | Galat Lama (m) | Waktu Lama (s) | Galat Baru (m) | Waktu Baru (s) |
|---|---:|---:|---:|---:|
| 0,5 m/s | 0,05 | 6,0 | 0,0236 | 6,030 |
| 1,0 m/s | 0,10 | 3,0 | 0,0381 | 3,019 |
| 2,5 m/s | 0,25 | 1,2 | 0,1462 | 1,214 |

Galat dan waktu baru merupakan rata-rata pengukuran pada instruksi 6, 7, dan 8 untuk setiap kecepatan.

### Analisis Hasil

| Kecepatan | Penurunan Galat |
|---|---:|
| 0,5 m/s | 52,8% |
| 1,0 m/s | 61,9% |
| 2,5 m/s | 41,5% |

Hasil pengujian menunjukkan bahwa galat posisi rata-rata implementasi baru lebih kecil daripada nilai referensi implementasi lama pada ketiga kecepatan. Galat rata-rata meningkat seiring bertambahnya kecepatan, sehingga penghentian pada kecepatan tinggi masih memiliki galat yang lebih besar.

Waktu baru merupakan rata-rata durasi segmen gerak pada instruksi 6–8, sedangkan waktu lama merupakan nilai referensi yang digunakan untuk perbandingan.

**Screenshot**
![Proses Pengujian](assets/pengujian.png)

## Kesimpulan Miru
Paket `rally_miru` mengimplementasikan pengelolaan antrean instruksi, komunikasi ROS 2, pengendalian gerak maju, belokan, pengaturan parameter kecepatan, dan publikasi status. Pengujian bonus menunjukkan bahwa galat posisi rata-rata implementasi baru lebih kecil dibandingkan nilai referensi implementasi lama pada tiga kecepatan yang diuji.


# 2. Paket Rally Navigator

Paket `rally_navigator` dikembangkan untuk mengolah data peta balap (`RaceMap`), menentukan lintasan navigasi dari titik Start hingga Finish, dan mengirimkan instruksi gerakan secara bertahap kepada Miru (`Instruction`) berdasarkan laporan kondisi terkini (`DriverStatus`).

## A. Ringkasan Implementasi
| Task | Deskripsi | Status | Modul Utama |
|---|---|---|---|
| Task A | Subscriber `/race/map` dengan QoS `TRANSIENT_LOCAL` dan `RELIABLE` | Selesai | `navigator_node.py` |
| Task B | Algoritma rute terpendek Breadth-First Search (BFS) | Selesai | `route.py` |
| Task C | Konversi rute ke arah mata angin (EAST, NORTH, WEST, SOUTH) | Selesai | `route.py` |
| Task D | Konversi arah menjadi instruksi gerakan dan belokan (`Instruction`) | Selesai | `route.py` |
| Task E | Publisher `/navigator/instruction` dan subscriber `/miru/status` | Selesai | `navigator_node.py` |
| Task F | Parameter dinamis `instructions_ahead` dengan validasi rentang 1–5 | Selesai | `navigator_node.py` |
| Task G | Implementasi dan analisis perbandingan algoritma DFS dan BFS | Selesai | `route.py` |

## B. Penerimaan Peta
Navigator menggunakan subscriber `/race/map` untuk menerima data peta balap bertipe `RaceMap`.
Konfigurasi QoS menggunakan:
- `durability=TRANSIENT_LOCAL`
- `reliability=RELIABLE`

Konfigurasi tersebut memungkinkan navigator menerima peta yang telah dipublikasikan sebelum node navigator aktif, selama publisher masih menyediakan sampel yang tersimpan sesuai pengaturan QoS.
Implementasi subscriber peta berada pada `navigator_node.py`.

Pengujian Task A:

![Task A](assets/Task_A.png)

## C. Pencarian Rute dengan BFS
Navigator menggunakan algoritma Breadth-First Search (BFS) untuk mencari lintasan dari titik Start menuju Finish pada peta balap.
Langkah-langkah implementasi:
1. Membaca struktur peta dan posisi Start serta Finish.
2. Mengeksplorasi simpul menggunakan antrean FIFO.
3. Melacak simpul sebelumnya untuk merekonstruksi rute.
4. Menghasilkan lintasan dengan jumlah langkah minimum pada grid tanpa bobot.

Implementasi pencarian rute berada pada `route.py`.
Pengujian `test_find_route.py`:
![Pengujian Find Route](assets/test_find_route.png)

## D. Konversi Rute dan Instruksi Gerakan
Rute hasil BFS dikonversi menjadi arah mata angin, kemudian menjadi instruksi gerakan yang dapat dijalankan Miru.
Langkah-langkah implementasi:
1. Mengonversi langkah pada grid menjadi arah EAST, NORTH, WEST, atau SOUTH.
2. Membandingkan arah berurutan untuk menentukan kebutuhan belokan.
3. Menggabungkan gerakan maju dan belokan menjadi pesan `Instruction`.
4. Menyertakan ID instruksi, jarak gerak, dan jenis belokan pada setiap pesan.
Implementasi konversi arah dan instruksi berada pada `route.py`.
Pengujian `test_directions.py`:
![Pengujian Directions](assets/test_directions.png)
Pengujian `test_instructions.py`:
![Pengujian Instructions](assets/test_instructions.png)

## E. Komunikasi dengan Miru
Navigator mengirimkan instruksi gerakan melalui `/navigator/instruction` dan menerima status Miru melalui `/miru/status`.
Langkah-langkah implementasi:
1. Membuat publisher untuk pesan `Instruction`.
2. Membuat subscriber untuk pesan `DriverStatus`.
3. Membaca `current_id`, `done_id`, dan jumlah instruksi yang masih menunggu.
4. Mengatur pengiriman instruksi berdasarkan progres Miru.
5. Mempertahankan batas pengiriman berdasarkan `done_id + instructions_ahead`.
Mekanisme tersebut memungkinkan navigator mengirim instruksi secara bertahap sesuai kapasitas antrean yang dikonfigurasi.

Pengujian Task E:

![Task E](assets/Task_E.png)
![Task E - Pengujian 1](assets/Task_E1.png)
![Task E - Pengujian 2](assets/Task_E2.png)
![Task E - Pengujian 3](assets/Task_E3.png)

## F. Parameter Dinamis `instructions_ahead`
Navigator menyediakan parameter `instructions_ahead` untuk mengatur jumlah instruksi yang boleh dikirim ke depan.
Nilai awal parameter adalah `2`, dengan rentang yang diperbolehkan dari `1` hingga `5`.

Langkah-langkah implementasi:
1. Mendaftarkan parameter `instructions_ahead`.
2. Menentukan nilai awal parameter sebesar `2`.
3. Memvalidasi perubahan parameter melalui callback.
4. Menerima nilai dalam rentang 1–5.
5. Menolak nilai di luar rentang yang ditentukan.

Pengujian Task F:
![Task F](assets/Task_F.png)

## G. Perbandingan Algoritma BFS dan DFS
BFS dan Depth-First Search (DFS) dibandingkan berdasarkan struktur data, pola eksplorasi, optimalitas rute, dan jumlah langkah yang dihasilkan pada grid 5×5.
| Kriteria | BFS (Breadth-First Search) | DFS (Depth-First Search) |
|---|---|---|
| Struktur Data | Queue (FIFO) | Stack (LIFO) atau rekursi |
| Pola Eksplorasi | Melebar per tingkat (*layer*) | Menyusuri satu jalur hingga ujung sebelum melakukan *backtracking* |
| Optimalitas Jalur | Menjamin rute terpendek pada graf tanpa bobot | Tidak menjamin rute terpendek |
| Panjang Rute pada Grid 5×5 | 5 langkah | 13 langkah |

BFS dipilih sebagai algoritma utama navigator karena menjamin lintasan dengan jumlah langkah minimum pada graf tanpa bobot. DFS dapat menghasilkan lintasan yang lebih panjang, bergantung pada urutan eksplorasi dan struktur peta.

Pengujian Task G:

![Task G](assets/Task_G.png)

## Kesimpulan Navigator
Paket `rally_navigator` mengimplementasikan penerimaan peta, pencarian rute menggunakan BFS, konversi arah menjadi instruksi gerakan, komunikasi dengan Miru, dan pengaturan jumlah instruksi yang dikirim ke depan melalui parameter dinamis. Pengujian unit dan fungsional digunakan untuk memverifikasi pencarian rute, konversi arah, pembentukan instruksi, komunikasi antarnode, validasi parameter, dan perbandingan algoritma.

## Pengguaan AI
AI digunakan untuk memberikan referensi dalam penyusunan sistem lomba dan validasi readme. Pada sintaks, AI digunakan dalam penyusunan BSF, pada readme, AI membantu menyusun tabel pengujian.
