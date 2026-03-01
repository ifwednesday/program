"""Aba para extração de dados de documentos (PDF/imagens)."""

import tkinter as tk

import customtkinter as ctk

try:
    from ..ui_builders.theme import (
        ACCENT,
        ACCENT_HOVER,
        BORDER,
        FONT_FAMILY,
        SURFACE_CARD,
        SURFACE_INPUT,
        SURFACE_SUBTLE,
        TEXT_MUTED,
        TEXT_PRIMARY,
    )
except ImportError:
    from ui_builders.theme import (  # type: ignore
        ACCENT,
        ACCENT_HOVER,
        BORDER,
        FONT_FAMILY,
        SURFACE_CARD,
        SURFACE_INPUT,
        SURFACE_SUBTLE,
        TEXT_MUTED,
        TEXT_PRIMARY,
    )

TARGET_OPTIONS = [
    "MODELO SIMPLES",
    "CERTIDÃO",
    "CASADOS - Pessoa 1",
    "CASADOS - Pessoa 2",
    "EMPRESA - Representante",
    "EMPRESA - Dados da Empresa",
    "IMÓVEIS",
]

TREATMENT_OPTIONS = ["Automático", "Sr.", "Sra.", "Dr.", "Dra."]


def build_tab_extracao(
    notebook: ctk.CTkTabview, tab_extracao: ctk.CTkFrame, app
) -> None:
    if not hasattr(app, "extraction_target"):
        app.extraction_target = tk.StringVar(value="MODELO SIMPLES")
    if not hasattr(app, "extraction_treatment"):
        app.extraction_treatment = tk.StringVar(value="Automático")
    if not hasattr(app, "extraction_auto_generate"):
        app.extraction_auto_generate = tk.BooleanVar(value=True)
    if not hasattr(app, "extraction_files"):
        app.extraction_files = []
    if not hasattr(app, "extraction_data"):
        app.extraction_data = {}
    if not hasattr(app, "extraction_raw_text"):
        app.extraction_raw_text = ""

    container = ctk.CTkFrame(tab_extracao, corner_radius=16, fg_color=SURFACE_CARD)
    container.pack(fill="both", expand=True, padx=10, pady=5)

    left = ctk.CTkScrollableFrame(container, corner_radius=16, fg_color=SURFACE_SUBTLE)
    left.pack(side="left", fill="both", expand=False, padx=(0, 10))
    left.configure(width=470)

    right = ctk.CTkFrame(
        container,
        corner_radius=16,
        fg_color=SURFACE_SUBTLE,
        border_width=1,
        border_color=BORDER,
    )
    right.pack(side="left", fill="both", expand=True)

    ctk.CTkLabel(
        left,
        text="EXTRAÇÃO DE DADOS",
        font=(FONT_FAMILY, 16, "bold"),
        text_color=TEXT_PRIMARY,
    ).pack(anchor="w", padx=14, pady=(14, 2))

    ctk.CTkLabel(
        left,
        text="Envie PDF/imagens, extraia dados e aplique na qualificação desejada.",
        font=(FONT_FAMILY, 11),
        text_color=TEXT_MUTED,
    ).pack(anchor="w", padx=14, pady=(0, 12))

    ctk.CTkButton(
        left,
        text="Selecionar PDF/Imagens",
        command=app.handlers.on_extraction_select_files,
        fg_color=ACCENT,
        hover_color=ACCENT_HOVER,
        text_color=TEXT_PRIMARY,
        font=(FONT_FAMILY, 11, "bold"),
        corner_radius=12,
        border_width=1,
        border_color=BORDER,
        height=36,
    ).pack(fill="x", padx=14, pady=(0, 8))

    app.extraction_files_info = ctk.CTkLabel(
        left,
        text="Nenhum arquivo selecionado",
        font=(FONT_FAMILY, 10),
        text_color=TEXT_MUTED,
    )
    app.extraction_files_info.pack(anchor="w", padx=14, pady=(0, 6))

    app.extraction_files_box = ctk.CTkTextbox(
        left,
        height=115,
        corner_radius=12,
        fg_color=SURFACE_INPUT,
        border_width=1,
        border_color=BORDER,
        text_color=TEXT_PRIMARY,
        font=(FONT_FAMILY, 10),
        wrap="word",
    )
    app.extraction_files_box.pack(fill="x", padx=14, pady=(0, 12))
    app.extraction_files_box.configure(state="disabled")

    ctk.CTkLabel(
        left,
        text="Destino da qualificação",
        font=(FONT_FAMILY, 11, "bold"),
        text_color=TEXT_PRIMARY,
    ).pack(anchor="w", padx=14, pady=(0, 4))
    ctk.CTkComboBox(
        left,
        variable=app.extraction_target,
        values=TARGET_OPTIONS,
        corner_radius=12,
        border_width=1,
        border_color=BORDER,
        fg_color=SURFACE_INPUT,
        text_color=TEXT_PRIMARY,
        button_color=ACCENT,
        button_hover_color=ACCENT_HOVER,
        dropdown_fg_color=SURFACE_SUBTLE,
        dropdown_text_color=TEXT_PRIMARY,
        font=(FONT_FAMILY, 11),
        height=36,
    ).pack(fill="x", padx=14, pady=(0, 10))

    ctk.CTkLabel(
        left,
        text="Tratamento a aplicar",
        font=(FONT_FAMILY, 11, "bold"),
        text_color=TEXT_PRIMARY,
    ).pack(anchor="w", padx=14, pady=(0, 4))
    ctk.CTkComboBox(
        left,
        variable=app.extraction_treatment,
        values=TREATMENT_OPTIONS,
        corner_radius=12,
        border_width=1,
        border_color=BORDER,
        fg_color=SURFACE_INPUT,
        text_color=TEXT_PRIMARY,
        button_color=ACCENT,
        button_hover_color=ACCENT_HOVER,
        dropdown_fg_color=SURFACE_SUBTLE,
        dropdown_text_color=TEXT_PRIMARY,
        font=(FONT_FAMILY, 11),
        height=36,
    ).pack(fill="x", padx=14, pady=(0, 10))

    ctk.CTkCheckBox(
        left,
        text="Gerar texto automaticamente após aplicar",
        variable=app.extraction_auto_generate,
        fg_color=ACCENT,
        hover_color=ACCENT_HOVER,
        border_width=1,
        border_color=BORDER,
        checkmark_color=TEXT_PRIMARY,
        text_color=TEXT_PRIMARY,
        font=(FONT_FAMILY, 11),
    ).pack(anchor="w", padx=14, pady=(0, 12))

    ctk.CTkButton(
        left,
        text="Extrair Informações",
        command=app.handlers.on_extraction_run,
        fg_color=ACCENT,
        hover_color=ACCENT_HOVER,
        text_color=TEXT_PRIMARY,
        font=(FONT_FAMILY, 11, "bold"),
        corner_radius=12,
        border_width=1,
        border_color=BORDER,
        height=36,
    ).pack(fill="x", padx=14, pady=(0, 6))

    ctk.CTkButton(
        left,
        text="Aplicar na Qualificação",
        command=app.handlers.on_extraction_apply,
        fg_color="#2a3750",
        hover_color="#334262",
        text_color=TEXT_PRIMARY,
        font=(FONT_FAMILY, 11, "bold"),
        corner_radius=12,
        border_width=1,
        border_color=BORDER,
        height=36,
    ).pack(fill="x", padx=14, pady=(0, 14))

    ctk.CTkLabel(
        right,
        text="Campos Detectados",
        font=(FONT_FAMILY, 13, "bold"),
        text_color=TEXT_PRIMARY,
    ).pack(anchor="w", padx=12, pady=(12, 6))

    app.extraction_result_box = ctk.CTkTextbox(
        right,
        height=220,
        corner_radius=12,
        fg_color=SURFACE_INPUT,
        border_width=1,
        border_color=BORDER,
        text_color=TEXT_PRIMARY,
        font=(FONT_FAMILY, 10),
        wrap="word",
    )
    app.extraction_result_box.pack(fill="x", padx=12, pady=(0, 10))
    app.extraction_result_box.configure(state="disabled")

    ctk.CTkLabel(
        right,
        text="Texto Extraído",
        font=(FONT_FAMILY, 13, "bold"),
        text_color=TEXT_PRIMARY,
    ).pack(anchor="w", padx=12, pady=(0, 6))

    app.extraction_raw_box = ctk.CTkTextbox(
        right,
        corner_radius=12,
        fg_color=SURFACE_INPUT,
        border_width=1,
        border_color=BORDER,
        text_color=TEXT_PRIMARY,
        font=(FONT_FAMILY, 10),
        wrap="word",
    )
    app.extraction_raw_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    app.extraction_raw_box.configure(state="disabled")
