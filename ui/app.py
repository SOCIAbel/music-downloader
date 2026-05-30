import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DEFAULT_DOWNLOAD_FOLDER, APP_TITLE
from core.downloader import download_audio, get_info, format_duration

HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".music_downloader_history.json")

# ─── Colores y estilos ────────────────────────────────────────────────────────
BG         = "#0f0f13"
BG2        = "#1a1a22"
BG3        = "#22222e"
ACCENT     = "#7c5cfc"
ACCENT2    = "#a78bfa"
SUCCESS    = "#4ade80"
ERROR      = "#f87171"
WARNING    = "#fbbf24"
TEXT       = "#f0f0f5"
TEXT_DIM   = "#6b6b80"
BORDER     = "#2e2e3e"
# ──────────────────────────────────────────────────────────────────────────────


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-50:], f, ensure_ascii=False, indent=2)
    except Exception:
        pass


class MusicDownloaderApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("660x700")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.folder = DEFAULT_DOWNLOAD_FOLDER
        self.history = load_history()
        self.download_thread = None
        self.is_downloading = False

        self._apply_styles()
        self._build_ui()
        self._refresh_history()

    # ── Estilos ttk ───────────────────────────────────────────────────────────
    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure("TProgressbar",
                        troughcolor=BG3,
                        background=ACCENT,
                        bordercolor=BG3,
                        lightcolor=ACCENT,
                        darkcolor=ACCENT2,
                        thickness=6)

        style.configure("TCombobox",
                        fieldbackground=BG3,
                        background=BG3,
                        foreground=TEXT,
                        selectbackground=ACCENT,
                        selectforeground=TEXT,
                        borderwidth=0)
        style.map("TCombobox", fieldbackground=[("readonly", BG3)],
                  selectbackground=[("readonly", BG3)],
                  selectforeground=[("readonly", TEXT)])

    # ── UI principal ──────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BG, pady=0)
        header.pack(fill="x", padx=0)

        header_inner = tk.Frame(header, bg=BG2, pady=18)
        header_inner.pack(fill="x")

        tk.Label(header_inner, text="🎵", font=("Segoe UI Emoji", 28),
                 bg=BG2, fg=ACCENT).pack()
        tk.Label(header_inner, text="Music Downloader",
                 font=("Segoe UI", 18, "bold"), bg=BG2, fg=TEXT).pack()
        tk.Label(header_inner, text="YouTube · SoundCloud · Bandcamp · TikTok · +1000 sitios",
                 font=("Segoe UI", 9), bg=BG2, fg=TEXT_DIM).pack()

        # Separador decorativo
        tk.Frame(self.root, bg=ACCENT, height=2).pack(fill="x")

        # Contenido principal
        main = tk.Frame(self.root, bg=BG, padx=30, pady=20)
        main.pack(fill="both", expand=True)

        # ── URL ──
        self._section_label(main, "🔗  URL del video / canción")
        url_frame = tk.Frame(main, bg=BG3, highlightbackground=BORDER,
                             highlightthickness=1)
        url_frame.pack(fill="x", pady=(4, 14))

        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var,
                                  font=("Segoe UI", 11), bg=BG3, fg=TEXT,
                                  insertbackground=ACCENT, relief="flat",
                                  bd=10)
        self.url_entry.pack(side="left", fill="x", expand=True)

        clear_btn = tk.Button(url_frame, text="✕", font=("Segoe UI", 10),
                              bg=BG3, fg=TEXT_DIM, relief="flat", bd=0,
                              cursor="hand2", command=lambda: self.url_var.set(""))
        clear_btn.pack(side="right", padx=8)
        self.url_entry.bind("<Return>", lambda e: self._start_download())

        # ── Fila: Formato + Calidad ──
        row = tk.Frame(main, bg=BG)
        row.pack(fill="x", pady=(0, 14))

        left = tk.Frame(row, bg=BG)
        left.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._section_label(left, "🎧  Formato")
        self.format_var = tk.StringVar(value="mp3")
        fmt_combo = ttk.Combobox(left, textvariable=self.format_var,
                                  values=["mp3", "m4a", "flac", "wav", "ogg"],
                                  state="readonly", font=("Segoe UI", 11), width=10)
        fmt_combo.pack(fill="x", pady=(4, 0))

        right = tk.Frame(row, bg=BG)
        right.pack(side="right", fill="x", expand=True, padx=(8, 0))
        self._section_label(right, "📶  Calidad (kbps)")
        self.quality_var = tk.StringVar(value="192")
        q_combo = ttk.Combobox(right, textvariable=self.quality_var,
                                values=["128", "192", "256", "320"],
                                state="readonly", font=("Segoe UI", 11), width=10)
        q_combo.pack(fill="x", pady=(4, 0))

        # ── Carpeta de descarga ──
        self._section_label(main, "📁  Carpeta de descarga")
        folder_frame = tk.Frame(main, bg=BG3, highlightbackground=BORDER,
                                highlightthickness=1)
        folder_frame.pack(fill="x", pady=(4, 18))

        self.folder_label = tk.Label(folder_frame, text=self.folder,
                                      font=("Segoe UI", 10), bg=BG3,
                                      fg=TEXT_DIM, anchor="w")
        self.folder_label.pack(side="left", fill="x", expand=True, padx=10, pady=8)

        folder_btn = tk.Button(folder_frame, text="Cambiar",
                               font=("Segoe UI", 9, "bold"),
                               bg=ACCENT, fg=TEXT, relief="flat", bd=0,
                               padx=12, pady=5, cursor="hand2",
                               command=self._choose_folder)
        folder_btn.pack(side="right", padx=6, pady=6)

        # ── Botón Descargar ──
        self.download_btn = tk.Button(
            main, text="⬇  DESCARGAR",
            font=("Segoe UI", 13, "bold"),
            bg=ACCENT, fg=TEXT, relief="flat", bd=0,
            padx=20, pady=12, cursor="hand2",
            activebackground=ACCENT2, activeforeground=TEXT,
            command=self._start_download
        )
        self.download_btn.pack(fill="x", pady=(0, 10))

        # ── Progreso ──
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main, variable=self.progress_var,
                                             maximum=100, mode="determinate")
        self.progress_bar.pack(fill="x", pady=(0, 6))

        self.status_var = tk.StringVar(value="Listo para descargar")
        self.status_label = tk.Label(main, textvariable=self.status_var,
                                      font=("Segoe UI", 10), bg=BG,
                                      fg=TEXT_DIM, anchor="w")
        self.status_label.pack(fill="x")

        # ── Historial ──
        tk.Frame(main, bg=BORDER, height=1).pack(fill="x", pady=14)
        hist_header = tk.Frame(main, bg=BG)
        hist_header.pack(fill="x")
        self._section_label(hist_header, "🕓  Historial reciente")
        tk.Button(hist_header, text="Limpiar", font=("Segoe UI", 8),
                  bg=BG, fg=TEXT_DIM, relief="flat", bd=0, cursor="hand2",
                  command=self._clear_history).pack(side="right")

        self.hist_frame = tk.Frame(main, bg=BG)
        self.hist_frame.pack(fill="both", expand=True, pady=(6, 0))

    # ── Helpers UI ────────────────────────────────────────────────────────────
    def _section_label(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"),
                 bg=parent["bg"], fg=TEXT_DIM).pack(anchor="w")

    def _set_status(self, msg, color=TEXT_DIM):
        self.status_var.set(msg)
        self.status_label.config(fg=color)

    def _choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder)
        if folder:
            self.folder = folder
            self.folder_label.config(text=folder)

    # ── Historial ─────────────────────────────────────────────────────────────
    def _refresh_history(self):
        for w in self.hist_frame.winfo_children():
            w.destroy()

        if not self.history:
            tk.Label(self.hist_frame, text="Sin descargas aún",
                     font=("Segoe UI", 9), bg=BG, fg=TEXT_DIM).pack(anchor="w")
            return

        for item in reversed(self.history[-6:]):
            row = tk.Frame(self.hist_frame, bg=BG3, pady=6, padx=10)
            row.pack(fill="x", pady=2)
            tk.Label(row, text="🎵", font=("Segoe UI Emoji", 10),
                     bg=BG3, fg=ACCENT).pack(side="left")
            info = tk.Frame(row, bg=BG3)
            info.pack(side="left", fill="x", expand=True, padx=8)
            tk.Label(info, text=item.get("title", "?")[:55],
                     font=("Segoe UI", 9, "bold"), bg=BG3, fg=TEXT,
                     anchor="w").pack(anchor="w")
            tk.Label(info,
                     text=f"{item.get('uploader','?')} · {item.get('duration','?')} · {item.get('date','')}",
                     font=("Segoe UI", 8), bg=BG3, fg=TEXT_DIM,
                     anchor="w").pack(anchor="w")

    def _clear_history(self):
        self.history = []
        save_history(self.history)
        self._refresh_history()

    # ── Descarga ──────────────────────────────────────────────────────────────
    def _start_download(self):
        if self.is_downloading:
            return

        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("URL vacía", "Por favor ingresa una URL válida.")
            return

        self.is_downloading = True
        self.download_btn.config(state="disabled", text="⏳  Descargando...", bg=BG3)
        self.progress_var.set(0)
        self._set_status("Conectando...", WARNING)

        self.download_thread = threading.Thread(
            target=self._download_worker, args=(url,), daemon=True
        )
        self.download_thread.start()

    def _on_progress(self, d):
        if d["status"] == "downloading":
            pct = d.get("_percent_str", "0%").strip().replace("%", "")
            try:
                self.root.after(0, self.progress_var.set, float(pct))
                self.root.after(0, self._set_status,
                                f"Descargando... {pct}%  –  {d.get('_speed_str','').strip()}",
                                ACCENT2)
            except Exception:
                pass
        elif d["status"] == "finished":
            self.root.after(0, self._set_status, "Convirtiendo a MP3...", WARNING)
            self.root.after(0, self.progress_var.set, 99)

    def _download_worker(self, url):
        try:
            result = download_audio(
                url=url,
                output_folder=self.folder,
                on_progress=self._on_progress,
                audio_format=self.format_var.get(),
            )
            entry = {
                "title": result["title"],
                "uploader": result["uploader"],
                "duration": format_duration(result["duration"]),
                "date": datetime.now().strftime("%d/%m/%Y"),
            }
            self.history.append(entry)
            save_history(self.history)

            self.root.after(0, self._on_success, result["title"])
        except Exception as e:
            self.root.after(0, self._on_error, str(e))

    def _on_success(self, title):
        self.progress_var.set(100)
        self._set_status(f"✅  Descargado: {title}", SUCCESS)
        self.download_btn.config(state="normal", text="⬇  DESCARGAR", bg=ACCENT)
        self.is_downloading = False
        self._refresh_history()

    def _on_error(self, error):
        self.progress_var.set(0)
        self._set_status(f"❌  Error: {error}", ERROR)
        self.download_btn.config(state="normal", text="⬇  DESCARGAR", bg=ACCENT)
        self.is_downloading = False
