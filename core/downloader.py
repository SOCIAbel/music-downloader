import yt_dlp
import os
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DEFAULT_DOWNLOAD_FOLDER, DEFAULT_FORMAT, AUDIO_QUALITY


def download_audio(url: str, output_folder: str = None, on_progress=None, audio_format: str = None) -> dict:
    """
    Descarga audio de una URL.
    Soporta YouTube, SoundCloud, Bandcamp, TikTok, Twitter/X y +1000 sitios más.
    """
    folder = output_folder or DEFAULT_DOWNLOAD_FOLDER
    fmt = audio_format or DEFAULT_FORMAT

    os.makedirs(folder, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": fmt,
            "preferredquality": AUDIO_QUALITY,
        }],
        "quiet": True,
        "no_warnings": True,
    }

    if on_progress:
        ydl_opts["progress_hooks"] = [on_progress]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return {
            "title": info.get("title", "Desconocido"),
            "duration": info.get("duration", 0),
            "uploader": info.get("uploader", "Desconocido"),
            "thumbnail": info.get("thumbnail", ""),
            "ext": fmt,
        }


def get_info(url: str) -> dict:
    """Obtiene info del video/audio sin descargar."""
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title", "Desconocido"),
            "duration": info.get("duration", 0),
            "uploader": info.get("uploader", "Desconocido"),
            "thumbnail": info.get("thumbnail", ""),
        }


def format_duration(seconds: int) -> str:
    if not seconds:
        return "??:??"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"
