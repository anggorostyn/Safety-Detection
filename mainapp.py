import streamlit as st
from PIL import Image
from ultralytics import YOLO
import cv2
import os
import requests
from datetime import datetime
import csv

# ------------------------------
# KONFIGURASI
# ------------------------------
ESP32_IP = "http://192.168.1.13"  # Ganti IP sesuai ESP32-CAM kamu
ESP32_STREAM_URL = f"{ESP32_IP}/stream"
MODEL_PATH = "model/best.pt"  # Ganti jika beda path model

# ------------------------------
# MUAT MODEL YOLO
# ------------------------------
model = YOLO(MODEL_PATH)

# ------------------------------
# FUNGSI: Kirim perintah ke ESP32
# ------------------------------
def kirim_perintah_ke_esp32(labels):
    required_classes = {'Hardhat', 'Mask', 'Vest'}
    detected = set([label for label in labels if label in required_classes])
    
    if not labels:
        # Tidak ada deteksi apapun
        requests.get(f"{ESP32_IP}/kosong")
        log_deteksi("Tidak Ada Objek", [])
    elif detected == required_classes:
        # Semua APD lengkap
        requests.get(f"{ESP32_IP}/apd_lengkap")
        log_deteksi("Lengkap", labels)
    else:
        # APD tidak lengkap
        requests.get(f"{ESP32_IP}/apd_tidak_lengkap")
        log_deteksi("Tidak Lengkap", labels)


# ------------------------------
# FUNGSI: Logging
# ------------------------------
def log_deteksi(status, labels):
    os.makedirs("logs", exist_ok=True)
    log_path = "logs/log_deteksi.csv"
    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([waktu, status, ",".join(labels)])

# ------------------------------
# FUNGSI: Deteksi dan tampilkan
# ------------------------------
def tampilkan_frame_deteksi(ambang, model, st_frame, frame):
    hasil = model.predict(frame, conf=ambang)
    names = model.names  # index ke nama class
    label_indices = hasil[0].boxes.cls.tolist()
    labels = [names[int(i)] for i in label_indices]

    kirim_perintah_ke_esp32(labels)

    hasil_plot = hasil[0].plot()
    st_frame.image(hasil_plot, caption='Hasil Deteksi APD', channels="BGR", use_column_width=True)

# ------------------------------
# FUNGSI UTAMA STREAMLIT
# ------------------------------
def main():
    st.set_page_config(page_title="Deteksi APD ESP32-CAM", layout="centered")
    st.title("🚨 Deteksi Alat Pelindung Diri (APD)")
    st.markdown("Sistem deteksi APD real-time dari ESP32-CAM menggunakan YOLO dan Streamlit.")

    st.sidebar.header("⚙️ Pengaturan")
    ambang_keyakinan = st.sidebar.slider(
        "Ambang Keyakinan Deteksi", min_value=0.0, max_value=1.0, value=0.5, step=0.05
    )

    if st.button("▶️ Mulai Deteksi dari ESP32-CAM"):
        try:
            cap = cv2.VideoCapture(ESP32_STREAM_URL)
            st_frame = st.empty()

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    st.warning("Gagal membaca stream dari ESP32-CAM.")
                    break
                tampilkan_frame_deteksi(ambang_keyakinan, model, st_frame, frame)

        except Exception as e:
            st.error(f"Terjadi kesalahan saat koneksi ESP32-CAM: {e}")

if __name__ == "__main__":
    main()
