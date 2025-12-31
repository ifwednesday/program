"""Construção de formulários compartilhados entre as abas."""

from typing import Iterable, Mapping

import customtkinter as ctk

try:
    from ..constants import ORGAO_RG_CODES
except ImportError:
    from constants import ORGAO_RG_CODES  # type: ignore

from .components import ComboFactory, EntryFactory, LabelFactory

FieldSpec = Mapping[str, object]

UF_BR_VALUES = [
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
]


class FormBuilder:
    def __init__(self, app) -> None:
        self.app = app
        self.labels = LabelFactory()
        self.entries = EntryFactory()
        self.combos = ComboFactory()

    def build_common_fields(self, parent: ctk.CTkFrame) -> int:
        fields: Iterable[FieldSpec] = (
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
            {
                "type": "entry",
                "label": "Nome do pai",
                "key": "nome_pai",
                "expand": True,
            },
            {
                "type": "entry",
                "label": "Nome da mãe",
                "key": "nome_mae",
                "expand": True,
            },
            {"type": "entry", "label": "RG (número)", "key": "rg", "width": 200},
            {
                "type": "combo",
                "label": "Órgão RG",
                "key": "orgao_rg",
                "values": ORGAO_RG_CODES,
            },
            {"type": "combo", "label": "UF RG", "key": "uf_rg", "values": UF_BR_VALUES},
            {"type": "entry", "label": "CPF", "key": "cpf", "width": 220},
            {"type": "entry", "label": "Profissão", "key": "profissao", "expand": True},
            {
                "type": "entry",
                "label": "Logradouro",
                "key": "logradouro",
                "expand": True,
            },
            {"type": "entry", "label": "Número", "key": "numero", "width": 120},
            {"type": "entry", "label": "Bairro", "key": "bairro", "expand": True},
            {"type": "entry", "label": "Cidade", "key": "cidade", "expand": True},
            {"type": "entry", "label": "CEP", "key": "cep", "width": 160},
            {"type": "entry", "label": "E-mail", "key": "email", "expand": True},
            {
                "type": "combo",
                "label": "Gênero (terminação)",
                "key": "genero_terminacao",
                "values": ["o", "a"],
            },
        )
        return self.build_from_definition(parent, fields)

    def build_from_definition(
        self, parent: ctk.CTkFrame, fields: Iterable[FieldSpec], start_row: int = 0
    ) -> int:
        row = start_row
        for field in fields:
            row = self._render_field(parent, field, row)
        return row

    def _render_field(self, parent: ctk.CTkFrame, field: FieldSpec, row: int) -> int:
        field_type = field["type"]
        label = field["label"]
        key = field["key"]

        if field_type == "checkbox":
            ctk.CTkCheckBox(
                parent,
                text=label,
                variable=self.app.vars[key],
                fg_color="#1f6aa5",
                hover_color="#1a5a8a",
                text_color="#ffffff",
                font=("Segoe UI", 11),
                corner_radius=8,
                border_width=2,
            ).grid(row=row, column=0, columnspan=2, sticky="w", padx=15, pady=2)
            return row + 1

        self.labels.create(
            parent, label, width=int(field.get("label_width", 160))
        ).grid(row=row, column=0, sticky="w", padx=(15, 6), pady=2)

        if field_type == "entry":
            width = int(field.get("width", 240))
            sticky = "ew" if field.get("expand") else "w"
            # Determinar tipo de formatação baseado na chave do campo
            format_type = self._get_field_format_type(key)
            self.entries.create(
                parent,
                textvariable=self.app.vars[key],
                width=width,
                field_type=format_type,
            ).grid(row=row, column=1, sticky=sticky, pady=2, padx=(0, 15))
        elif field_type == "combo":
            self.combos.create(
                parent, variable=self.app.vars[key], values=list(field["values"])
            ).grid(row=row, column=1, sticky="w", pady=2, padx=(0, 15))
        else:
            raise ValueError(f"Tipo de campo não suportado: {field_type}")

        parent.grid_columnconfigure(1, weight=1)
        return row + 1

    def _get_field_format_type(self, key: str) -> str:
        """Determina o tipo de formatação baseado na chave do campo"""
        if "cpf" in key.lower():
            return "cpf"
        elif any(
            date_key in key.lower()
            for date_key in [
                "data_nascimento",
                "data_registro",
                "data_certidao",
                "cnh_data_expedicao",
                "cert_data",
            ]
        ):
            return "date"
        elif "cnpj" in key.lower():
            return "cnpj"
        else:
            return "text"
