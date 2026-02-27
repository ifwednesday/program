import tkinter as tk
import tkinter.font as tkfont

import customtkinter as ctk

try:
    from .ui_builders.theme import APP_BG, FONT_FAMILY
except ImportError:
    from ui_builders.theme import APP_BG, FONT_FAMILY  # type: ignore


def setup_styles(app: tk.Tk) -> None:
    ctk.set_appearance_mode("dark")
    # Removido set_default_color_theme para permitir corner_radius customizado

    try:
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family=FONT_FAMILY, size=11, weight="normal")
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(family=FONT_FAMILY, size=11)
    except Exception:  # noqa: BLE001
        pass

    app.configure(bg=APP_BG)
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)
