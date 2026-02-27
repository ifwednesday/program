"""Aba Empresa com formulário para dados da empresa e representante."""

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


def build_tab_empresa(notebook: ctk.CTkTabview, tab_empresa: ctk.CTkFrame, app) -> None:
    container = ctk.CTkFrame(tab_empresa, corner_radius=16, fg_color=SURFACE_CARD)
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

    _build_empresa_form(scroll_container, app)

    commands = {
        "generate": app.handlers.on_generate_empresa,
        "copy": app.handlers.on_copy_empresa,
        "save": app.handlers.on_save_empresa,
        "clear": app.handlers.on_clear_empresa,
        "exit": app.handlers.on_exit,
    }
    app.preview_builder.build(right, "preview_empresa", commands)


def _build_empresa_form(parent: ctk.CTkScrollableFrame, app) -> None:
    """Formulário para dados da empresa e representante"""
    row = 0

    # Dados da empresa
    empresa_label = ctk.CTkLabel(
        parent,
        text="DADOS DA EMPRESA",
        font=(FONT_FAMILY, 14, "bold"),
        text_color=TEXT_PRIMARY,
    )
    empresa_label.grid(
        row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 5)
    )
    row += 1

    row = app.form_builder.build_from_definition(parent, _EMPRESA_FIELDS, start_row=row)

    # Separador
    ctk.CTkFrame(parent, height=3, fg_color=BORDER).grid(
        row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=15
    )
    row += 1

    # Dados do representante
    representante_label = ctk.CTkLabel(
        parent,
        text="DADOS DO REPRESENTANTE",
        font=(FONT_FAMILY, 14, "bold"),
        text_color=TEXT_PRIMARY,
    )
    representante_label.grid(
        row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 5)
    )
    row += 1

    row = app.form_builder.build_from_definition(
        parent, _REPRESENTANTE_FIELDS, start_row=row
    )

    # Separador
    ctk.CTkFrame(parent, height=3, fg_color=BORDER).grid(
        row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=15
    )
    row += 1

    # Dados pessoais do representante
    pessoal_label = ctk.CTkLabel(
        parent,
        text="DADOS PESSOAIS DO REPRESENTANTE",
        font=(FONT_FAMILY, 14, "bold"),
        text_color=TEXT_PRIMARY,
    )
    pessoal_label.grid(
        row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 5)
    )
    row += 1

    # Switch CNH
    switch_frame = ctk.CTkFrame(
        parent, corner_radius=16, fg_color=SURFACE_CARD, border_width=1, border_color=BORDER
    )
    switch_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=5)
    ctk.CTkSwitch(
        master=switch_frame,
        text="Usar CNH",
        variable=app.cnh_enabled_empresa,
        command=lambda: _toggle_cnh_empresa_and_generate(app),
        font=(FONT_FAMILY, 11, "bold"),
        text_color=TEXT_PRIMARY,
        progress_color=ACCENT,
        button_color=ACCENT,
        button_hover_color=ACCENT_HOVER,
        corner_radius=16,
    ).pack(anchor="w", padx=10, pady=8)
    row += 1

    # Campos pessoais sem CNH primeiro
    row = app.form_builder.build_from_definition(
        parent, _PESSOAIS_FIELDS_SEM_CNH, start_row=row
    )

    # Campos CNH (criar e armazenar widgets)
    app.cnh_empresa_widgets = []

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
    app.cnh_empresa_widgets.append(
        (cnh_uf_label, row, 0, {"sticky": "w", "padx": (15, 6), "pady": 2})
    )
    app.cnh_empresa_widgets.append(
        (cnh_uf_combo, row, 1, {"sticky": "w", "pady": 2, "padx": (0, 15)})
    )
    row += 1

    cnh_numero_label = labels.create(parent, "CNH Número")
    cnh_numero_entry = entries.create(
        parent, textvariable=app.vars["cnh_numero"], width=200
    )
    app.cnh_empresa_widgets.append(
        (cnh_numero_label, row, 0, {"sticky": "w", "padx": (15, 6), "pady": 2})
    )
    app.cnh_empresa_widgets.append(
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
    app.cnh_empresa_widgets.append(
        (cnh_data_label, row, 0, {"sticky": "w", "padx": (15, 6), "pady": 2})
    )
    app.cnh_empresa_widgets.append(
        (cnh_data_entry, row, 1, {"sticky": "ew", "pady": 2, "padx": (0, 15)})
    )
    row += 1

    # Campos restantes (RG, CPF, etc)
    row = app.form_builder.build_from_definition(
        parent, _PESSOAIS_FIELDS_RESTANTES, start_row=row
    )

    # Mostrar campos CNH inicialmente (default True porque template atual usa CNH)
    # Verificar se o switch está ativado para mostrar/ocultar campos
    if app.cnh_enabled_empresa.get():
        for widget, r, c, opts in app.cnh_empresa_widgets:
            widget.grid(row=r, column=c, **opts)
    else:
        for widget, _, _, _ in app.cnh_empresa_widgets:
            widget.grid_remove()

    # Separador
    ctk.CTkFrame(parent, height=3, fg_color=BORDER).grid(
        row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=15
    )
    row += 1

    # Endereço pessoal do representante
    endereco_label = ctk.CTkLabel(
        parent,
        text="ENDEREÇO PESSOAL DO REPRESENTANTE",
        font=(FONT_FAMILY, 14, "bold"),
        text_color=TEXT_PRIMARY,
    )
    endereco_label.grid(
        row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 5)
    )
    row += 1

    row = app.form_builder.build_from_definition(
        parent, _ENDERECO_PESSOAL_FIELDS, start_row=row
    )

    parent.grid_columnconfigure(1, weight=1)


def _toggle_cnh_empresa(app):
    """Mostra ou oculta campos CNH na aba empresa"""
    if app.cnh_enabled_empresa.get():
        for widget, r, c, opts in app.cnh_empresa_widgets:
            widget.grid(row=r, column=c, **opts)
    else:
        for widget, _, _, _ in app.cnh_empresa_widgets:
            widget.grid_remove()


def _toggle_cnh_empresa_and_generate(app):
    """Toggle CNH e gera texto automaticamente se houver dados"""
    _toggle_cnh_empresa(app)
    # Gerar automaticamente se houver dados
    if app.vars.get("nome_representante", tk.StringVar()).get():
        app.handlers.on_generate_empresa()


_EMPRESA_FIELDS = (
    {"type": "entry", "label": "Razão Social", "key": "razao_social", "expand": True},
    {"type": "entry", "label": "CNPJ", "key": "cnpj", "width": 200},
    {
        "type": "combo",
        "label": "Junta Comercial",
        "key": "junta_comercial",
        "values": [
            "JUCEMAT",
            "JUCESP",
            "JUCERGS",
            "JUCEMG",
            "JUCERJ",
            "JUCECE",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
            "JUCEMT",
        ],
    },
    {"type": "entry", "label": "NIRE", "key": "nire", "width": 200},
    {
        "type": "entry",
        "label": "Logradouro",
        "key": "logradouro",
        "expand": True,
    },
    {"type": "entry", "label": "Número", "key": "numero", "width": 120},
    {"type": "entry", "label": "Quadra", "key": "quadra_empresa", "width": 120},
    {"type": "entry", "label": "Lote", "key": "lote_empresa", "width": 120},
    {"type": "entry", "label": "Bairro", "key": "bairro", "expand": True},
    {"type": "entry", "label": "Cidade", "key": "cidade", "expand": True},
    {"type": "entry", "label": "CEP", "key": "cep", "width": 160},
    {
        "type": "entry",
        "label": "E-mail da empresa",
        "key": "email_empresa",
        "expand": True,
    },
    {
        "type": "entry",
        "label": "Número da alteração",
        "key": "numero_alteracao",
        "width": 120,
    },
    {
        "type": "entry",
        "label": "Número do registro",
        "key": "numero_registro",
        "width": 200,
    },
    {
        "type": "entry",
        "label": "Data do registro",
        "key": "data_registro",
        "width": 160,
    },
    {
        "type": "combo",
        "label": "UF da Junta",
        "key": "uf_junta",
        "values": UF_BR_VALUES,
    },
    {"type": "entry", "label": "Protocolo", "key": "protocolo", "width": 200},
    {
        "type": "entry",
        "label": "Data da certidão",
        "key": "data_certidao",
        "width": 160,
    },
    {
        "type": "entry",
        "label": "Autenticação eletrônica",
        "key": "autenticacao_eletronica",
        "expand": True,
    },
)

_REPRESENTANTE_FIELDS = (
    {
        "type": "combo",
        "label": "Cargo do representante",
        "key": "cargo_representante",
        "values": [
            "sócia administradora",
            "sócio administrador",
            "sócia",
            "sócio",
            "diretor",
            "diretora",
            "presidente",
            "vice-presidente",
            "gerente",
            "procurador",
            "procuradora",
        ],
    },
    {
        "type": "combo",
        "label": "Tratamento",
        "key": "tratamento",
        "values": ["Sr.", "Sra.", "Dr.", "Dra."],
    },
    {
        "type": "entry",
        "label": "Nome completo",
        "key": "nome_representante",
        "width": 320,
        "expand": True,
    },
    {
        "type": "combo",
        "label": "Nacionalidade",
        "key": "nacionalidade_empresa",
        "values": ["brasileira", "brasileiro"],
    },
    {
        "type": "combo",
        "label": "Estado civil",
        "key": "estado_civil_empresa",
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
)

_PESSOAIS_FIELDS_SEM_CNH = (
    {"type": "entry", "label": "Naturalidade", "key": "naturalidade", "expand": True},
    {
        "type": "entry",
        "label": "Data de nascimento",
        "key": "data_nascimento",
        "width": 160,
    },
    {"type": "entry", "label": "Nome do pai", "key": "nome_pai", "expand": True},
    {"type": "entry", "label": "Nome da mãe", "key": "nome_mae", "expand": True},
)

_PESSOAIS_FIELDS_RESTANTES = (
    {"type": "entry", "label": "RG", "key": "rg", "width": 200},
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

_ENDERECO_PESSOAL_FIELDS = (
    {
        "type": "entry",
        "label": "Endereço pessoal",
        "key": "endereco_pessoal",
        "expand": True,
    },
    {
        "type": "entry",
        "label": "E-mail pessoal",
        "key": "email_pessoal",
        "expand": True,
    },
)
