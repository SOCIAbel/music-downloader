# 🎵 Music Downloader

Aplicación de escritorio para descargar música desde YouTube, SoundCloud, Bandcamp, TikTok y más de 1000 sitios.

## ✅ Requisitos

- Python 3.8+
- ffmpeg instalado en el sistema

## 📦 Instalación

### 1. Instalar dependencias Python
```bash
pip install -r requirements.txt
```

### 2. Instalar ffmpeg

**Windows:**
```bash
winget install ffmpeg
```
O descárgalo de https://ffmpeg.org/download.html y agrégalo al PATH.

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install ffmpeg
```

## 🚀 Ejecutar

```bash
python main.py
```

## 🎧 Formatos soportados
- MP3, M4A, FLAC, WAV, OGG

## 🌐 Sitios compatibles
YouTube, SoundCloud, Bandcamp, TikTok, Twitter/X, Facebook, Vimeo, Dailymotion, y +1000 más.

## 📁 Estructura
```
music-downloader/
├── main.py          # Punto de entrada
├── config.py        # Configuración
├── requirements.txt
├── core/
│   └── downloader.py  # Lógica de descarga (yt-dlp)
└── ui/
    └── app.py         # Interfaz gráfica (tkinter)
```
"# music-downloader" 
