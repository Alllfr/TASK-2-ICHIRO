# Task 2: Miru

Miru adalah pembalap yang menjalankan instruksi dari navigator. Miru menerima instruksi melalui ROS 2, menggerakkan turtle menggunakan turtlesim, dan melaporkan statusnya secara berkala.

Implementasi tugas ini mencakup pengelolaan antrean instruksi, komunikasi ROS 2, pengaturan kecepatan, gerak maju, belokan, dan laporan status. Bagian bonus berfokus pada pengurangan galat penghentian gerakan.

## A. Antrean Instruksi

Implementasi `InstructionQueue` menyimpan instruksi dalam antrean FIFO. Setiap instruksi memiliki `instruction_id`, `distance`, dan `turn`.

Instruksi hanya diterima apabila ID-nya lebih besar daripada ID terakhir yang diterima. Instruksi dengan ID duplikat atau lebih kecil akan diabaikan.

Langkah-langkah:

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

Langkah-langkah:

1. Membuat publisher bertipe `Twist` pada `/turtle1/cmd_vel`.
2. Membuat subscriber bertipe `Pose` pada `/turtle1/pose`.
3. Menyimpan pose terbaru melalui callback `on_pose()`.
4. Mengimplementasikan `publish_velocity()` untuk mengatur `linear.x` sebagai kecepatan maju dan `angular.z` sebagai kecepatan rotasi.

Implementasi perhitungan gerak:

![Implementasi Motion](assets/motion.png)

Implementasi komunikasi ROS 2:

![Implementasi Miru Node](assets/miru_node.png)

Pemeriksaan dapat dilakukan melalui `ros2 node info /miru`. Publisher dan subscriber harus muncul pada topik yang sesuai.

## C. Aba-aba GO dan Parameter

Miru menyimpan status lomba terbaru melalui subscriber `/race/state`. Gerakan dimulai ketika status lomba menunjukkan `GO`.

Kecepatan gerak dikendalikan melalui parameter `speed`, dengan batas `MIN_SPEED` sebesar 0,1 m/s dan `MAX_SPEED` sebesar 2,5 m/s.

Langkah-langkah:

1. Mendaftarkan parameter `speed` dengan nilai awal 1,0.
2. Mendaftarkan callback `on_parameter_change()` untuk memvalidasi perubahan parameter.
3. Menolak nilai di luar rentang yang diperbolehkan.
4. Membuat subscriber `/race/state` dengan callback `on_race_state()`.
5. Menyimpan status lomba terbaru untuk digunakan oleh state machine.

Implementasi GO dan parameter:

![Implementasi GO dan Parameter](assets/go_parameter.png)

Pengujian GO dan parameter:

![Pengujian GO dan Parameter](assets/test_go_parameter.png)

Pengujian parameter perlu mencakup nilai yang ditolak, misalnya 3,0 dan 0,05, serta nilai batas 2,5 yang diterima.

## D. Maju

Miru bergerak maju berdasarkan koordinat rencana, yaitu `planned_x`, `planned_y`, dan `planned_heading`.

Langkah-langkah:

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

Pengujian perlu memastikan Miru bergerak menuju titik tujuan berdasarkan posisi rencana dan dapat menyelesaikan instruksi dengan benar.

## E. Belok

Miru mendukung belokan 90 derajat ke kiri dan ke kanan.

Langkah-langkah:

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

Pengujian perlu mencakup belokan kiri dan kanan serta pemeriksaan orientasi akhir turtle.

## F. Laporan Status

Miru melaporkan status kepada navigator melalui `/miru/status` sebanyak 20 kali per detik.

Langkah-langkah:

1. Membuat publisher bertipe `DriverStatus` pada `/miru/status`.
2. Membuat timer dengan interval `STATUS_PERIOD` sebesar 0,05 detik.
3. Memeriksa apakah pose pertama telah diterima.
4. Mengisi pesan dengan state Miru, koordinat `x` dan `y`, orientasi `theta`, `current_id`, `done_id`, dan jumlah antrean.
5. Menerbitkan pesan menggunakan `self.status_publisher.publish(msg)`.

Implementasi publisher dan timer:

![Implementasi Publisher dan Timer Status](assets/status.png)

Implementasi fungsi laporan status:

![Implementasi Publish Status](assets/status_topic.png)

Verifikasi dapat dilakukan menggunakan `ros2 topic echo /miru/status` dan `ros2 topic hz /miru/status`. Frekuensi publikasi yang diharapkan adalah sekitar 20 Hz ketika pose tersedia.

## G. Bonus: Berhenti Lebih Tepat

Gerakan turtlesim memiliki jeda antara pengiriman perintah kecepatan dan penghentian gerakan. Akibatnya, turtle dapat melewati titik tujuan.

Untuk mengurangi galat penghentian, fungsi `drive_step()` dimodifikasi agar kecepatan berkurang ketika turtle mendekati target. Pada implementasi ini, kecepatan diturunkan ketika sisa jarak kurang dari 0,5 meter, sementara kondisi penyelesaian instruksi tetap menggunakan sisa jarak nol atau negatif.

Implementasi penghentian:

![Implementasi Precise Stop](assets/precise_stop.png)

Simulasi penghentian:

![Simulasi Precise Stop](assets/precise_stop_simulation.png)

### Metode pengukuran

Lakukan pengukuran untuk instruksi maju tiga kotak dengan kecepatan 0,5 m/s, 1,0 m/s, dan 2,5 m/s. Ulangi setiap pengukuran sebelum dan sesudah modifikasi.

Catat koordinat target, koordinat akhir, dan waktu tempuh setiap percobaan.

Galat posisi dihitung menggunakan:

e = √((x_aktual − x_target)² + (y_aktual − y_target)²)
### Hasil Pengujian Akurasi Berhenti Miru

| Kecepatan | Galat Lama (m) | Waktu Lama (s) | Galat Baru (m) | Waktu Baru (s) |
|---|---:|---:|---:|---:|
| 0.5 m/s | 0.05 | 6.0 | 0.0236 | 6.030 |
| 1.0 m/s | 0.10 | 3.0 | 0.0381 | 3.019 |
| 2.5 m/s | 0.25 | 1.2 | 0.1462 | 1.214 |

**Catatan:** Hasil baru merupakan rata-rata galat dan waktu dari instruksi 6–8 pada setiap kecepatan. Nilai lama menggunakan data referensi sebelumnya.

**Kesimpulan:** Implementasi baru menghasilkan galat berhenti rata-rata yang lebih kecil dibandingkan nilai referensi lama pada ketiga kecepatan yang diuji.

## Kesimpulan

Implementasi Miru menggabungkan pengelolaan antrean, komunikasi ROS 2, pengendalian gerak, belokan, dan laporan status. Perbaikan bonus berupaya mengurangi galat penghentian melalui perlambatan saat mendekati target.

Keberhasilan implementasi harus dikonfirmasi melalui pengujian otomatis dan simulasi. Hasil pengukuran bonus dicatat secara terpisah agar peningkatan akurasi dan perubahan waktu tempuh dapat dibandingkan.