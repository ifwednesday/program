"""Janela principal do Qualificador com tema CustomTkinter."""

import json
import logging
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from typing import Dict

import customtkinter as ctk

try:
    from .config import get_config
    from .handlers import EventHandlers
    from .history import get_history_manager
    from .logger import setup_logging
    from .shortcuts import ShortcutManager
    from .styles import setup_styles
    from .tabs.tab_casados import build_tab_casados
    from .tabs.tab_certidao import build_tab_certidao
    from .template_engine import load_template as load_template_cached
    from .ui_builders.cnh import CNHSection
    from .ui_builders.forms import FormBuilder
    from .ui_builders.previews import PreviewBuilder
except ImportError:
    from config import get_config  # type: ignore
    from handlers import EventHandlers  # type: ignore
    from history import get_history_manager  # type: ignore
    from logger import setup_logging  # type: ignore
    from shortcuts import ShortcutManager  # type: ignore
    from styles import setup_styles  # type: ignore
    from tabs.tab_casados import build_tab_casados  # type: ignore
    from tabs.tab_certidao import build_tab_certidao  # type: ignore
    from template_engine import load_template as load_template_cached  # type: ignore
    from ui_builders.cnh import CNHSection  # type: ignore
    from ui_builders.forms import FormBuilder  # type: ignore
    from ui_builders.previews import PreviewBuilder  # type: ignore

logger = logging.getLogger(__name__)


def _base_dir() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[1]


def load_template_text(template_path: Path, use_cache: bool = True) -> str:
    """Carrega template JSON com suporte a cache"""
    try:
        # Usar cache de templates
        content = load_template_cached(str(template_path), use_cache=use_cache)
        data = json.loads(content)
        if not isinstance(data, dict) or "template" not in data:
            raise ValueError("Arquivo de template inválido: chave 'template' ausente")
        return data["template"]
    except FileNotFoundError:
        raise FileNotFoundError(f"Template não encontrado: {template_path}")
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON do template {template_path}: {e}")
        raise ValueError(f"Arquivo de template inválido: {e}")
    except Exception as e:
        logger.error(f"Erro ao carregar template {template_path}: {e}")
        raise


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        
        # Inicializar sistema de configuração
        self.config = get_config()
        
        # Inicializar sistema de logging
        setup_logging(
            enabled=self.config.get("logging.enabled", True),
            level=self.config.get("logging.level", "INFO"),
            max_file_size_mb=self.config.get("logging.max_file_size_mb", 10),
            backup_count=self.config.get("logging.backup_count", 3),
        )
        logger.info("=" * 60)
        logger.info("Aplicação Qualificador iniciada")
        logger.info("=" * 60)
        
        # Inicializar gerenciador de histórico
        self.history = get_history_manager()
        logger.info(f"Histórico carregado: {len(self.history._history)} entradas")
        
        self.title("Qualificador - by: ifwedesnay")

        # Obter dimensões da janela da configuração
        window_width = self.config.get("ui.window_width", 1400)
        window_height = self.config.get("ui.window_height", 900)
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Ajustar se for maior que a tela
        window_width = min(window_width, int(screen_width * 0.95))
        window_height = min(window_height, int(screen_height * 0.95))

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minsize(1200, 800)
        logger.info(f"Janela configurada: {window_width}x{window_height}")

        self.base_dir = _base_dir()
        
        # Configurar ícone da janela e barra de tarefas
        icon_path = self.base_dir / "Qualificador.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
                logger.info(f"Ícone da janela configurado: {icon_path}")
                
                # Configurar ícone da barra de tarefas no Windows
                try:
                    import ctypes
                    # Define App User Model ID para Windows 7+
                    myappid = 'ifwedesnay.qualificador.app.2.0'
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                    logger.info("App User Model ID configurado para barra de tarefas")
                except Exception as e:
                    logger.warning(f"Não foi possível configurar App User Model ID: {e}")
                    
            except Exception as e:
                logger.warning(f"Não foi possível definir o ícone da janela: {e}")
        else:
            logger.warning(f"Arquivo de ícone não encontrado: {icon_path}")
        
        templates_dir = self.base_dir / "templates"
        setup_styles(self)

        try:
            self.template_text = load_template_text(templates_dir / "modelo_1.json")
            self.template_text_cnh = load_template_text(
                templates_dir / "modelo_2_cnh.json"
            )
            self.template_text_cert = load_template_text(
                templates_dir / "modelo_3_certidao.json"
            )
            self.template_text_casados = load_template_text(
                templates_dir / "modelo_4_casados.json"
            )
            self.template_text_casados_sem_cnh = load_template_text(
                templates_dir / "modelo_5_casados_sem_cnh.json"
            )
            self.template_text_empresa = load_template_text(
                templates_dir / "modelo_6_empresa.json"
            )
            self.template_text_imovel = load_template_text(
                templates_dir / "modelo_7_imovel.json"
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Erro ao carregar template: {exc}")
            self.destroy()
            return

        self.vars: Dict[str, tk.Variable] = {}
        self._build_vars()
        self.handlers = EventHandlers(self)
        self.form_builder = FormBuilder(self)
        self.cnh_section = CNHSection(self)
        self.preview_builder = PreviewBuilder(self)
        self.cnh_enabled = tk.BooleanVar(value=False)

        self._build_ui()
        
        # Configurar atalhos de teclado
        self.shortcut_manager = ShortcutManager(self)
        logger.info("Atalhos de teclado configurados")
        
        logger.info("Aplicação inicializada com sucesso")

    def _build_vars(self) -> None:
        self.vars["tratamento"] = tk.StringVar(value="Sr.")
        self.vars["nome"] = tk.StringVar()
        self.vars["nome_caps"] = tk.BooleanVar(value=True)
        self.vars["nacionalidade"] = tk.StringVar(value="brasileiro")
        self.vars["estado_civil"] = tk.StringVar(value="solteiro")
        self.vars["naturalidade"] = tk.StringVar()
        self.vars["data_nascimento"] = tk.StringVar()
        self.vars["nome_pai"] = tk.StringVar()
        self.vars["nome_mae"] = tk.StringVar()
        self.vars["rg"] = tk.StringVar()
        self.vars["orgao_rg"] = tk.StringVar(value="SSP")
        self.vars["uf_rg"] = tk.StringVar(value="MT")
        self.vars["cpf"] = tk.StringVar()
        self.vars["profissao"] = tk.StringVar(value="do lar")
        self.vars["logradouro"] = tk.StringVar(value="Rua Campo Novo")
        self.vars["numero"] = tk.StringVar(value="56")
        self.vars["bairro"] = tk.StringVar(value="Sant'Ana")
        self.vars["cidade"] = tk.StringVar(value="Nova Xavantina-MT")
        self.vars["cep"] = tk.StringVar(value="78690-000")
        self.vars["email"] = tk.StringVar(value="não declarado")
        self.vars["genero_terminacao"] = tk.StringVar(value="o")
        self.vars["cnh_uf"] = tk.StringVar(value="MT")
        self.vars["cnh_numero"] = tk.StringVar(value="")
        self.vars["cnh_data_expedicao"] = tk.StringVar(value="")
        self.vars["cert_matricula"] = tk.StringVar(value="")
        self.vars["cert_data"] = tk.StringVar(value="")
        self.vars["tratamento1"] = tk.StringVar(value="Sr.")
        self.vars["nome1"] = tk.StringVar(value="")
        self.vars["nome_caps1"] = tk.BooleanVar(value=True)
        self.vars["genero_terminacao1"] = tk.StringVar(value="o")
        self.vars["naturalidade1"] = tk.StringVar(value="")
        self.vars["data_nascimento1"] = tk.StringVar(value="")
        self.vars["nome_pai1"] = tk.StringVar(value="")
        self.vars["nome_mae1"] = tk.StringVar(value="")
        self.vars["rg1"] = tk.StringVar(value="")
        self.vars["orgao_rg1"] = tk.StringVar(value="SSP")
        self.vars["uf_rg1"] = tk.StringVar(value="MT")
        self.vars["cpf1"] = tk.StringVar(value="")
        self.vars["profissao1"] = tk.StringVar(value="do lar")
        self.vars["cnh_uf1"] = tk.StringVar(value="MT")
        self.vars["cnh_numero1"] = tk.StringVar(value="")
        self.vars["cnh_data_expedicao1"] = tk.StringVar(value="")
        self.vars["email1"] = tk.StringVar(value="não declarado")
        self.vars["tratamento2"] = tk.StringVar(value="Sra.")
        self.vars["nome2"] = tk.StringVar(value="")
        self.vars["nome_caps2"] = tk.BooleanVar(value=True)
        self.vars["genero_terminacao2"] = tk.StringVar(value="a")
        self.vars["naturalidade2"] = tk.StringVar(value="")
        self.vars["data_nascimento2"] = tk.StringVar(value="")
        self.vars["nome_pai2"] = tk.StringVar(value="")
        self.vars["nome_mae2"] = tk.StringVar(value="")
        self.vars["rg2"] = tk.StringVar(value="")
        self.vars["orgao_rg2"] = tk.StringVar(value="SSP")
        self.vars["uf_rg2"] = tk.StringVar(value="MT")
        self.vars["cpf2"] = tk.StringVar(value="")
        self.vars["profissao2"] = tk.StringVar(value="do lar")
        self.vars["cnh_uf2"] = tk.StringVar(value="MT")
        self.vars["cnh_numero2"] = tk.StringVar(value="")
        self.vars["cnh_data_expedicao2"] = tk.StringVar(value="")
        self.vars["email2"] = tk.StringVar(value="não declarado")
        self.vars["regime_casamento"] = tk.StringVar(value="")
        self.vars["cert_casamento_matricula"] = tk.StringVar(value="")
        # Endereço específico para casados
        self.vars["logradouro_casados"] = tk.StringVar(value="Rua Campo Novo")
        self.vars["numero_casados"] = tk.StringVar(value="56")
        self.vars["bairro_casados"] = tk.StringVar(value="Sant'Ana")
        self.vars["cidade_casados"] = tk.StringVar(value="Nova Xavantina-MT")
        self.vars["cep_casados"] = tk.StringVar(value="78690-000")
        self.cnh_enabled1 = tk.BooleanVar(value=False)
        self.cnh_enabled2 = tk.BooleanVar(value=False)

        # Variáveis da empresa
        self.vars["razao_social"] = tk.StringVar(value="")
        self.vars["cnpj"] = tk.StringVar(value="")
        self.vars["junta_comercial"] = tk.StringVar(value="JUCEMAT")
        self.vars["nire"] = tk.StringVar(value="")
        self.vars["quadra_empresa"] = tk.StringVar(value="")
        self.vars["lote_empresa"] = tk.StringVar(value="")
        self.vars["logradouro_empresa"] = tk.StringVar(value="Rua Campo Novo")
        self.vars["numero_empresa"] = tk.StringVar(value="56")
        self.vars["bairro_empresa"] = tk.StringVar(value="Sant'Ana")
        self.vars["cidade_empresa"] = tk.StringVar(value="Nova Xavantina-MT")
        self.vars["cep_empresa"] = tk.StringVar(value="78690-000")
        self.vars["email_empresa"] = tk.StringVar(value="não declarado")
        self.vars["numero_alteracao"] = tk.StringVar(value="2ª")
        self.vars["numero_registro"] = tk.StringVar(value="")
        self.vars["data_registro"] = tk.StringVar(value="")
        self.vars["uf_junta"] = tk.StringVar(value="MT")
        self.vars["protocolo"] = tk.StringVar(value="")
        self.vars["data_certidao"] = tk.StringVar(value="")
        self.vars["autenticacao_eletronica"] = tk.StringVar(value="")
        self.vars["cargo_representante"] = tk.StringVar(value="sócia administradora")
        self.vars["nome_representante"] = tk.StringVar(value="")
        self.vars["nacionalidade_empresa"] = tk.StringVar(value="brasileira")
        self.vars["estado_civil_empresa"] = tk.StringVar(value="casada")
        self.vars["endereco_pessoal"] = tk.StringVar(value="")
        self.vars["email_pessoal"] = tk.StringVar(value="não declarado")

        # Variáveis do imóvel
        self.vars["quantidade_imovel"] = tk.StringVar(value="Um (01)")
        self.vars["tipo_imovel"] = tk.StringVar(value="lote de terras")
        self.vars["zona_imovel"] = tk.StringVar(value="zona urbana")
        self.vars["cidade_imovel"] = tk.StringVar(value="Nova Xavantina")
        self.vars["estado_imovel"] = tk.StringVar(value="Mato Grosso")
        self.vars["loteamento"] = tk.StringVar(value="")
        self.vars["area_valor"] = tk.StringVar(value="")
        self.vars["area_unidade"] = tk.StringVar(value="m²")
        self.vars["area_por_extenso"] = tk.StringVar(value="")
        self.vars["lote"] = tk.StringVar(value="")
        self.vars["lote_por_extenso"] = tk.StringVar(value="")
        self.vars["quadra"] = tk.StringVar(value="")
        self.vars["quadra_por_extenso"] = tk.StringVar(value="")

    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self, corner_radius=0, fg_color="#1a1a1a")
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        notebook = ctk.CTkTabview(
            container,
            corner_radius=12,
            fg_color="#2d2d2d",
            segmented_button_fg_color="#3a3a3a",
            segmented_button_selected_color="#1f6aa5",
            text_color="#ffffff",
            segmented_button_selected_hover_color="#1a5a8a",
        )
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._build_modelo_tab(notebook)
        self._build_certidao_tab(notebook)
        self._build_casados_tab(notebook)
        self._build_empresa_tab(notebook)
        self._build_imovel_tab(notebook)
        self._build_status_bar()

    def _build_modelo_tab(self, notebook: ctk.CTkTabview) -> None:
        tab = notebook.add("MODELO")

        switch_frame = ctk.CTkFrame(tab, corner_radius=12, fg_color="#2d2d2d")
        switch_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        ctk.CTkSwitch(
            master=switch_frame,
            text="Usar dados de CNH",
            variable=self.cnh_enabled,
            command=self._toggle_cnh_fields,
            font=("Segoe UI", 12, "bold"),
            text_color="#ffffff",
            progress_color="#1f6aa5",
            button_color="#1f6aa5",
            button_hover_color="#1a5a8a",
            corner_radius=8,
        ).pack(anchor="w", padx=15, pady=10)

        main = ctk.CTkFrame(tab, corner_radius=12, fg_color="#2d2d2d")
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        left_container = ctk.CTkFrame(main, corner_radius=8, fg_color="#3a3a3a")
        right = ctk.CTkFrame(main, corner_radius=8, fg_color="#3a3a3a")
        left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        left_scroll = ctk.CTkScrollableFrame(
            left_container, corner_radius=0, fg_color="#3a3a3a"
        )
        left_scroll.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        last_row = self.form_builder.build_common_fields(left_scroll)
        self.cnh_section.build(left_scroll, row=last_row)
        self.cnh_section.hide()

        commands = {
            "generate": self.handlers.on_generate_modelo,
            "copy": self.handlers.on_copy_modelo,
            "save": self.handlers.on_save_modelo,
            "clear": self.handlers.on_clear_modelo,
            "exit": self.handlers.on_exit,
        }
        self.preview_builder.build(right, "preview", commands)

    def _build_certidao_tab(self, notebook: ctk.CTkTabview) -> None:
        tab_certidao = notebook.add("CERTIDÃO")
        build_tab_certidao(notebook, tab_certidao, self)

    def _build_casados_tab(self, notebook: ctk.CTkTabview) -> None:
        tab_casados = notebook.add("CASADOS")
        build_tab_casados(notebook, tab_casados, self)

    def _build_empresa_tab(self, notebook: ctk.CTkTabview) -> None:
        tab_empresa = notebook.add("EMPRESA")
        try:
            from .tabs.tab_empresa import build_tab_empresa

            build_tab_empresa(notebook, tab_empresa, self)
        except ImportError:
            from tabs.tab_empresa import build_tab_empresa  # type: ignore

            build_tab_empresa(notebook, tab_empresa, self)

    def _build_imovel_tab(self, notebook: ctk.CTkTabview) -> None:
        tab_imovel = notebook.add("IMÓVEIS")
        try:
            from .tabs.tab_imovel import build_tab_imovel

            build_tab_imovel(notebook, tab_imovel, self)
        except ImportError:
            from tabs.tab_imovel import build_tab_imovel  # type: ignore

            build_tab_imovel(notebook, tab_imovel, self)

    def _build_status_bar(self) -> None:
        # Frame para a barra de status
        status_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#2d2d2d")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Label de status à esquerda
        self.status = ctk.CTkLabel(
            status_frame,
            text="Pronto",
            font=("Segoe UI", 10),
            text_color="#ffffff",
            fg_color="#2d2d2d",
            corner_radius=0,
            anchor="w",
        )
        self.status.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=10)
        
        # Label de licença à direita
        license_label = ctk.CTkLabel(
            status_frame,
            text="📋 Uso Pessoal • Empresas: Licença Comercial Requerida",
            font=("Segoe UI", 9),
            text_color="#888888",
            fg_color="#2d2d2d",
            corner_radius=0,
            anchor="e",
        )
        license_label.pack(side=tk.RIGHT, ipady=5, padx=10)

    def _toggle_cnh_fields(self) -> None:
        if self.cnh_enabled.get():
            self.cnh_section.show()
        else:
            self.cnh_section.hide()


def main() -> None:
    app = App()
    if app.winfo_exists():
        app.mainloop()


if __name__ == "__main__":
    main()
