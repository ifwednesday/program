import tkinter as tk
import tkinter.font as tkfont

import customtkinter as ctk


def setup_styles(app: tk.Tk) -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    try:
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=11, weight="normal")
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(family="Segoe UI", size=11)
    except Exception:  # noqa: BLE001
        pass

    app.configure(bg="#1a1a1a")
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)
