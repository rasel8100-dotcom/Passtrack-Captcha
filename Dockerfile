FROM python:3.10-slim

# Tesseract OCR এবং অন্যান্য dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Requirements install করো
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code copy করো
COPY main.py .

# Port expose
EXPOSE 10000

# Backend run করো
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
