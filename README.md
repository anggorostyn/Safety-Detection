# 🦺 Deteksi APD Otomatis dengan YOLOv5, Streamlit, dan ESP32

Proyek ini merupakan sistem deteksi otomatis penggunaan Alat Pelindung Diri (APD) menggunakan model YOLOv8 yang dijalankan melalui aplikasi Streamlit. Sistem ini terhubung ke perangkat ESP32 melalui HTTP untuk mengaktifkan LED dan buzzer berdasarkan hasil deteksi dari kamera USB. APD yang dideteksi meliputi: Masker (Mask), Helm Pengaman (Hardhat), dan Rompi Keselamatan (Safety Vest).

## 🚀 Cara Menjalankan Program

1. Clone repository ke komputer lokal:
```bash
git clone https://github.com/username/nama-repo.git
cd nama-repo
```

2. (Opsional) Buat virtual environment:
```bash
python -m venv venv
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows
```

3. Install semua dependensi:
```bash
pip install -r requirements.txt
```

4. Letakkan model YOLO hasil training (`best.pt`) ke dalam folder `model/`.
Model harus mengenali label berikut: Mask, Hardhat, Safety Vest.

5. Jalankan aplikasi Streamlit:
```bash
streamlit run app.py
```

6. Akses aplikasi di browser:
```
http://localhost:8501
```

## ⚙️ Pengaturan dalam Kode

Alamat IP ESP32 dapat diatur di bagian atas file `app.py`:
```python
ESP32_IP = "http://192.168.x.x"  # Ganti dengan IP ESP32 Anda
```

Indeks kamera USB dapat disesuaikan:
```python
USB_CAM_INDEX = 1
```

## 📋 Fitur Program

- Antarmuka pengguna interaktif dengan Streamlit
- Deteksi otomatis 3 jenis APD menggunakan YOLOv5
- Komunikasi langsung dengan ESP32 menggunakan HTTP
- Logging otomatis hasil deteksi ke file .csv
- Tampilan visual hasil deteksi di UI

## 🌐 Integrasi dengan ESP32

ESP32 harus dikonfigurasi untuk menerima request HTTP dari aplikasi Streamlit. Endpoint yang harus tersedia:
- `/apd_lengkap` → LED hijau dan buzzer menyala
- `/apd_tidak_lengkap` → LED merah dan buzzer menyala
- `/kosong` → Semua indikator dimatikan

ESP32 dapat menggunakan sketch Arduino sederhana untuk merespons HTTP GET sesuai endpoint di atas.

## 🧠 Cara Kerja Sistem

1. Streamlit membuka kamera USB.
2. YOLOv8 melakukan deteksi objek.
3. Program mengecek label yang terdeteksi.
4. Jika lengkap → request ke `/apd_lengkap`, jika tidak → `/apd_tidak_lengkap`, jika kosong → `/kosong`
5. Hasil deteksi dicatat otomatis ke log `.csv`

## 📁 Logging Deteksi

File log berada di: `logs/log_deteksi.csv`  
Format:
```
[Waktu], [Status Deteksi], [Label yang Terdeteksi]
```

Contoh:
```
2025-06-27 21:33:12, Lengkap, Mask,Hardhat,Safety Vest
2025-06-27 21:33:18, Tidak Lengkap, Mask,Hardhat
```

## 📦 Contoh Isi requirements.txt

```
streamlit
ultralytics
opencv-python
Pillow
requests
```

## 💡 Tips Tambahan

- Pastikan ESP32 dan PC berada di jaringan WiFi yang sama
- Gunakan model YOLO hasil pelatihan dengan label Mask, Hardhat, Safety Vest
- Jika kamera tidak terbaca, coba ubah `USB_CAM_INDEX` menjadi 0 atau 2


