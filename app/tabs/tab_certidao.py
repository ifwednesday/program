"""Aba Certidão reutilizando builders compartilhados."""

import customtkinter as ctk

try:
    from ..constants import ORGAO_RG_CODES
    from ..ui_builders.forms import UF_BR_VALUES
except ImportError:
    from constants import ORGAO_RG_CODES  # type: ignore
    from ui_builders.forms import UF_BR_VALUES  # type: ignore


def build_tab_certidao(
    notebook: ctk.CTkTabview, tab_certidao: ctk.CTkFrame, app
) -> None:
    container = ctk.CTkFrame(tab_certidao, corner_radius=12, fg_color="#2d2d2d")
    container.pack(fill="both", expand=True, padx=10, pady=5)

    # Scroll para acomodar todos os campos
    scroll_container = ctk.CTkScrollableFrame(
        container, corner_radius=8, fg_color="#3a3a3a"
    )
    scroll_container.pack(side="left", fill="both", expand=True)

    right = ctk.CTkFrame(container, corner_radius=8, fg_color="#3a3a3a")
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
        "values": ["Sr.", "Sra."],
    },
    {
        "type": "entry",
        "label": "Nome completo",
        "key": "nome",
        "width": 320,
        "expand": True,
    },
    {"type": "checkbox", "label": "Nome em MAIÚSCULAS", "key": "nome_caps"},
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
    {
        "type": "combo",
        "label": "Gênero (terminação)",
        "key": "genero_terminacao",
        "values": ["o", "a"],
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

    # Dados pessoais básicos
    row = app.form_builder.build_from_definition(
        parent, _CERTIDAO_FIELDS, start_row=row
    )

    # Separador
    ctk.CTkFrame(parent, height=2, fg_color="#4a4a4a").grid(
        row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=10
    )
    row += 1

    # Campos específicos da certidão
    for field in _CERTIDAO_EXTRA_FIELDS:
        if field["type"] == "separator":
            ctk.CTkFrame(parent, height=2, fg_color="#4a4a4a").grid(
                row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=10
            )
            row += 1
            continue
        row = app.form_builder.build_from_definition(parent, [field], start_row=row)

    parent.grid_columnconfigure(1, weight=1)
