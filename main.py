from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import io
from PIL import Image
import pytesseract

app = FastAPI()

class CaptchaRequest(BaseModel):
    image: str

@app.post("/api/solve")
async def solve_captcha(req: CaptchaRequest):
    try:
        img_str = req.image
        if "," in img_str:
            img_str = img_str.split(",")[1]
            
        img_bytes = base64.b64decode(img_str)
        image = Image.open(io.BytesIO(img_bytes)).convert("L") # Grayscale
        
        # OCR প্রসেসিং
        text = pytesseract.image_to_string(image, config='--psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ').strip()
        
        return {"captcha": text, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
