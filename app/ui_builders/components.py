"""Fábricas de widgets CustomTkinter."""

from typing import Any, List, Optional, Sequence, Tuple, Union

import customtkinter as ctk


class LabelFactory:
    def __init__(
        self,
        text_color: str = "#ffffff",
        font: Tuple[str, int, str] = ("Segoe UI", 11, "bold"),
    ):
        self.text_color = text_color
        self.font = font

    def create(
        self,
        parent: Any,
        text: str,
        width: int = 160,
        height: int = 25,
        anchor: str = "w",
    ) -> ctk.CTkLabel:
        return ctk.CTkLabel(
            parent,
            text=text,
            width=width,
            height=height,
            font=self.font,
            text_color=self.text_color,
            anchor=anchor,
        )


class EntryFactory:
    def create(
        self,
        parent: Any,
        textvariable,
        width: int = 200,
        height: int = 32,
        state: str = "normal",
        field_type: str = "text",
    ) -> ctk.CTkEntry:
        entry = ctk.CTkEntry(
            parent,
            textvariable=textvariable,
            width=width,
            height=height,
            corner_radius=8,
            border_width=2,
            border_color="#4a4a4a",
            fg_color="#2a2a2a",
            text_color="#ffffff",
            placeholder_text_color="#b3b3b3",
            font=("Segoe UI", 11),
            state=state,
        )

        # Aplicar formatação automática baseada no tipo de campo
        if field_type == "cpf":
            try:
                from ..validators import auto_format_cpf

                entry.bind("<KeyRelease>", auto_format_cpf)
            except ImportError:
                from validators import auto_format_cpf  # type: ignore

                entry.bind("<KeyRelease>", auto_format_cpf)
        elif field_type == "date":
            try:
                from ..validators import auto_format_date

                entry.bind("<KeyRelease>", auto_format_date)
            except ImportError:
                from validators import auto_format_date  # type: ignore

                entry.bind("<KeyRelease>", auto_format_date)
        elif field_type == "cnpj":
            try:
                from ..validators import auto_format_cnpj

                entry.bind("<KeyRelease>", auto_format_cnpj)
            except ImportError:
                from validators import auto_format_cnpj  # type: ignore

                entry.bind("<KeyRelease>", auto_format_cnpj)

        return entry


class ComboFactory:
    def create(
        self,
        parent: Any,
        variable,
        values: Sequence[str],
        width: int = 120,
        height: int = 32,
        state: str = "readonly",
        enable_search: bool = True,
    ) -> ctk.CTkComboBox:
        combo = ctk.CTkComboBox(
            parent,
            variable=variable,
            values=list(values),
            width=width,
            height=height,
            corner_radius=8,
            border_width=2,
            border_color="#4a4a4a",
            fg_color="#2a2a2a",
            text_color="#ffffff",
            dropdown_fg_color="#2a2a2a",
            dropdown_text_color="#ffffff",
            dropdown_hover_color="#3a3a3a",
            button_color="#4a4a4a",
            button_hover_color="#5a5a5a",
            font=("Segoe UI", 11),
            state=state,
        )

        if enable_search:
            self._setup_keyboard_navigation(combo, list(values))

        return combo

    def _setup_keyboard_navigation(
        self, combo: ctk.CTkComboBox, values: List[str]
    ) -> None:
        """Configura navegação cíclica por teclado"""
        last_key = {"char": "", "index": -1}

        def on_keypress(event):
            if event.char and event.char.isalnum():
                char = event.char.upper()

                # Encontrar todos os valores que começam com esta letra
                matching = [v for v in values if v.upper().startswith(char)]

                if not matching:
                    return

                # Se mesma tecla, avançar para próximo na sequência
                if char == last_key["char"]:
                    last_key["index"] = (last_key["index"] + 1) % len(matching)
                else:
                    last_key["char"] = char
                    last_key["index"] = 0

                combo.set(matching[last_key["index"]])

        combo.bind("<KeyPress>", on_keypress)


class ButtonFactory:
    def __init__(self, font: Union[Tuple[str, int], Tuple[str, int, str]] = ("Segoe UI", 11)):
        self.font = font

    def create(
        self,
        parent: Any,
        text: str,
        command,
        fg_color: str,
        hover_color: str,
        text_color: str = "#ffffff",
        state: str = "normal",
        corner_radius: int = 8,
        font: Optional[Union[Tuple[str, int], Tuple[str, int, str]]] = None,
    ) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            font=font or self.font,
            state=state,
            corner_radius=corner_radius,
        )
