"""Aba Casados com formulário para casal."""

import tkinter as tk

import customtkinter as ctk

try:
    from ..constants import ORGAO_RG_CODES
    from ..ui_builders.forms import UF_BR_VALUES
except ImportError:
    from constants import ORGAO_RG_CODES  # type: ignore
    from ui_builders.forms import UF_BR_VALUES  # type: ignore


def build_tab_casados(notebook: ctk.CTkTabview, tab_casados: ctk.CTkFrame, app) -> None:
    container = ctk.CTkFrame(tab_casados, corner_radius=12, fg_color="#2d2d2d")
    container.pack(fill="both", expand=True, padx=10, pady=5)

    # Scroll para acomodar todos os campos
    scroll_container = ctk.CTkScrollableFrame(
        container, corner_radius=8, fg_color="#3a3a3a"
    )
    scroll_container.pack(side="left", fill="both", expand=True)

    right = ctk.CTkFrame(container, corner_radius=8, fg_color="#3a3a3a")
    right.pack(side="left", fill="both", expand=True, padx=(10, 0))

    _build_casados_form(scroll_container, app)

    commands = {
        "generate": app.handlers.on_generate_casados,
        "copy": app.handlers.on_copy_casados,
        "save": app.handlers.on_save_casados,
        "clear": app.handlers.on_clear_casados,
        "exit": app.handlers.on_exit,
    }
    app.preview_builder.build(right, "preview_casados", commands)


def _build_casados_form(parent: ctk.CTkScrollableFrame, app) -> None:
    """Formulário para casal com campos duplicados"""
    row = 0

    # Switch CNH Pessoa 1
    switch_frame1 = ctk.CTkFrame(parent, corner_radius=8, fg_color="#2d2d2d")
    switch_frame1.grid(row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=5)
    ctk.CTkSwitch(
        master=switch_frame1,
        text="Usar CNH Pessoa 1",
        variable=app.cnh_enabled1,
        command=lambda: _toggle_cnh_pessoa1_and_generate(app),
        font=("Segoe UI", 11, "bold"),
        text_color="#ffffff",
        progress_color="#1f6aa5",
        button_color="#1f6aa5",
        button_hover_color="#1a5a8a",
        corner_radius=8,
    ).pack(anchor="w", padx=10, pady=8)
    row += 1

    # Pessoa 1
    row = app.form_builder.build_from_definition(
        parent, _PESSOA1_FIELDS_BASE, start_row=row
    )

    # Campos CNH Pessoa 1 (criar e armazenar widgets)
    app.cnh1_widgets = []

    # Criar campos CNH1 manualmente para controlar visibilidade
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

    cnh_uf1_label = labels.create(parent, "CNH UF Pessoa 1")
    cnh_uf1_combo = combos.create(
        parent, variable=app.vars["cnh_uf1"], values=UF_BR_VALUES, width=100
    )
    app.cnh1_widgets.append(
        (cnh_uf1_label, row, 0, {"sticky": "w", "padx": (15, 6), "pady": 2})
    )
    app.cnh1_widgets.append(
        (cnh_uf1_combo, row, 1, {"sticky": "w", "pady": 2, "padx": (0, 15)})
    )
    row += 1

    cnh_numero1_label = labels.create(parent, "CNH Número Pessoa 1")
    cnh_numero1_entry = entries.create(
        parent, textvariable=app.vars["cnh_numero1"], width=200
    )
    app.cnh1_widgets.append(
        (cnh_numero1_label, row, 0, {"sticky": "w", "padx": (15, 6), "pady": 2})
    )
    app.cnh1_widgets.append(
        (cnh_numero1_entry, row, 1, {"sticky": "ew", "pady": 2, "padx": (0, 15)})
    )
    row += 1

    cnh_data1_label = labels.create(parent, "CNH Data Pessoa 1")
    cnh_data1_entry = entries.create(
        parent,
        textvariable=app.vars["cnh_data_expedicao1"],
        width=200,
        field_type="date",
    )
    app.cnh1_widgets.append(
        (cnh_data1_label, row, 0, {"sticky": "w", "padx": (15, 6), "pady": 2})
    )
    app.cnh1_widgets.append(
        (cnh_data1_entry, row, 1, {"sticky": "ew", "pady": 2, "padx": (0, 15)})
    )
    row += 1

    # Ocultar campos CNH1 inicialmente
    for widget, _, _, _ in app.cnh1_widgets:
        widget.grid_remove()

    # Switch CNH Pessoa 2
    switch_frame2 = ctk.CTkFrame(parent, corner_radius=8, fg_color="#2d2d2d")
    switch_frame2.grid(row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=5)
    ctk.CTkSwitch(
        master=switch_frame2,
        text="Usar CNH Pessoa 2",
        variable=app.cnh_enabled2,
        command=lambda: _toggle_cnh_pessoa2_and_generate(app),
        font=("Segoe UI", 11, "bold"),
        text_color="#ffffff",
        progress_color="#1f6aa5",
        button_color="#1f6aa5",
        button_hover_color="#1a5a8a",
        corner_radius=8,
    ).pack(anchor="w", padx=10, pady=8)
    row += 1

    # Pessoa 2
    row = app.form_builder.build_from_definition(
        parent, _PESSOA2_FIELDS_BASE, start_row=row
    )

    # Campos CNH Pessoa 2 (criar e armazenar widgets)
    app.cnh2_widgets = []

    cnh_uf2_label = labels.create(parent, "CNH UF Pessoa 2")
    cnh_uf2_combo = combos.create(
        parent, variable=app.vars["cnh_uf2"], values=UF_BR_VALUES, width=100
    )
    app.cnh2_widgets.append(
        (cnh_uf2_label, row, 0, {"sticky": "w", "padx": (15, 6), "pady": 2})
    )
    app.cnh2_widgets.append(
        (cnh_uf2_combo, row, 1, {"sticky": "w", "pady": 2, "padx": (0, 15)})
    )
    row += 1

    cnh_numero2_label = labels.create(parent, "CNH Número Pessoa 2")
    cnh_numero2_entry = entries.create(
        parent, textvariable=app.vars["cnh_numero2"], width=200
    )
    app.cnh2_widgets.append(
        (cnh_numero2_label, row, 0, {"sticky": "w", "padx": (15, 6), "pady": 2})
    )
    app.cnh2_widgets.append(
        (cnh_numero2_entry, row, 1, {"sticky": "ew", "pady": 2, "padx": (0, 15)})
    )
    row += 1

    cnh_data2_label = labels.create(parent, "CNH Data Pessoa 2")
    cnh_data2_entry = entries.create(
        parent,
        textvariable=app.vars["cnh_data_expedicao2"],
        width=200,
        field_type="date",
    )
    app.cnh2_widgets.append(
        (cnh_data2_label, row, 0, {"sticky": "w", "padx": (15, 6), "pady": 2})
    )
    app.cnh2_widgets.append(
        (cnh_data2_entry, row, 1, {"sticky": "ew", "pady": 2, "padx": (0, 15)})
    )
    row += 1

    # Ocultar campos CNH2 inicialmente
    for widget, _, _, _ in app.cnh2_widgets:
        widget.grid_remove()

    # Dados do casamento e endereço compartilhado
    app.form_builder.build_from_definition(parent, _CASAMENTO_FIELDS, start_row=row)
    parent.grid_columnconfigure(1, weight=1)


def _toggle_cnh_pessoa1(app):
    if app.cnh_enabled1.get():
        for widget, r, c, opts in app.cnh1_widgets:
            widget.grid(row=r, column=c, **opts)
    else:
        for widget, _, _, _ in app.cnh1_widgets:
            widget.grid_remove()


def _toggle_cnh_pessoa2(app):
    if app.cnh_enabled2.get():
        for widget, r, c, opts in app.cnh2_widgets:
            widget.grid(row=r, column=c, **opts)
    else:
        for widget, _, _, _ in app.cnh2_widgets:
            widget.grid_remove()


def _toggle_cnh_pessoa1_and_generate(app):
    _toggle_cnh_pessoa1(app)
    # Gerar automaticamente se houver dados
    if app.vars.get("nome1", tk.StringVar()).get():
        app.handlers.on_generate_casados()


def _toggle_cnh_pessoa2_and_generate(app):
    _toggle_cnh_pessoa2(app)
    # Gerar automaticamente se houver dados
    if app.vars.get("nome2", tk.StringVar()).get():
        app.handlers.on_generate_casados()


_PESSOA1_FIELDS_BASE = (
    {
        "type": "combo",
        "label": "Tratamento Pessoa 1",
        "key": "tratamento1",
        "values": ["Sr.", "Sra."],
    },
    {
        "type": "entry",
        "label": "Nome completo Pessoa 1",
        "key": "nome1",
        "width": 320,
        "expand": True,
    },
    {"type": "checkbox", "label": "Nome em MAIÚSCULAS Pessoa 1", "key": "nome_caps1"},
    {
        "type": "combo",
        "label": "Gênero Pessoa 1",
        "key": "genero_terminacao1",
        "values": ["o", "a"],
    },
    {
        "type": "entry",
        "label": "Naturalidade Pessoa 1",
        "key": "naturalidade1",
        "expand": True,
    },
    {
        "type": "entry",
        "label": "Data nascimento Pessoa 1",
        "key": "data_nascimento1",
        "width": 200,
    },
    {
        "type": "entry",
        "label": "Nome do pai Pessoa 1",
        "key": "nome_pai1",
        "expand": True,
    },
    {
        "type": "entry",
        "label": "Nome da mãe Pessoa 1",
        "key": "nome_mae1",
        "expand": True,
    },
    {"type": "entry", "label": "RG Pessoa 1", "key": "rg1", "width": 200},
    {
        "type": "combo",
        "label": "Órgão RG Pessoa 1",
        "key": "orgao_rg1",
        "values": ORGAO_RG_CODES,
    },
    {
        "type": "combo",
        "label": "UF RG Pessoa 1",
        "key": "uf_rg1",
        "values": UF_BR_VALUES,
    },
    {"type": "entry", "label": "CPF Pessoa 1", "key": "cpf1", "width": 220},
    {
        "type": "entry",
        "label": "Profissão Pessoa 1",
        "key": "profissao1",
        "expand": True,
    },
    {"type": "entry", "label": "E-mail Pessoa 1", "key": "email1", "expand": True},
)

_PESSOA2_FIELDS_BASE = (
    {
        "type": "combo",
        "label": "Tratamento Pessoa 2",
        "key": "tratamento2",
        "values": ["Sr.", "Sra."],
    },
    {
        "type": "entry",
        "label": "Nome completo Pessoa 2",
        "key": "nome2",
        "width": 320,
        "expand": True,
    },
    {"type": "checkbox", "label": "Nome em MAIÚSCULAS Pessoa 2", "key": "nome_caps2"},
    {
        "type": "combo",
        "label": "Gênero Pessoa 2",
        "key": "genero_terminacao2",
        "values": ["o", "a"],
    },
    {
        "type": "entry",
        "label": "Naturalidade Pessoa 2",
        "key": "naturalidade2",
        "expand": True,
    },
    {
        "type": "entry",
        "label": "Data nascimento Pessoa 2",
        "key": "data_nascimento2",
        "width": 200,
    },
    {
        "type": "entry",
        "label": "Nome do pai Pessoa 2",
        "key": "nome_pai2",
        "expand": True,
    },
    {
        "type": "entry",
        "label": "Nome da mãe Pessoa 2",
        "key": "nome_mae2",
        "expand": True,
    },
    {"type": "entry", "label": "RG Pessoa 2", "key": "rg2", "width": 200},
    {
        "type": "combo",
        "label": "Órgão RG Pessoa 2",
        "key": "orgao_rg2",
        "values": ORGAO_RG_CODES,
    },
    {
        "type": "combo",
        "label": "UF RG Pessoa 2",
        "key": "uf_rg2",
        "values": UF_BR_VALUES,
    },
    {"type": "entry", "label": "CPF Pessoa 2", "key": "cpf2", "width": 220},
    {
        "type": "entry",
        "label": "Profissão Pessoa 2",
        "key": "profissao2",
        "expand": True,
    },
    {"type": "entry", "label": "E-mail Pessoa 2", "key": "email2", "expand": True},
)

_CASAMENTO_FIELDS = (
    {
        "type": "combo",
        "label": "Regime de casamento",
        "key": "regime_casamento",
        "values": [
            "comunhão parcial de bens",
            "comunhão universal de bens",
            "separação total de bens",
            "participação final nos aquestos",
        ],
    },
    {
        "type": "entry",
        "label": "Matrícula certidão casamento",
        "key": "cert_casamento_matricula",
        "expand": True,
    },
    {
        "type": "entry",
        "label": "Logradouro",
        "key": "logradouro_casados",
        "expand": True,
    },
    {"type": "entry", "label": "Número", "key": "numero_casados", "width": 120},
    {"type": "entry", "label": "Bairro", "key": "bairro_casados", "expand": True},
    {"type": "entry", "label": "Cidade", "key": "cidade_casados", "expand": True},
    {"type": "entry", "label": "CEP", "key": "cep_casados", "width": 160},
)
