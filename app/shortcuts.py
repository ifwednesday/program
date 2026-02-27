"""Sistema de atalhos de teclado"""

import logging
import tkinter as tk
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)


class ShortcutManager:
    """Gerenciador de atalhos de teclado"""

    def __init__(self, app):
        self.app = app
        self.shortcuts: Dict[str, Dict[str, object]] = {}
        self._setup_shortcuts()

    def _setup_shortcuts(self) -> None:
        """Configura todos os atalhos de teclado"""
        # Atalhos principais
        self.register("<Control-g>", self._on_generate, "Gerar documento")
        self.register("<Control-G>", self._on_generate, "Gerar documento")

        self.register("<Control-s>", self._on_save, "Salvar arquivo")
        self.register("<Control-S>", self._on_save, "Salvar arquivo")

        self.register("<Control-l>", self._on_clear, "Limpar campos")
        self.register("<Control-L>", self._on_clear, "Limpar campos")

        self.register("<Control-c>", self._on_copy, "Copiar texto")
        self.register("<Control-C>", self._on_copy, "Copiar texto")

        self.register("<F5>", self._on_generate, "Gerar documento")

        self.register("<Control-q>", self._on_exit, "Sair")
        self.register("<Control-Q>", self._on_exit, "Sair")

        self.register("<Escape>", self._on_clear_focus, "Remover foco")

        logger.info(f"Atalhos de teclado configurados: {len(self.shortcuts)} atalhos")

    def register(self, key_combination: str, callback: Callable, description: str = "") -> None:
        """Registra um atalho de teclado"""
        self.shortcuts[key_combination] = {
            "callback": callback,
            "description": description,
        }
        self.app.bind(key_combination, callback)
        logger.debug(f"Atalho registrado: {key_combination} - {description}")

    def _get_current_tab(self) -> str:
        notebook = getattr(self.app, "notebook", None)
        if notebook is None:
            logger.warning("Atalho acionado antes da inicialização das abas")
            return ""
        try:
            return str(notebook.get()).strip()
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Falha ao identificar aba atual: {exc}")
            return ""

    def _execute_current_tab_action(self, action: str) -> bool:
        current_tab = self._get_current_tab()
        logger.info(f"Atalho {action} acionado na aba: {current_tab or 'desconhecida'}")

        handlers = {
            "MODELO SIMPLES": {
                "generate": self.app.handlers.on_generate_modelo,
                "save": self.app.handlers.on_save_modelo,
                "clear": self.app.handlers.on_clear_modelo,
                "copy": self.app.handlers.on_copy_modelo,
            },
            "MODELO": {
                "generate": self.app.handlers.on_generate_modelo,
                "save": self.app.handlers.on_save_modelo,
                "clear": self.app.handlers.on_clear_modelo,
                "copy": self.app.handlers.on_copy_modelo,
            },
            "CERTIDÃO": {
                "generate": self.app.handlers.on_generate_cert,
                "save": self.app.handlers.on_save_cert,
                "clear": self.app.handlers.on_clear_cert,
                "copy": self.app.handlers.on_copy_cert,
            },
            "CASADOS": {
                "generate": self.app.handlers.on_generate_casados,
                "save": self.app.handlers.on_save_casados,
                "clear": self.app.handlers.on_clear_casados,
                "copy": self.app.handlers.on_copy_casados,
            },
            "EMPRESA": {
                "generate": self.app.handlers.on_generate_empresa,
                "save": self.app.handlers.on_save_empresa,
                "clear": self.app.handlers.on_clear_empresa,
                "copy": self.app.handlers.on_copy_empresa,
            },
            "IMÓVEIS": {
                "generate": self.app.handlers.on_generate_imovel,
                "save": self.app.handlers.on_save_imovel,
                "clear": self.app.handlers.on_clear_imovel,
                "copy": self.app.handlers.on_copy_imovel,
            },
        }

        tab_actions = handlers.get(current_tab)
        if not tab_actions:
            logger.warning(f"Nenhuma ação mapeada para a aba: {current_tab}")
            return False

        callback = tab_actions.get(action)
        if not callback:
            logger.warning(f"Ação '{action}' não disponível para a aba: {current_tab}")
            return False

        callback()
        return True

    def _on_generate(self, event: tk.Event) -> str:
        """Gera documento da aba atual"""
        try:
            self._execute_current_tab_action("generate")
        except Exception as e:
            logger.error(f"Erro ao executar atalho Gerar: {e}")

        return "break"  # Prevenir propagação do evento

    def _on_save(self, event: tk.Event) -> str:
        """Salva documento da aba atual"""
        try:
            self._execute_current_tab_action("save")
        except Exception as e:
            logger.error(f"Erro ao executar atalho Salvar: {e}")

        return "break"

    def _on_clear(self, event: tk.Event) -> str:
        """Limpa campos da aba atual"""
        try:
            self._execute_current_tab_action("clear")
        except Exception as e:
            logger.error(f"Erro ao executar atalho Limpar: {e}")

        return "break"

    def _on_copy(self, event: tk.Event) -> Optional[str]:
        """Copia texto da aba atual sem bloquear Ctrl+C normal nos campos de entrada."""
        try:
            focused = self.app.focus_get()
            # Mantém Ctrl+C padrão para campos de entrada.
            if focused and not isinstance(focused, tk.Text):
                return None

            if self._execute_current_tab_action("copy"):
                return "break"
        except Exception as e:
            logger.error(f"Erro ao executar atalho Copiar: {e}")

        # Permitir Ctrl+C normal em outros widgets
        return None

    def _on_exit(self, event: tk.Event) -> str:
        """Sai da aplicação"""
        try:
            logger.info("Atalho Sair acionado")
            self.app.handlers.on_exit()
        except Exception as e:
            logger.error(f"Erro ao executar atalho Sair: {e}")

        return "break"

    def _on_clear_focus(self, event: tk.Event) -> str:
        """Remove foco do widget atual"""
        try:
            self.app.focus()
        except Exception as e:
            logger.error(f"Erro ao remover foco: {e}")

        return "break"

    def get_shortcuts_help(self) -> str:
        """Retorna string formatada com todos os atalhos"""
        help_text = "ATALHOS DE TECLADO DISPONÍVEIS:\n\n"
        shortcuts_by_desc: Dict[str, list[str]] = {}

        for key, info in self.shortcuts.items():
            desc = str(info["description"])
            if desc not in shortcuts_by_desc:
                shortcuts_by_desc[desc] = []
            shortcuts_by_desc[desc].append(key)

        for desc, keys in sorted(shortcuts_by_desc.items()):
            keys_str = " ou ".join(keys)
            help_text += f"  {keys_str:<20} - {desc}\n"

        return help_text

