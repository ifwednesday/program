"""Aba Empresa com formulário para dados da empresa e representante."""

import customtkinter as ctk

try:
    from ..constants import ORGAO_RG_CODES
    from ..ui_builders.forms import UF_BR_VALUES
except ImportError:
    from constants import ORGAO_RG_CODES  # type: ignore
    from ui_builders.forms import UF_BR_VALUES  # type: ignore


def build_tab_empresa(notebook: ctk.CTkTabview, tab_empresa: ctk.CTkFrame, app) -> None:
    container = ctk.CTkFrame(tab_empresa, corner_radius=12, fg_color="#2d2d2d")
    container.pack(fill="both", expand=True, padx=10, pady=5)

    # Scroll para acomodar todos os campos
    scroll_container = ctk.CTkScrollableFrame(
        container, corner_radius=8, fg_color="#3a3a3a"
    )
    scroll_container.pack(side="left", fill="both", expand=True)

    right = ctk.CTkFrame(container, corner_radius=8, fg_color="#3a3a3a")
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
        font=("Segoe UI", 14, "bold"),
        text_color="#1f6aa5",
    )
    empresa_label.grid(
        row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 5)
    )
    row += 1

    row = app.form_builder.build_from_definition(parent, _EMPRESA_FIELDS, start_row=row)

    # Separador
    ctk.CTkFrame(parent, height=3, fg_color="#1f6aa5").grid(
        row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=15
    )
    row += 1

    # Dados do representante
    representante_label = ctk.CTkLabel(
        parent,
        text="DADOS DO REPRESENTANTE",
        font=("Segoe UI", 14, "bold"),
        text_color="#1f6aa5",
    )
    representante_label.grid(
        row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 5)
    )
    row += 1

    row = app.form_builder.build_from_definition(
        parent, _REPRESENTANTE_FIELDS, start_row=row
    )

    # Separador
    ctk.CTkFrame(parent, height=3, fg_color="#1f6aa5").grid(
        row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=15
    )
    row += 1

    # Dados pessoais do representante
    pessoal_label = ctk.CTkLabel(
        parent,
        text="DADOS PESSOAIS DO REPRESENTANTE",
        font=("Segoe UI", 14, "bold"),
        text_color="#1f6aa5",
    )
    pessoal_label.grid(
        row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 5)
    )
    row += 1

    row = app.form_builder.build_from_definition(
        parent, _PESSOAIS_FIELDS, start_row=row
    )

    # Separador
    ctk.CTkFrame(parent, height=3, fg_color="#1f6aa5").grid(
        row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=15
    )
    row += 1

    # Endereço pessoal do representante
    endereco_label = ctk.CTkLabel(
        parent,
        text="ENDEREÇO PESSOAL DO REPRESENTANTE",
        font=("Segoe UI", 14, "bold"),
        text_color="#1f6aa5",
    )
    endereco_label.grid(
        row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 5)
    )
    row += 1

    row = app.form_builder.build_from_definition(
        parent, _ENDERECO_PESSOAL_FIELDS, start_row=row
    )

    parent.grid_columnconfigure(1, weight=1)


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
        "key": "logradouro_empresa",
        "expand": True,
    },
    {"type": "entry", "label": "Número", "key": "numero_empresa", "width": 120},
    {"type": "entry", "label": "Quadra", "key": "quadra_empresa", "width": 120},
    {"type": "entry", "label": "Lote", "key": "lote_empresa", "width": 120},
    {"type": "entry", "label": "Bairro", "key": "bairro_empresa", "expand": True},
    {"type": "entry", "label": "Cidade", "key": "cidade_empresa", "expand": True},
    {"type": "entry", "label": "CEP", "key": "cep_empresa", "width": 160},
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
        "values": ["Sr.", "Sra."],
    },
    {
        "type": "entry",
        "label": "Nome completo",
        "key": "nome_representante",
        "width": 320,
        "expand": True,
    },
    {"type": "checkbox", "label": "Nome em MAIÚSCULAS", "key": "nome_caps"},
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

_PESSOAIS_FIELDS = (
    {"type": "entry", "label": "Naturalidade", "key": "naturalidade", "expand": True},
    {
        "type": "entry",
        "label": "Data de nascimento",
        "key": "data_nascimento",
        "width": 160,
    },
    {"type": "entry", "label": "Nome do pai", "key": "nome_pai", "expand": True},
    {"type": "entry", "label": "Nome da mãe", "key": "nome_mae", "expand": True},
    {"type": "combo", "label": "CNH UF", "key": "cnh_uf", "values": UF_BR_VALUES},
    {"type": "entry", "label": "CNH Número", "key": "cnh_numero", "width": 200},
    {
        "type": "entry",
        "label": "CNH Data de expedição",
        "key": "cnh_data_expedicao",
        "width": 160,
    },
    {"type": "entry", "label": "RG", "key": "rg", "width": 200},
    {"type": "combo", "label": "Órgão RG", "key": "orgao_rg", "values": ORGAO_RG_CODES},
    {"type": "combo", "label": "UF RG", "key": "uf_rg", "values": UF_BR_VALUES},
    {"type": "entry", "label": "CPF", "key": "cpf", "width": 220},
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
