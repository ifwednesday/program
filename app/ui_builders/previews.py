"""Seções de pré-visualização de texto e botões de ação."""

import tkinter as tk
from typing import Callable, Dict

import customtkinter as ctk

from .components import ButtonFactory, LabelFactory
from .theme import (
    ACCENT,
    ACCENT_HOVER,
    BORDER,
    DANGER,
    DANGER_HOVER,
    FONT_FAMILY,
    NEUTRAL,
    NEUTRAL_HOVER,
    SUCCESS,
    SUCCESS_HOVER,
    SURFACE_CARD,
    SURFACE_INPUT,
    TEXT_PRIMARY,
    WARNING,
    WARNING_HOVER,
)


class PreviewBuilder:
    def __init__(self, app) -> None:
        self.app = app
        self.labels = LabelFactory(font=(FONT_FAMILY, 13, "bold"))
        self.buttons = ButtonFactory(font=(FONT_FAMILY, 11, "bold"))

    def build(
        self, parent: ctk.CTkFrame, preview_attr: str, commands: Dict[str, Callable]
    ) -> tk.Text:
        self.labels.create(parent, "Pré-visualização", width=200, height=32).pack(
            anchor="w", pady=(0, 8)
        )

        preview_container = ctk.CTkFrame(
            parent,
            corner_radius=14,
            fg_color=SURFACE_CARD,
            border_width=1,
            border_color=BORDER,
        )
        preview_container.pack(fill=tk.BOTH, expand=True, pady=(4, 6))

        text_widget = tk.Text(
            preview_container,
            height=25,
            wrap=tk.WORD,
            bg=SURFACE_INPUT,
            fg=TEXT_PRIMARY,
            font=(FONT_FAMILY, 11),
            borderwidth=0,
            highlightthickness=1,
            highlightcolor=BORDER,
            highlightbackground=BORDER,
            insertbackground=TEXT_PRIMARY,
        )
        text_widget.configure(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        setattr(self.app, preview_attr, text_widget)

        buttons_frame = ctk.CTkFrame(
            parent, corner_radius=12, fg_color=SURFACE_CARD, border_width=1, border_color=BORDER
        )
        buttons_frame.pack(fill=tk.X, pady=(8, 0))

        button_specs = [
            ("Gerar", commands["generate"], ACCENT, ACCENT_HOVER, "normal"),
            ("Copiar", commands["copy"], NEUTRAL, NEUTRAL_HOVER, "disabled"),
            ("Salvar .txt", commands["save"], SUCCESS, SUCCESS_HOVER, "disabled"),
            ("Limpar", commands["clear"], WARNING, WARNING_HOVER, "normal"),
            ("Sair", commands["exit"], DANGER, DANGER_HOVER, "normal"),
        ]

        for text, command, color, hover, state in button_specs:
            button = self.buttons.create(
                buttons_frame,
                text=text,
                command=command,
                fg_color=color,
                hover_color=hover,
                state=state,
            )
            button.pack(side=tk.LEFT, padx=(8 if text == "Gerar" else 0, 4), pady=8)
            if text == "Copiar":
                if preview_attr == "preview":
                    btn_name = "btn_copy"
                elif "casados" in preview_attr:
                    btn_name = "btn_copy_casados"
                elif "empresa" in preview_attr:
                    btn_name = "btn_copy_empresa"
                elif "imovel" in preview_attr:
                    btn_name = "btn_copy_imovel"
                else:
                    btn_name = "btn_copy3"
                setattr(self.app, btn_name, button)
            elif text == "Salvar .txt":
                if preview_attr == "preview":
                    btn_name = "btn_save"
                elif "casados" in preview_attr:
                    btn_name = "btn_save_casados"
                elif "empresa" in preview_attr:
                    btn_name = "btn_save_empresa"
                elif "imovel" in preview_attr:
                    btn_name = "btn_save_imovel"
                else:
                    btn_name = "btn_save3"
                setattr(self.app, btn_name, button)

        return text_widget
