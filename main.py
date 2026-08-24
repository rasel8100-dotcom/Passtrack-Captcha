from fastapi import FastAPI, UploadFile, File
import cv2
import numpy as np
import pytesseract

app = FastAPI()

@app.get("/")
def home():
    return {"status": "OCR Engine Active"}

@app.post("/solve")
async def solve_captcha(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    # Noise Reduction & Thresholding
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # OCR Read (Alphanumeric restrict)
    text = pytesseract.image_to_string(thresh, config='--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
    return {"captcha": text.replace(" ", "").strip()}
