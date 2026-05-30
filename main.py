import tkinter as tk
from ui.app import MusicDownloaderApp

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    app = MusicDownloaderApp(root)
    root.mainloop()
