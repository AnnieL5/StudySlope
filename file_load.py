import tkinter as tk
from tkinter import filedialog

def load_text_file():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        filetypes=[("Text Files", "*.txt")]
    )

    root.destroy()

    if not file_path:
        return ""

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()