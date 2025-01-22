from ultralytics import YOLO
import cv2

# Load the YOLO model
model = YOLO(r'model/best.pt')  # Path ke model kamu

# Inisialisasi webcam
cap = cv2.VideoCapture(1)  # '0' untuk webcam default, sesuaikan jika menggunakan kamera eksternal (misalnya, '1' atau '2')

if not cap.isOpened():
    print("Error: Tidak dapat mengakses kamera.")
    exit()

# Loop untuk membaca frame dari kamera secara langsung
while True:
    ret, frame = cap.read()  # Baca frame dari kamera
    if not ret:
        print("Error: Tidak dapat membaca frame dari kamera.")
        break

    # Gunakan model YOLO untuk melakukan prediksi pada frame
    results = model.predict(source=frame, imgsz=640, conf=0.4)

    # Gambarkan hasil deteksi pada frame
    annotated_frame = results[0].plot()

    # Tampilkan frame dengan hasil deteksi
    cv2.imshow('Pendeteksi Alat Pelindung Diri', annotated_frame)

    # Tekan 'q' untuk keluar dari loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Lepaskan resource kamera dan tutup semua jendela OpenCV
cap.release()
cv2.destroyAllWindows()
