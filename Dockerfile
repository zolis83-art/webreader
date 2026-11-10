FROM python:3.10-slim

WORKDIR /app

# Rendszerfüggőségek (FFmpeg stb.) telepítése
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python csomagok telepítése
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projekt fájlok és a modell másolása
COPY . .

# Port megnyitása és futtatás
EXPOSE 10000
CMD ["python", "app.py"]
