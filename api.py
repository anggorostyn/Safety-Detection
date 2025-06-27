from fastapi import FastAPI, File, UploadFile
import cv2
import numpy as np
from ultralytics import YOLO
import os

app = FastAPI()
model = YOLO('model/best.pt')

def proses_gambar(gambar):
    hasil = model(gambar, conf=0.5)
    for deteksi in hasil:
        deteksi.save('hasil.jpg')
    hasil_gambar = cv2.imread('hasil.jpg')
    labels = [deteksi.names[int(cls)] for cls in deteksi.boxes.cls]
    return "APD_Lengkap" if all(label in labels for label in ['helm', 'rompi']) else "APD_Tidak_Lengkap", hasil_gambar

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return "Error"
        status, _ = proses_gambar(img)
        return status
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8501)