# Dockerfile (Versi Baru dengan stress-ng)

FROM python:3.9-slim
WORKDIR /app

# Install stress-ng sebagai root sebelum menyalin file aplikasi
RUN apt-get update && apt-get install -y stress-ng && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]