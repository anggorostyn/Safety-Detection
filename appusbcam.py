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
ESP32_IP = "http://172.20.10.3"  
MODEL_PATH = "model/best.pt"      
USB_CAM_INDEX = 1                

# ------------------------------
# MUAT MODEL YOLO
# ------------------------------
model = YOLO(MODEL_PATH)

# ------------------------------
# FUNGSI: Kirim perintah ke ESP32
# ------------------------------
def kirim_perintah_ke_esp32(labels):
    required_classes = {'Mask', "Hardhat", "Safety Vest"}
    detected = set([label for label in labels if label in required_classes])
    
    try:
        if not labels:
            # Tidak ada deteksi apapun
            requests.get(f"{ESP32_IP}/kosong", timeout=1)
            log_deteksi("Tidak Ada Objek", [])
        elif detected == required_classes:
            # Semua APD lengkap
            requests.get(f"{ESP32_IP}/apd_lengkap", timeout=1)
            log_deteksi("Lengkap", labels)
        else:
            # APD tidak lengkap
            requests.get(f"{ESP32_IP}/apd_tidak_lengkap", timeout=1)
            log_deteksi("Tidak Lengkap", labels)
    except:
        print("ESP32 tidak merespon. Periksa koneksi.")

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
    names = model.names
    label_indices = hasil[0].boxes.cls.tolist()
    labels = [names[int(i)] for i in label_indices]

    kirim_perintah_ke_esp32(labels)

    hasil_plot = hasil[0].plot()
    st_frame.image(hasil_plot, caption='Hasil Deteksi APD', channels="BGR", use_column_width=True)

# ------------------------------
# FUNGSI UTAMA STREAMLIT
# ------------------------------
def main():
    st.set_page_config(page_title="Deteksi APD via USB Camera", layout="centered")
    st.title("🧠 Deteksi Alat Pelindung Diri (APD) dengan USB Camera")
    st.markdown("Menggunakan YOLO dan Streamlit, serta kontrol aktuator via ESP32.")

    st.sidebar.header("⚙️ Pengaturan")
    ambang_keyakinan = st.sidebar.slider(
        "Ambang Keyakinan Deteksi", min_value=0.0, max_value=1.0, value=0.5, step=0.05
    )

    if st.button("▶️ Mulai Deteksi dari USB Camera"):
        try:
            cap = cv2.VideoCapture(USB_CAM_INDEX)
            if not cap.isOpened():
                st.error("Gagal membuka kamera USB. Coba ganti indeks kamera.")
                return
            
            st_frame = st.empty()

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    st.warning("Gagal membaca frame dari USB camera.")
                    break
                tampilkan_frame_deteksi(ambang_keyakinan, model, st_frame, frame)

        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca kamera: {e}")
        finally:
            cap.release()

if __name__ == "__main__":
    main()
