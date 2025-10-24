"""Seções de pré-visualização de texto e botões de ação."""

import tkinter as tk
from typing import Callable, Dict

import customtkinter as ctk

from .components import ButtonFactory, LabelFactory


class PreviewBuilder:
    def __init__(self, app) -> None:
        self.app = app
        self.labels = LabelFactory(font=("Segoe UI", 14, "bold"))
        self.buttons = ButtonFactory(font=("Segoe UI", 11, "bold"))

    def build(
        self, parent: ctk.CTkFrame, preview_attr: str, commands: Dict[str, Callable]
    ) -> tk.Text:
        self.labels.create(parent, "Pré-visualização", width=200, height=32).pack(
            anchor="w", pady=(0, 8)
        )

        preview_container = ctk.CTkFrame(
            parent,
            corner_radius=12,
            fg_color="#3a3a3a",
            border_width=1,
            border_color="#4a4a4a",
        )
        preview_container.pack(fill=tk.BOTH, expand=True, pady=(4, 4))

        text_widget = tk.Text(
            preview_container,
            height=25,
            wrap=tk.WORD,
            bg="#2a2a2a",
            fg="#ffffff",
            font=("Segoe UI", 11),
            borderwidth=0,
            highlightthickness=1,
            highlightcolor="#4a4a4a",
            highlightbackground="#4a4a4a",
            insertbackground="#ffffff",
        )
        text_widget.configure(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        setattr(self.app, preview_attr, text_widget)

        buttons_frame = ctk.CTkFrame(parent, corner_radius=8, fg_color="#3a3a3a")
        buttons_frame.pack(fill=tk.X, pady=(8, 0))

        button_specs = [
            ("Gerar", commands["generate"], "#1f6aa5", "#1a5a8a", "normal"),
            ("Copiar", commands["copy"], "#4a4a4a", "#5a5a5a", "disabled"),
            ("Salvar .txt", commands["save"], "#2e7d32", "#256428", "disabled"),
            ("Limpar", commands["clear"], "#f57c00", "#db6e00", "normal"),
            ("Sair", commands["exit"], "#d32f2f", "#b71c1c", "normal"),
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
