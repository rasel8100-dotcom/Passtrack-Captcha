from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import io
from PIL import Image
import pytesseract
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS setup - allow requests from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CaptchaRequest(BaseModel):
    image: str

@app.get("/")
async def root():
    return {"status": "CAPTCHA Solver API is running"}

@app.post("/api/solve")
async def solve_captcha(req: CaptchaRequest):
    """
    Solve CAPTCHA from base64 image
    
    Request: {"image": "base64_string"}
    Response: {"captcha": "solved_text", "status": "success"}
    """
    try:
        logger.info("Received CAPTCHA solve request")
        
        img_str = req.image
        
        # Remove data URL prefix if exists
        if "," in img_str:
            img_str = img_str.split(",")[1]
        
        logger.info(f"Image string length: {len(img_str)}")
        
        # Decode base64
        try:
            img_bytes = base64.b64decode(img_str)
        except Exception as e:
            logger.error(f"Base64 decode error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid base64 image: {str(e)}")
        
        logger.info(f"Image bytes length: {len(img_bytes)}")
        
        # Open image and convert to grayscale
        try:
            image = Image.open(io.BytesIO(img_bytes)).convert("L")
            logger.info(f"Image opened successfully: {image.size}")
        except Exception as e:
            logger.error(f"Image open error: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to open image: {str(e)}")
        
        # Optional: Image preprocessing for better OCR
        # You can uncomment and modify these based on needs
        # from PIL import ImageEnhance
        # enhancer = ImageEnhance.Contrast(image)
        # image = enhancer.enhance(2)
        
        # OCR processing
        try:
            # Tesseract config:
            # --psm 6: Assume a single uniform block of text
            # -c tessedit_char_whitelist: Only recognize these characters
            text = pytesseract.image_to_string(
                image, 
                config='--psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            ).strip()
            
            logger.info(f"OCR Result: {text}")
            
            if not text:
                logger.warning("OCR returned empty string")
                return {
                    "captcha": "",
                    "status": "success",
                    "warning": "OCR could not read text"
                }
            
            return {
                "captcha": text,
                "status": "success",
                "length": len(text)
            }
            
        except Exception as e:
            logger.error(f"OCR error: {e}")
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/api/solve/url")
async def solve_captcha_from_url(req: dict):
    """
    Solve CAPTCHA from URL
    Request: {"url": "image_url"}
    """
    try:
        import requests
        
        url = req.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL required")
        
        response = requests.get(url, timeout=5)
        img_bytes = response.content
        
        image = Image.open(io.BytesIO(img_bytes)).convert("L")
        
        text = pytesseract.image_to_string(
            image,
            config='--psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ).strip()
        
        return {
            "captcha": text,
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"URL fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
