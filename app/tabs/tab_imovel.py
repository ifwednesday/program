"""Aba Imóveis com formulário para dados do imóvel."""

import customtkinter as ctk


def build_tab_imovel(notebook: ctk.CTkTabview, tab_imovel: ctk.CTkFrame, app) -> None:
    container = ctk.CTkFrame(tab_imovel, corner_radius=16, fg_color="#2d2d2d")
    container.pack(fill="both", expand=True, padx=10, pady=5)

    # Scroll para acomodar todos os campos
    scroll_container = ctk.CTkScrollableFrame(
        container, corner_radius=16, fg_color="#3a3a3a"
    )
    scroll_container.pack(side="left", fill="both", expand=True)

    right = ctk.CTkFrame(container, corner_radius=16, fg_color="#3a3a3a")
    right.pack(side="left", fill="both", expand=True, padx=(10, 0))

    _build_imovel_form(scroll_container, app)

    commands = {
        "generate": app.handlers.on_generate_imovel,
        "copy": app.handlers.on_copy_imovel,
        "save": app.handlers.on_save_imovel,
        "clear": app.handlers.on_clear_imovel,
        "exit": app.handlers.on_exit,
    }
    app.preview_builder.build(right, "preview_imovel", commands)


def _build_imovel_form(parent: ctk.CTkScrollableFrame, app) -> None:
    """Formulário para dados do imóvel"""
    row = 0

    # Dados básicos do imóvel
    imovel_label = ctk.CTkLabel(
        parent,
        text="DADOS DO IMÓVEL",
        font=("Segoe UI", 14, "bold"),
        text_color="#1f6aa5",
    )
    imovel_label.grid(
        row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 5)
    )
    row += 1

    row = app.form_builder.build_from_definition(parent, _IMOVEL_FIELDS, start_row=row)

    # Separador
    ctk.CTkFrame(parent, height=3, fg_color="#1f6aa5").grid(
        row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=15
    )
    row += 1

    # Localização
    localizacao_label = ctk.CTkLabel(
        parent, text="LOCALIZAÇÃO", font=("Segoe UI", 14, "bold"), text_color="#1f6aa5"
    )
    localizacao_label.grid(
        row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 5)
    )
    row += 1

    row = app.form_builder.build_from_definition(
        parent, _LOCALIZACAO_FIELDS, start_row=row
    )

    # Separador
    ctk.CTkFrame(parent, height=3, fg_color="#1f6aa5").grid(
        row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=15
    )
    row += 1

    # Área e medidas
    area_label = ctk.CTkLabel(
        parent,
        text="ÁREA E MEDIDAS",
        font=("Segoe UI", 14, "bold"),
        text_color="#1f6aa5",
    )
    area_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 5))
    row += 1

    row = app.form_builder.build_from_definition(parent, _AREA_FIELDS, start_row=row)

    # Separador
    ctk.CTkFrame(parent, height=3, fg_color="#1f6aa5").grid(
        row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=15
    )
    row += 1

    # Lote e quadra
    lote_label = ctk.CTkLabel(
        parent,
        text="LOTE E QUADRA",
        font=("Segoe UI", 14, "bold"),
        text_color="#1f6aa5",
    )
    lote_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 5))
    row += 1

    row = app.form_builder.build_from_definition(parent, _LOTE_FIELDS, start_row=row)

    parent.grid_columnconfigure(1, weight=1)


_IMOVEL_FIELDS = (
    {
        "type": "combo",
        "label": "Quantidade",
        "key": "quantidade_imovel",
        "values": ["Um (01)", "Dois (02)", "Três (03)", "Quatro (04)", "Cinco (05)"],
        "width": 120,
    },
    {
        "type": "combo",
        "label": "Tipo do imóvel",
        "key": "tipo_imovel",
        "values": [
            "lote de terras",
            "casa residencial",
            "apartamento",
            "terreno",
            "sala comercial",
            "galpão",
            "sobrado",
            "chácara",
            "sítio",
            "fazenda",
        ],
        "expand": True,
    },
    {
        "type": "combo",
        "label": "Zona",
        "key": "zona_imovel",
        "values": [
            "zona urbana",
            "zona rural",
            "zona industrial",
            "zona comercial",
            "zona residencial",
        ],
        "width": 150,
    },
    {"type": "entry", "label": "Cidade", "key": "cidade_imovel", "expand": True},
    {
        "type": "combo",
        "label": "Estado",
        "key": "estado_imovel",
        "values": [
            "Acre",
            "Alagoas",
            "Amapá",
            "Amazonas",
            "Bahia",
            "Ceará",
            "Distrito Federal",
            "Espírito Santo",
            "Goiás",
            "Maranhão",
            "Mato Grosso",
            "Mato Grosso do Sul",
            "Minas Gerais",
            "Pará",
            "Paraíba",
            "Paraná",
            "Pernambuco",
            "Piauí",
            "Rio de Janeiro",
            "Rio Grande do Norte",
            "Rio Grande do Sul",
            "Rondônia",
            "Roraima",
            "Santa Catarina",
            "São Paulo",
            "Sergipe",
            "Tocantins",
        ],
        "expand": True,
    },
)

_LOCALIZACAO_FIELDS = (
    {
        "type": "entry",
        "label": "Nome do loteamento",
        "key": "loteamento",
        "expand": True,
    },
)

_AREA_FIELDS = (
    {"type": "entry", "label": "Valor da área", "key": "area_valor", "width": 120},
    {
        "type": "combo",
        "label": "Unidade",
        "key": "area_unidade",
        "values": ["m²", "hectares", "alqueires", "metros quadrados"],
        "width": 120,
    },
    {
        "type": "entry",
        "label": "Área por extenso",
        "key": "area_por_extenso",
        "expand": True,
    },
)

_LOTE_FIELDS = (
    {"type": "entry", "label": "Número do lote", "key": "lote", "width": 120},
    {
        "type": "entry",
        "label": "Lote por extenso",
        "key": "lote_por_extenso",
        "expand": True,
    },
    {"type": "entry", "label": "Número da quadra", "key": "quadra", "width": 120},
    {
        "type": "entry",
        "label": "Quadra por extenso",
        "key": "quadra_por_extenso",
        "expand": True,
    },
)
