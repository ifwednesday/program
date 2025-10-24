"""Sistema de atalhos de teclado"""

import logging
import tkinter as tk

logger = logging.getLogger(__name__)


class ShortcutManager:
    """Gerenciador de atalhos de teclado"""

    def __init__(self, app):
        self.app = app
        self.shortcuts = {}
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

    def register(self, key_combination: str, callback, description: str = "") -> None:
        """Registra um atalho de teclado"""
        self.shortcuts[key_combination] = {"callback": callback, "description": description}
        self.app.bind(key_combination, callback)
        logger.debug(f"Atalho registrado: {key_combination} - {description}")

    def _on_generate(self, event: tk.Event) -> str:
        """Gera documento da aba atual"""
        try:
            current_tab = self.app.notebook.get()
            logger.info(f"Atalho Gerar acionado na aba: {current_tab}")
            
            if current_tab == "Modelo":
                self.app.handlers.on_generate_modelo()
            elif current_tab == "Certidão":
                self.app.handlers.on_generate_certidao()
            elif current_tab == "Casados":
                self.app.handlers.on_generate_casados()
            elif current_tab == "Empresa":
                self.app.handlers.on_generate_empresa()
            elif current_tab == "Imóvel":
                self.app.handlers.on_generate_imovel()
        except Exception as e:
            logger.error(f"Erro ao executar atalho Gerar: {e}")
        
        return "break"  # Prevenir propagação do evento

    def _on_save(self, event: tk.Event) -> str:
        """Salva documento da aba atual"""
        try:
            current_tab = self.app.notebook.get()
            logger.info(f"Atalho Salvar acionado na aba: {current_tab}")
            
            if current_tab == "Modelo":
                self.app.handlers.on_save_modelo()
            elif current_tab == "Certidão":
                self.app.handlers.on_save_certidao()
            elif current_tab == "Casados":
                self.app.handlers.on_save_casados()
            elif current_tab == "Empresa":
                self.app.handlers.on_save_empresa()
            elif current_tab == "Imóvel":
                self.app.handlers.on_save_imovel()
        except Exception as e:
            logger.error(f"Erro ao executar atalho Salvar: {e}")
        
        return "break"

    def _on_clear(self, event: tk.Event) -> str:
        """Limpa campos da aba atual"""
        try:
            current_tab = self.app.notebook.get()
            logger.info(f"Atalho Limpar acionado na aba: {current_tab}")
            
            if current_tab == "Modelo":
                self.app.handlers.on_clear_modelo()
            elif current_tab == "Certidão":
                self.app.handlers.on_clear_certidao()
            elif current_tab == "Casados":
                self.app.handlers.on_clear_casados()
            elif current_tab == "Empresa":
                self.app.handlers.on_clear_empresa()
            elif current_tab == "Imóvel":
                self.app.handlers.on_clear_imovel()
        except Exception as e:
            logger.error(f"Erro ao executar atalho Limpar: {e}")
        
        return "break"

    def _on_copy(self, event: tk.Event) -> str:
        """Copia texto da aba atual (só se widget de texto estiver focado)"""
        try:
            # Verificar se o foco está em um widget de texto (preview)
            focused = self.app.focus_get()
            if focused and isinstance(focused, tk.Text):
                current_tab = self.app.notebook.get()
                logger.info(f"Atalho Copiar acionado na aba: {current_tab}")
                
                if current_tab == "Modelo":
                    self.app.handlers.on_copy_modelo()
                elif current_tab == "Certidão":
                    self.app.handlers.on_copy_certidao()
                elif current_tab == "Casados":
                    self.app.handlers.on_copy_casados()
                elif current_tab == "Empresa":
                    self.app.handlers.on_copy_empresa()
                elif current_tab == "Imóvel":
                    self.app.handlers.on_copy_imovel()
                
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
        shortcuts_by_desc = {}
        
        for key, info in self.shortcuts.items():
            desc = info["description"]
            if desc not in shortcuts_by_desc:
                shortcuts_by_desc[desc] = []
            shortcuts_by_desc[desc].append(key)
        
        for desc, keys in sorted(shortcuts_by_desc.items()):
            keys_str = " ou ".join(keys)
            help_text += f"  {keys_str:<20} - {desc}\n"
        
        return help_text

