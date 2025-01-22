import streamlit as st
from PIL import Image
from ultralytics import YOLO
import cv2
import os
import shutil

# Memuat model YOLO
model = YOLO('model/best.pt')

@st.cache_data
def proses_gambar(file_unggah, _model, ambang_keyakinan):
    # Membaca gambar
    gambar = Image.open(file_unggah)

    # Menjalankan inferensi dengan ambang keyakinan yang diberikan
    hasil = _model(gambar, conf=ambang_keyakinan)
    for hasil_deteksi in hasil:
        hasil_deteksi.save(filename='hasil.jpg')

    # Membuka hasil deteksi
    hasil_gambar = Image.open('hasil.jpg')
    return hasil_gambar


def simpan_file_unggah(file_unggah):
    # Menyimpan file unggahan video
    nama_file = "video_sample.mp4"
    os.makedirs("uploads", exist_ok=True)
    with open(os.path.join("uploads", nama_file), "wb") as f:
        f.write(file_unggah.getbuffer())
    return os.path.join("uploads", nama_file)


def hapus_direktori(direktori):
    # Menghapus isi direktori jika ada
    if os.path.exists(direktori):
        shutil.rmtree(direktori)


def tampilkan_frame_deteksi(ambang, model, st_frame, gambar, tampilkan_pelacakan=None, pelacak=None):
    # Menampilkan hasil deteksi atau pelacakan pada frame video
    if tampilkan_pelacakan:
        hasil = model.track(gambar, conf=ambang, persist=True, tracker=pelacak)
    else:
        hasil = model.predict(gambar, conf=ambang)

    hasil_plot = hasil[0].plot()
    st_frame.image(hasil_plot,
                   caption='Hasil Deteksi Video',
                   channels="BGR",
                   use_column_width=True
                   )


def main():
    # Opsi sidebar
    st.sidebar.title("Pengaturan")
    tipe_input = st.sidebar.radio("Pilih Jenis Input:", ["Gambar", "Video", "Webcam"])

    # Bagian ambang keyakinan
    st.sidebar.title("Ambang Keyakinan")
    st.sidebar.write("""
        Sesuaikan ambang keyakinan untuk mengontrol sensitivitas deteksi:
        - **Keyakinan Tinggi (0.7 - 1.0):** Deteksi lebih ketat dan akurat.
        - **Keyakinan Sedang (0.5 - 0.7):** Keseimbangan antara akurasi dan deteksi.
        - **Keyakinan Rendah (0.3 - 0.5):** Lebih banyak deteksi tetapi mungkin ada kesalahan positif.
    """)
    ambang_keyakinan = st.sidebar.slider(
        "Atur Ambang Keyakinan",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Atur nilai ini untuk menyeimbangkan antara akurasi dan deteksi."
    )

    if ambang_keyakinan > 0.75:
        st.sidebar.success("Keyakinan Tinggi: Deteksi lebih ketat.")
    elif 0.5 <= ambang_keyakinan <= 0.75:
        st.sidebar.info("Keyakinan Sedang: Deteksi seimbang.")
    else:
        st.sidebar.warning("Keyakinan Rendah: Mungkin ada kesalahan deteksi.")

    # Aplikasi utama
    if tipe_input == "Gambar":
        st.title("Deteksi PPE (Alat Pelindung Diri)")
        opsi = st.radio(
            "Pilih Sumber Gambar:",
            ("Unggah Gambar", "Ambil Gambar"),
            horizontal=True,
        )

        if opsi == "Unggah Gambar":
            file_unggah = st.file_uploader(
                "Unggah gambar PPE (Alat Pelindung Diri):",
                type=["jpg", "jpeg", "png"]
            )

            if file_unggah is not None:
                hasil_gambar = proses_gambar(file_unggah, model, ambang_keyakinan)
                st.image(hasil_gambar, caption='Hasil Deteksi PPE', use_column_width=True)

        elif opsi == "Ambil Gambar":
            gambar = st.camera_input("Ambil gambar menggunakan webcam:")
            if gambar is not None:
                hasil_gambar = proses_gambar(gambar, model, ambang_keyakinan)
                st.image(hasil_gambar, caption='Hasil Deteksi PPE', use_column_width=True)

    elif tipe_input == "Video":
        # Menghapus direktori unggahan
        hapus_direktori("uploads")
        st.title("Unggah Video untuk Deteksi PPE")
        file_video = st.file_uploader(
            "Unggah video (Max 10MB):",
            type=["mp4"]
        )

        if file_video is not None:
            simpan_file_unggah(file_video)
            video_bytes = file_video.read()
            st.video(video_bytes)
            st.write("Memproses video untuk deteksi, harap tunggu...")
            try:
                vid_cap = cv2.VideoCapture('uploads/video_sample.mp4')
                st_frame = st.empty()
                while vid_cap.isOpened():
                    sukses, gambar = vid_cap.read()
                    if sukses:
                        tampilkan_frame_deteksi(ambang_keyakinan, model, st_frame, gambar)
                    else:
                        vid_cap.release()
                        break
            except Exception as e:
                st.sidebar.error(f"Kesalahan dalam memproses video: {str(e)}")

    elif tipe_input == "Webcam":
        st.title("Deteksi PPE Menggunakan Webcam")
        st.write("Menyiapkan webcam untuk deteksi, harap tunggu...")

        sumber_webcam = st.sidebar.radio("Pilih Sumber Kamera:", ["Webcam", "Kamera USB"])
        sumber_webcam = 0 if sumber_webcam == "Webcam" else 1

        try:
            vid_cap = cv2.VideoCapture(sumber_webcam)
            st_frame = st.empty()
            while vid_cap.isOpened():
                sukses, gambar = vid_cap.read()
                if sukses:
                    tampilkan_frame_deteksi(ambang_keyakinan, model, st_frame, gambar)
                else:
                    vid_cap.release()
                    break
        except Exception as e:
            st.sidebar.error(f"Kesalahan dalam penggunaan webcam: {str(e)}")


if __name__ == "__main__":
    main()
