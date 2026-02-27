"""Componentes para o bloco CNH da aba MODELO."""

import customtkinter as ctk
from typing import Union

from .components import ComboFactory, EntryFactory, LabelFactory
from .theme import BORDER

CNH_UF_VALUES = [
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


class CNHSection:
    def __init__(self, app) -> None:
        self.app = app
        self.labels = LabelFactory()
        self.combos = ComboFactory()
        self.entries = EntryFactory()

    def build(
        self, parent: Union[ctk.CTkFrame, ctk.CTkScrollableFrame], row: int
    ) -> int:
        self.app.cnh_separator = ctk.CTkFrame(parent, height=2, fg_color=BORDER)
        self.app.cnh_separator.grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=10
        )
        row += 1

        self.app.cnh_uf_label = self.labels.create(parent, "CNH UF")
        self.app.cnh_uf_entry = self.combos.create(
            parent, variable=self.app.vars["cnh_uf"], values=CNH_UF_VALUES, width=100
        )
        self.app.cnh_numero_label = self.labels.create(parent, "CNH Número")
        self.app.cnh_numero_entry = self.entries.create(
            parent, textvariable=self.app.vars["cnh_numero"], width=200
        )
        self.app.cnh_data_label = self.labels.create(parent, "CNH Data expedição")
        self.app.cnh_data_entry = self.entries.create(
            parent,
            textvariable=self.app.vars["cnh_data_expedicao"],
            width=200,
            field_type="date",
        )

        self.app.cnh_uf_label.grid(row=row, column=0, sticky="w", padx=(15, 6), pady=2)
        self.app.cnh_uf_entry.grid(row=row, column=1, sticky="w", pady=2, padx=(0, 15))
        row += 1
        self.app.cnh_numero_label.grid(
            row=row, column=0, sticky="w", padx=(15, 6), pady=2
        )
        self.app.cnh_numero_entry.grid(
            row=row, column=1, sticky="ew", pady=2, padx=(0, 15)
        )
        row += 1
        self.app.cnh_data_label.grid(
            row=row, column=0, sticky="w", padx=(15, 6), pady=2
        )
        self.app.cnh_data_entry.grid(
            row=row, column=1, sticky="ew", pady=2, padx=(0, 15)
        )

        parent.grid_columnconfigure(1, weight=1)
        return row + 1

    def hide(self) -> None:
        self.app.cnh_separator.grid_remove()
        self.app.cnh_uf_label.grid_remove()
        self.app.cnh_uf_entry.grid_remove()
        self.app.cnh_numero_label.grid_remove()
        self.app.cnh_numero_entry.grid_remove()
        self.app.cnh_data_label.grid_remove()
        self.app.cnh_data_entry.grid_remove()

    def show(self) -> None:
        self.app.cnh_separator.grid()
        self.app.cnh_uf_label.grid()
        self.app.cnh_uf_entry.grid()
        self.app.cnh_numero_label.grid()
        self.app.cnh_numero_entry.grid()
        self.app.cnh_data_label.grid()
        self.app.cnh_data_entry.grid()
