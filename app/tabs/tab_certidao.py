"""Aba Certidão reutilizando builders compartilhados."""

import tkinter as tk

import customtkinter as ctk

try:
    from ..constants import ORGAO_RG_CODES
    from ..ui_builders.forms import UF_BR_VALUES
    from ..ui_builders.theme import (
        ACCENT,
        ACCENT_HOVER,
        BORDER,
        FONT_FAMILY,
        SURFACE_CARD,
        SURFACE_SUBTLE,
        TEXT_PRIMARY,
    )
except ImportError:
    from constants import ORGAO_RG_CODES  # type: ignore
    from ui_builders.forms import UF_BR_VALUES  # type: ignore
    from ui_builders.theme import (  # type: ignore
        ACCENT,
        ACCENT_HOVER,
        BORDER,
        FONT_FAMILY,
        SURFACE_CARD,
        SURFACE_SUBTLE,
        TEXT_PRIMARY,
    )


def build_tab_certidao(
    notebook: ctk.CTkTabview, tab_certidao: ctk.CTkFrame, app
) -> None:
    container = ctk.CTkFrame(tab_certidao, corner_radius=16, fg_color=SURFACE_CARD)
    container.pack(fill="both", expand=True, padx=10, pady=5)

    # Scroll para acomodar todos os campos
    scroll_container = ctk.CTkScrollableFrame(
        container, corner_radius=16, fg_color=SURFACE_SUBTLE
    )
    scroll_container.pack(side="left", fill="both", expand=True)

    right = ctk.CTkFrame(
        container, corner_radius=16, fg_color=SURFACE_SUBTLE, border_width=1, border_color=BORDER
    )
    right.pack(side="left", fill="both", expand=True, padx=(10, 0))

    _build_certidao_form(scroll_container, app)

    commands = {
        "generate": app.handlers.on_generate_cert,
        "copy": app.handlers.on_copy_cert,
        "save": app.handlers.on_save_cert,
        "clear": app.handlers.on_clear_cert,
        "exit": app.handlers.on_exit,
    }
    app.preview_builder.build(right, "preview3", commands)


_CERTIDAO_FIELDS = (
    {
        "type": "combo",
        "label": "Tratamento",
        "key": "tratamento",
        "values": ["Sr.", "Sra.", "Dr.", "Dra."],
    },
    {
        "type": "entry",
        "label": "Nome completo",
        "key": "nome",
        "width": 320,
        "expand": True,
    },
    {
        "type": "combo",
        "label": "Nacionalidade",
        "key": "nacionalidade",
        "values": ["brasileira", "brasileiro"],
    },
    {
        "type": "combo",
        "label": "Estado civil",
        "key": "estado_civil",
        "values": [
            "solteira",
            "solteiro",
            "casada",
            "casado",
            "divorciada",
            "divorciado",
            "viúva",
            "viúvo",
        ],
    },
    {
        "type": "entry",
        "label": "Naturalidade (Cidade-UF)",
        "key": "naturalidade",
        "expand": True,
    },
    {
        "type": "entry",
        "label": "Data de nascimento",
        "key": "data_nascimento",
        "width": 200,
    },
    {"type": "entry", "label": "Nome do pai", "key": "nome_pai", "expand": True},
    {"type": "entry", "label": "Nome da mãe", "key": "nome_mae", "expand": True},
    {"type": "entry", "label": "RG (número)", "key": "rg", "width": 200},
    {"type": "combo", "label": "Órgão RG", "key": "orgao_rg", "values": ORGAO_RG_CODES},
    {"type": "combo", "label": "UF RG", "key": "uf_rg", "values": UF_BR_VALUES},
    {"type": "entry", "label": "CPF", "key": "cpf", "width": 220},
    {
        "type": "checkbox",
        "label": "CPF é o número da CIN (novo RG)",
        "key": "cpf_igual_rg",
    },
    {"type": "entry", "label": "Profissão", "key": "profissao", "expand": True},
)


_CERTIDAO_EXTRA_FIELDS = (
    {"type": "separator"},
    {
        "type": "entry",
        "label": "Matrícula certidão",
        "key": "cert_matricula",
        "expand": True,
    },
    {
        "type": "entry",
        "label": "Data certidão (dd/mm/aaaa)",
        "key": "cert_data",
        "width": 220,
    },
    {"type": "entry", "label": "Logradouro", "key": "logradouro", "expand": True},
    {"type": "entry", "label": "Número", "key": "numero", "width": 120},
    {"type": "entry", "label": "Bairro", "key": "bairro", "expand": True},
    {"type": "entry", "label": "Cidade", "key": "cidade", "expand": True},
    {"type": "entry", "label": "CEP", "key": "cep", "width": 160},
    {"type": "entry", "label": "E-mail", "key": "email", "expand": True},
)


def _build_certidao_form(parent: ctk.CTkScrollableFrame, app) -> None:
    """Formulário para dados da certidão"""
    row = 0

    # Switch CNH
    switch_frame = ctk.CTkFrame(
        parent, corner_radius=16, fg_color=SURFACE_CARD, border_width=1, border_color=BORDER
    )
    switch_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=5)
    ctk.CTkSwitch(
        master=switch_frame,
        text="Usar CNH",
        variable=app.cnh_enabled_certidao,
        command=lambda: _toggle_cnh_certidao_and_generate(app),
        font=(FONT_FAMILY, 11, "bold"),
        text_color=TEXT_PRIMARY,
        progress_color=ACCENT,
        button_color=ACCENT,
        button_hover_color=ACCENT_HOVER,
        corner_radius=16,
    ).pack(anchor="w", padx=10, pady=8)
    row += 1

    # Dados pessoais básicos
    row = app.form_builder.build_from_definition(
        parent, _CERTIDAO_FIELDS, start_row=row
    )

    # Campos CNH (criar e armazenar widgets)
    app.cnh_certidao_widgets = []

    # Criar campos CNH manualmente para controlar visibilidade
    try:
        from ..ui_builders.components import ComboFactory, EntryFactory, LabelFactory
    except ImportError:
        from ui_builders.components import (  # type: ignore
            ComboFactory,
            EntryFactory,
            LabelFactory,
        )

    labels = LabelFactory()
    combos = ComboFactory()
    entries = EntryFactory()

    cnh_uf_label = labels.create(parent, "CNH UF")
    cnh_uf_combo = combos.create(
        parent, variable=app.vars["cnh_uf"], values=UF_BR_VALUES, width=100
    )
    app.cnh_certidao_widgets.append(
        (cnh_uf_label, row, 0, {"sticky": "w", "padx": (15, 6), "pady": 2})
    )
    app.cnh_certidao_widgets.append(
        (cnh_uf_combo, row, 1, {"sticky": "w", "pady": 2, "padx": (0, 15)})
    )
    row += 1

    cnh_numero_label = labels.create(parent, "CNH Número")
    cnh_numero_entry = entries.create(
        parent, textvariable=app.vars["cnh_numero"], width=200
    )
    app.cnh_certidao_widgets.append(
        (cnh_numero_label, row, 0, {"sticky": "w", "padx": (15, 6), "pady": 2})
    )
    app.cnh_certidao_widgets.append(
        (cnh_numero_entry, row, 1, {"sticky": "ew", "pady": 2, "padx": (0, 15)})
    )
    row += 1

    cnh_data_label = labels.create(parent, "CNH Data de expedição")
    cnh_data_entry = entries.create(
        parent,
        textvariable=app.vars["cnh_data_expedicao"],
        width=200,
        field_type="date",
    )
    app.cnh_certidao_widgets.append(
        (cnh_data_label, row, 0, {"sticky": "w", "padx": (15, 6), "pady": 2})
    )
    app.cnh_certidao_widgets.append(
        (cnh_data_entry, row, 1, {"sticky": "ew", "pady": 2, "padx": (0, 15)})
    )
    row += 1

    # Ocultar campos CNH inicialmente
    for widget, _, _, _ in app.cnh_certidao_widgets:
        widget.grid_remove()

    # Separador
    ctk.CTkFrame(parent, height=2, fg_color=BORDER).grid(
        row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=10
    )
    row += 1

    # Campos específicos da certidão
    for field in _CERTIDAO_EXTRA_FIELDS:
        if field["type"] == "separator":
            ctk.CTkFrame(parent, height=2, fg_color=BORDER).grid(
                row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=10
            )
            row += 1
            continue
        row = app.form_builder.build_from_definition(parent, [field], start_row=row)

    parent.grid_columnconfigure(1, weight=1)


def _toggle_cnh_certidao(app):
    """Mostra ou oculta campos CNH na aba certidão"""
    if app.cnh_enabled_certidao.get():
        for widget, r, c, opts in app.cnh_certidao_widgets:
            widget.grid(row=r, column=c, **opts)
    else:
        for widget, _, _, _ in app.cnh_certidao_widgets:
            widget.grid_remove()


def _toggle_cnh_certidao_and_generate(app):
    """Toggle CNH e gera texto automaticamente se houver dados"""
    _toggle_cnh_certidao(app)
    # Gerar automaticamente se houver dados
    if app.vars.get("nome", tk.StringVar()).get():
        app.handlers.on_generate_cert()
