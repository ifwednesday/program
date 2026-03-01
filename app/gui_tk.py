"""Janela principal do Qualificador com tema CustomTkinter."""

import json
import logging
import sys
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox
from typing import Dict, Optional

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
    from .tabs.tab_extracao import build_tab_extracao
    from .template_engine import load_template as load_template_cached
    from .ui_builders.cnh import CNHSection
    from .ui_builders.forms import FormBuilder
    from .ui_builders.previews import PreviewBuilder
    from .ui_builders.theme import (
        ACCENT,
        ACCENT_HOVER,
        ACCENT_SOFT,
        BORDER,
        BORDER_STRONG,
        CONTENT_BG,
        FONT_FAMILY,
        SHELL_BG,
        SIDEBAR_BG,
        SURFACE_CARD,
        SURFACE_INPUT,
        SURFACE_SUBTLE,
        TEXT_MUTED,
        TEXT_PRIMARY,
        TEXT_SOFT,
        WARNING,
        WARNING_HOVER,
    )
except ImportError:
    from config import get_config  # type: ignore
    from handlers import EventHandlers  # type: ignore
    from history import get_history_manager  # type: ignore
    from logger import setup_logging  # type: ignore
    from shortcuts import ShortcutManager  # type: ignore
    from styles import setup_styles  # type: ignore
    from tabs.tab_casados import build_tab_casados  # type: ignore
    from tabs.tab_certidao import build_tab_certidao  # type: ignore
    from tabs.tab_extracao import build_tab_extracao  # type: ignore
    from template_engine import load_template as load_template_cached  # type: ignore
    from ui_builders.cnh import CNHSection  # type: ignore
    from ui_builders.forms import FormBuilder  # type: ignore
    from ui_builders.previews import PreviewBuilder  # type: ignore
    from ui_builders.theme import (  # type: ignore
        ACCENT,
        ACCENT_HOVER,
        ACCENT_SOFT,
        BORDER,
        BORDER_STRONG,
        CONTENT_BG,
        FONT_FAMILY,
        SHELL_BG,
        SIDEBAR_BG,
        SURFACE_CARD,
        SURFACE_INPUT,
        SURFACE_SUBTLE,
        TEXT_MUTED,
        TEXT_PRIMARY,
        TEXT_SOFT,
        WARNING,
        WARNING_HOVER,
    )

logger = logging.getLogger(__name__)
APP_VERSION = "2.2.1"
PROJECT_GITHUB_URL = "https://github.com/ifwednesday/program"
SIDEBAR_ITEMS = (
    ("MODELO SIMPLES", "Modelo Simples", "MS"),
    ("CERTIDÃO", "Certidão", "CT"),
    ("CASADOS", "Casados", "CS"),
    ("EMPRESA", "Empresa", "EP"),
    ("IMÓVEIS", "Imóveis", "IM"),
    ("EXTRAÇÃO", "Extração", "EX"),
    ("SOBRE", "Sobre", "SB"),
)


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
        self.app_config = get_config()

        # Inicializar sistema de logging
        setup_logging(
            enabled=self.app_config.get("logging.enabled", True),
            level=self.app_config.get("logging.level", "INFO"),
            max_file_size_mb=self.app_config.get("logging.max_file_size_mb", 10),
            backup_count=self.app_config.get("logging.backup_count", 3),
        )
        logger.info("=" * 60)
        logger.info("Aplicação Qualificador iniciada")
        logger.info("=" * 60)

        # Inicializar gerenciador de histórico
        self.history = get_history_manager()
        logger.info(f"Histórico carregado: {len(self.history._history)} entradas")

        self.title("Qualificador - by: ifwednesday")

        # Obter dimensões da janela da configuração
        window_width = self.app_config.get("ui.window_width", 1400)
        window_height = self.app_config.get("ui.window_height", 900)

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

        self._setup_window_icon()

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
            self.template_text_cert_cnh = load_template_text(
                templates_dir / "modelo_3_certidao_cnh.json"
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
            self.template_text_empresa_sem_cnh = load_template_text(
                templates_dir / "modelo_6_empresa_sem_cnh.json"
            )
            self.template_text_imovel = load_template_text(
                templates_dir / "modelo_7_imovel.json"
            )
            self.template_text_imovel_alternativo = load_template_text(
                templates_dir / "modelo_7_imovel_alternativo.json"
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Erro ao carregar template: {exc}")
            self.destroy()
            return

        self.vars: Dict[str, tk.Variable] = {}
        self._build_vars()
        self._setup_treatment_autofill()
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

    def _setup_window_icon(self) -> None:
        """Configura ícone com fallback para Windows/macOS/Linux."""
        ico_path = self.base_dir / "Qualificador.ico"
        png_path = self.base_dir / "Qualificador.png"
        self._icon_image: Optional[tk.PhotoImage] = None

        icon_applied = False
        if ico_path.exists():
            try:
                self.iconbitmap(str(ico_path))
                logger.info(f"Ícone .ico configurado: {ico_path}")
                icon_applied = True
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"Falha ao aplicar .ico na janela: {exc}")

        if png_path.exists():
            try:
                self._icon_image = tk.PhotoImage(file=str(png_path))
                self.iconphoto(True, self._icon_image)
                logger.info(f"Ícone .png configurado: {png_path}")
                icon_applied = True
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"Falha ao aplicar .png na janela: {exc}")

        if sys.platform == "win32":
            try:
                import ctypes

                myappid = "ifwednesday.qualificador.app.2.1"
                windll = getattr(ctypes, "windll", None)
                shell32 = getattr(windll, "shell32", None) if windll else None
                if shell32 is not None:
                    shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                    logger.info("App User Model ID configurado para barra de tarefas")
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"Não foi possível configurar App User Model ID: {exc}")

        if not icon_applied:
            logger.warning(
                "Ícone não aplicado. Verifique Qualificador.ico/Qualificador.png na raiz."
            )

    def _build_vars(self) -> None:
        defaults = self.app_config.get_defaults()

        def cfg(key: str, fallback: str) -> str:
            value = defaults.get(key, fallback)
            return str(value) if value is not None else fallback

        self.vars["tratamento"] = tk.StringVar(value=cfg("tratamento", "Sr."))
        self.vars["nome"] = tk.StringVar()
        self.vars["nacionalidade"] = tk.StringVar(
            value=cfg("nacionalidade", "brasileiro")
        )
        self.vars["estado_civil"] = tk.StringVar(value=cfg("estado_civil", "solteiro"))
        self.vars["naturalidade"] = tk.StringVar()
        self.vars["data_nascimento"] = tk.StringVar()
        self.vars["nome_pai"] = tk.StringVar()
        self.vars["nome_mae"] = tk.StringVar()
        self.vars["rg"] = tk.StringVar()
        self.vars["orgao_rg"] = tk.StringVar(value=cfg("orgao_rg", "SSP"))
        self.vars["uf_rg"] = tk.StringVar(value=cfg("uf_rg", "MT"))
        self.vars["cpf"] = tk.StringVar()
        self.vars["cpf_igual_rg"] = tk.BooleanVar(value=False)
        self.vars["profissao"] = tk.StringVar(value=cfg("profissao", "do lar"))
        self.vars["logradouro"] = tk.StringVar(
            value=cfg("logradouro", "Rua Campo Novo")
        )
        self.vars["numero"] = tk.StringVar(value=cfg("numero", "56"))
        self.vars["bairro"] = tk.StringVar(value=cfg("bairro", "Sant'Ana"))
        self.vars["cidade"] = tk.StringVar(value=cfg("cidade", "Nova Xavantina-MT"))
        self.vars["cep"] = tk.StringVar(value=cfg("cep", "78690-000"))
        self.vars["email"] = tk.StringVar(value=cfg("email", "não declarado"))
        self.vars["genero_terminacao"] = tk.StringVar(
            value=cfg("genero_terminacao", "o")
        )
        self.vars["cnh_uf"] = tk.StringVar(value=cfg("cnh_uf", "MT"))
        self.vars["cnh_numero"] = tk.StringVar(value="")
        self.vars["cnh_data_expedicao"] = tk.StringVar(value="")
        self.vars["cert_matricula"] = tk.StringVar(value="")
        self.vars["cert_data"] = tk.StringVar(value="")
        self.vars["tratamento1"] = tk.StringVar(value=cfg("tratamento1", "Sr."))
        self.vars["nome1"] = tk.StringVar(value="")
        self.vars["genero_terminacao1"] = tk.StringVar(
            value=cfg("genero_terminacao1", "o")
        )
        self.vars["naturalidade1"] = tk.StringVar(value="")
        self.vars["data_nascimento1"] = tk.StringVar(value="")
        self.vars["nome_pai1"] = tk.StringVar(value="")
        self.vars["nome_mae1"] = tk.StringVar(value="")
        self.vars["rg1"] = tk.StringVar(value="")
        self.vars["orgao_rg1"] = tk.StringVar(value=cfg("orgao_rg1", "SSP"))
        self.vars["uf_rg1"] = tk.StringVar(value=cfg("uf_rg1", "MT"))
        self.vars["cpf1"] = tk.StringVar(value="")
        self.vars["cpf_igual_rg1"] = tk.BooleanVar(value=False)
        self.vars["profissao1"] = tk.StringVar(value=cfg("profissao1", "do lar"))
        self.vars["cnh_uf1"] = tk.StringVar(value=cfg("cnh_uf1", "MT"))
        self.vars["cnh_numero1"] = tk.StringVar(value="")
        self.vars["cnh_data_expedicao1"] = tk.StringVar(value="")
        self.vars["email1"] = tk.StringVar(value=cfg("email1", "não declarado"))
        self.vars["tratamento2"] = tk.StringVar(value=cfg("tratamento2", "Sra."))
        self.vars["nome2"] = tk.StringVar(value="")
        self.vars["genero_terminacao2"] = tk.StringVar(
            value=cfg("genero_terminacao2", "a")
        )
        self.vars["naturalidade2"] = tk.StringVar(value="")
        self.vars["data_nascimento2"] = tk.StringVar(value="")
        self.vars["nome_pai2"] = tk.StringVar(value="")
        self.vars["nome_mae2"] = tk.StringVar(value="")
        self.vars["rg2"] = tk.StringVar(value="")
        self.vars["orgao_rg2"] = tk.StringVar(value=cfg("orgao_rg2", "SSP"))
        self.vars["uf_rg2"] = tk.StringVar(value=cfg("uf_rg2", "MT"))
        self.vars["cpf2"] = tk.StringVar(value="")
        self.vars["cpf_igual_rg2"] = tk.BooleanVar(value=False)
        self.vars["profissao2"] = tk.StringVar(value=cfg("profissao2", "do lar"))
        self.vars["cnh_uf2"] = tk.StringVar(value=cfg("cnh_uf2", "MT"))
        self.vars["cnh_numero2"] = tk.StringVar(value="")
        self.vars["cnh_data_expedicao2"] = tk.StringVar(value="")
        self.vars["email2"] = tk.StringVar(value=cfg("email2", "não declarado"))
        self.vars["regime_casamento"] = tk.StringVar(value="")
        self.vars["cert_casamento_matricula"] = tk.StringVar(value="")
        # Endereço específico para casados
        self.vars["logradouro_casados"] = tk.StringVar(
            value=cfg("logradouro_casados", "Rua Campo Novo")
        )
        self.vars["numero_casados"] = tk.StringVar(value=cfg("numero_casados", "56"))
        self.vars["bairro_casados"] = tk.StringVar(
            value=cfg("bairro_casados", "Sant'Ana")
        )
        self.vars["cidade_casados"] = tk.StringVar(
            value=cfg("cidade_casados", "Nova Xavantina-MT")
        )
        self.vars["cep_casados"] = tk.StringVar(value=cfg("cep_casados", "78690-000"))
        self.cnh_enabled1 = tk.BooleanVar(value=False)
        self.cnh_enabled2 = tk.BooleanVar(value=False)
        self.cnh_enabled_certidao = tk.BooleanVar(value=False)
        self.cnh_enabled_empresa = tk.BooleanVar(
            value=True
        )  # Default True porque template atual usa CNH
        self.casados_modelo_alternativo = tk.BooleanVar(value=False)
        self.imovel_modelo_alternativo = tk.BooleanVar(value=False)

        # Variáveis da empresa
        self.vars["razao_social"] = tk.StringVar(value="")
        self.vars["cnpj"] = tk.StringVar(value="")
        self.vars["junta_comercial"] = tk.StringVar(value="JUCEMAT")
        self.vars["nire"] = tk.StringVar(value="")
        self.vars["quadra_empresa"] = tk.StringVar(value="")
        self.vars["lote_empresa"] = tk.StringVar(value="")
        self.vars["logradouro_empresa"] = tk.StringVar(
            value=cfg("logradouro_empresa", "Rua Campo Novo")
        )
        self.vars["numero_empresa"] = tk.StringVar(value=cfg("numero_empresa", "56"))
        self.vars["bairro_empresa"] = tk.StringVar(
            value=cfg("bairro_empresa", "Sant'Ana")
        )
        self.vars["cidade_empresa"] = tk.StringVar(
            value=cfg("cidade_empresa", "Nova Xavantina-MT")
        )
        self.vars["cep_empresa"] = tk.StringVar(value=cfg("cep_empresa", "78690-000"))
        self.vars["email_empresa"] = tk.StringVar(
            value=cfg("email_empresa", "não declarado")
        )
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
        self.vars["email_pessoal"] = tk.StringVar(
            value=cfg("email_pessoal", "não declarado")
        )

        # Variáveis do imóvel
        self.vars["quantidade_imovel"] = tk.StringVar(value="Um (01)")
        self.vars["tipo_imovel"] = tk.StringVar(value="lote de terras")
        self.vars["zona_imovel"] = tk.StringVar(value="zona urbana")
        self.vars["cidade_imovel"] = tk.StringVar(
            value=cfg("cidade_imovel", "Nova Xavantina")
        )
        self.vars["estado_imovel"] = tk.StringVar(value="Mato Grosso")
        self.vars["loteamento"] = tk.StringVar(value="")
        self.vars["area_valor"] = tk.StringVar(value="")
        self.vars["area_unidade"] = tk.StringVar(value="m²")
        self.vars["area_por_extenso"] = tk.StringVar(value="")
        self.vars["lote"] = tk.StringVar(value="")
        self.vars["lote_por_extenso"] = tk.StringVar(value="")
        self.vars["quadra"] = tk.StringVar(value="")
        self.vars["quadra_por_extenso"] = tk.StringVar(value="")

    def _setup_treatment_autofill(self) -> None:
        self._bind_treatment_defaults(
            tratamento_key="tratamento",
            genero_key="genero_terminacao",
            nacionalidade_key="nacionalidade",
            estado_civil_key="estado_civil",
        )
        self._bind_treatment_defaults(
            tratamento_key="tratamento1", genero_key="genero_terminacao1"
        )
        self._bind_treatment_defaults(
            tratamento_key="tratamento2", genero_key="genero_terminacao2"
        )
        self._bind_treatment_defaults(
            tratamento_key="tratamento",
            genero_key="genero_terminacao",
            nacionalidade_key="nacionalidade_empresa",
            estado_civil_key="estado_civil_empresa",
        )

    def _bind_treatment_defaults(
        self,
        tratamento_key: str,
        genero_key: str,
        nacionalidade_key: str = "",
        estado_civil_key: str = "",
    ) -> None:
        tratamento_var = self.vars.get(tratamento_key)
        genero_var = self.vars.get(genero_key)
        if not isinstance(tratamento_var, tk.StringVar) or not isinstance(
            genero_var, tk.StringVar
        ):
            return

        def _on_change(*_args: object) -> None:
            genero = self._gender_from_treatment(tratamento_var.get())
            if genero not in {"o", "a"}:
                return
            genero_var.set(genero)

            if nacionalidade_key:
                nacionalidade_var = self.vars.get(nacionalidade_key)
                if isinstance(nacionalidade_var, tk.StringVar):
                    nacionalidade_var.set(
                        "brasileira" if genero == "a" else "brasileiro"
                    )

            if estado_civil_key:
                estado_civil_var = self.vars.get(estado_civil_key)
                if isinstance(estado_civil_var, tk.StringVar):
                    estado_civil_var.set(
                        self._normalize_estado_civil(
                            estado_civil_var.get(),
                            feminino=(genero == "a"),
                        )
                    )

        tratamento_var.trace_add("write", _on_change)
        _on_change()

    @staticmethod
    def _gender_from_treatment(tratamento: str) -> str:
        lowered = (tratamento or "").strip().lower()
        if lowered in {"sra.", "dra."}:
            return "a"
        if lowered in {"sr.", "dr."}:
            return "o"
        return ""

    @staticmethod
    def _normalize_estado_civil(estado_civil: str, feminino: bool) -> str:
        pares = {
            "solteiro": "solteira",
            "casado": "casada",
            "divorciado": "divorciada",
            "viúvo": "viúva",
        }
        base = (estado_civil or "").strip().lower()
        for masc, fem in pares.items():
            if base in {masc, fem}:
                return fem if feminino else masc
        return "solteira" if feminino else "solteiro"

    def _build_ui(self) -> None:
        shell = ctk.CTkFrame(self, corner_radius=0, fg_color=SHELL_BG)
        shell.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        main_layout = ctk.CTkFrame(shell, corner_radius=0, fg_color=SHELL_BG)
        main_layout.pack(fill=tk.BOTH, expand=True)

        self.sidebar = ctk.CTkFrame(
            main_layout,
            width=250,
            corner_radius=16,
            fg_color=SIDEBAR_BG,
            border_width=1,
            border_color=BORDER,
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.sidebar.pack_propagate(False)

        content_panel = ctk.CTkFrame(
            main_layout,
            corner_radius=16,
            fg_color=CONTENT_BG,
            border_width=1,
            border_color=BORDER,
        )
        content_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.notebook = ctk.CTkTabview(
            content_panel,
            corner_radius=12,
            fg_color=SURFACE_CARD,
            segmented_button_fg_color=SURFACE_SUBTLE,
            segmented_button_selected_color=ACCENT,
            text_color=TEXT_PRIMARY,
            segmented_button_selected_hover_color=ACCENT_HOVER,
        )
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_modelo_tab(self.notebook)
        self._build_certidao_tab(self.notebook)
        self._build_casados_tab(self.notebook)
        self._build_empresa_tab(self.notebook)
        self._build_imovel_tab(self.notebook)
        self._build_extracao_tab(self.notebook)
        self._build_about_tab(self.notebook)
        self._build_sidebar_menu()
        self._hide_notebook_header()
        self._set_active_tab("MODELO SIMPLES")
        self._build_status_bar()

    def _build_modelo_tab(self, notebook: ctk.CTkTabview) -> None:
        tab = notebook.add("MODELO SIMPLES")

        switch_frame = ctk.CTkFrame(
            tab,
            corner_radius=16,
            fg_color=SURFACE_CARD,
            border_width=1,
            border_color=BORDER,
        )
        switch_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        ctk.CTkSwitch(
            master=switch_frame,
            text="Usar dados de CNH",
            variable=self.cnh_enabled,
            command=self._toggle_cnh_fields,
            font=(FONT_FAMILY, 12, "bold"),
            text_color=TEXT_PRIMARY,
            progress_color=ACCENT,
            button_color=ACCENT,
            button_hover_color=ACCENT_HOVER,
            corner_radius=16,
        ).pack(anchor="w", padx=15, pady=10)

        main = ctk.CTkFrame(tab, corner_radius=16, fg_color=SURFACE_CARD)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        left_container = ctk.CTkFrame(
            main,
            corner_radius=16,
            fg_color=SURFACE_SUBTLE,
            border_width=1,
            border_color=BORDER,
        )
        right = ctk.CTkFrame(
            main,
            corner_radius=16,
            fg_color=SURFACE_SUBTLE,
            border_width=1,
            border_color=BORDER,
        )
        left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        left_scroll = ctk.CTkScrollableFrame(
            left_container, corner_radius=0, fg_color=SURFACE_SUBTLE
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

    def _build_extracao_tab(self, notebook: ctk.CTkTabview) -> None:
        tab_extracao = notebook.add("EXTRAÇÃO")
        build_tab_extracao(notebook, tab_extracao, self)

    def _build_about_tab(self, notebook: ctk.CTkTabview) -> None:
        tab_about = notebook.add("SOBRE")

        container = ctk.CTkFrame(tab_about, corner_radius=16, fg_color=SURFACE_CARD)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        header = ctk.CTkFrame(
            container,
            corner_radius=14,
            fg_color=SURFACE_SUBTLE,
            border_width=1,
            border_color=BORDER_STRONG,
        )
        header.pack(fill=tk.X, padx=12, pady=(12, 10))

        ctk.CTkLabel(
            header,
            text="QUALIFICADOR",
            font=(FONT_FAMILY, 20, "bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=14, pady=(12, 2))

        ctk.CTkLabel(
            header,
            text="Ferramenta de apoio para notas e registros",
            font=(FONT_FAMILY, 12),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", padx=14, pady=(0, 12))

        info = ctk.CTkFrame(
            container,
            corner_radius=14,
            fg_color=SURFACE_SUBTLE,
            border_width=1,
            border_color=BORDER,
        )
        info.pack(fill=tk.X, padx=12, pady=(0, 10))

        details = [
            ("Versão", APP_VERSION),
            ("Licença", "Uso Pessoal Não-Comercial"),
            ("Projeto", "ifwednesday/program"),
        ]
        for label, value in details:
            row = ctk.CTkFrame(info, fg_color="transparent")
            row.pack(fill=tk.X, padx=12, pady=6)
            ctk.CTkLabel(
                row,
                text=f"{label}:",
                width=95,
                anchor="w",
                font=(FONT_FAMILY, 11, "bold"),
                text_color=TEXT_MUTED,
            ).pack(side=tk.LEFT)
            ctk.CTkLabel(
                row,
                text=value,
                anchor="w",
                font=(FONT_FAMILY, 11),
                text_color=TEXT_PRIMARY,
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ctk.CTkButton(
            info,
            text="Abrir GitHub do Projeto",
            command=lambda: self._open_external_link(PROJECT_GITHUB_URL),
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            font=(FONT_FAMILY, 11, "bold"),
            height=34,
            corner_radius=17,
        ).pack(anchor="w", padx=12, pady=(8, 12))

        license_box = ctk.CTkTextbox(
            container,
            corner_radius=12,
            fg_color=SURFACE_INPUT,
            border_width=1,
            border_color=BORDER,
            text_color=TEXT_PRIMARY,
            font=(FONT_FAMILY, 10),
            wrap="word",
        )
        license_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        license_box.insert("1.0", self._get_license_excerpt())
        license_box.configure(state="disabled")

    def _build_sidebar_menu(self) -> None:
        self.sidebar_collapsed = False
        self.sidebar_width_expanded = 264
        self.sidebar_width_collapsed = 92

        header = ctk.CTkFrame(
            self.sidebar,
            corner_radius=14,
            fg_color=SURFACE_SUBTLE,
            border_width=1,
            border_color=BORDER,
        )
        header.pack(fill=tk.X, padx=10, pady=(12, 10))

        header_top = ctk.CTkFrame(header, fg_color="transparent")
        header_top.pack(fill=tk.X, padx=10, pady=(10, 6))

        self.sidebar_title = ctk.CTkLabel(
            header_top,
            text="QUALIFICADOR",
            font=(FONT_FAMILY, 14, "bold"),
            text_color=TEXT_PRIMARY,
        )
        self.sidebar_title.pack(side=tk.LEFT)

        self.btn_sidebar_toggle = ctk.CTkButton(
            header_top,
            text="◀",
            command=self._toggle_sidebar,
            width=30,
            height=26,
            corner_radius=13,
            fg_color=SURFACE_CARD,
            hover_color=SURFACE_SUBTLE,
            text_color=TEXT_PRIMARY,
            font=(FONT_FAMILY, 12, "bold"),
        )
        self.btn_sidebar_toggle.pack(side=tk.RIGHT)

        self.sidebar_subtitle = ctk.CTkLabel(
            header,
            text="Painel notarial",
            font=(FONT_FAMILY, 10),
            text_color=TEXT_MUTED,
        )
        self.sidebar_subtitle.pack(anchor="w", padx=10, pady=(0, 12))

        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER).pack(
            fill=tk.X, padx=14, pady=(0, 12)
        )

        self.sidebar_buttons: Dict[str, ctk.CTkButton] = {}
        self.sidebar_meta: Dict[str, tuple[str, str]] = {}
        for tab_name, label, icon in SIDEBAR_ITEMS:
            button = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}  {label}",
                anchor="w",
                command=lambda name=tab_name: self._set_active_tab(name),
                fg_color="transparent",
                hover_color=SURFACE_SUBTLE,
                text_color=TEXT_MUTED,
                corner_radius=12,
                height=42,
                font=(FONT_FAMILY, 11, "bold"),
                border_spacing=12,
                border_width=0,
            )
            button.pack(fill=tk.X, padx=10, pady=5)
            self.sidebar_buttons[tab_name] = button
            self.sidebar_meta[tab_name] = (icon, label)

        footer = ctk.CTkFrame(
            self.sidebar,
            corner_radius=14,
            fg_color=SURFACE_SUBTLE,
            border_width=1,
            border_color=BORDER,
        )
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=12)

        self.sidebar_footer_title = ctk.CTkLabel(
            footer,
            text="Acesso rápido",
            font=(FONT_FAMILY, 10),
            text_color=TEXT_MUTED,
        )
        self.sidebar_footer_title.pack(anchor="w", padx=10, pady=(8, 0))

        self.sidebar_footer_subtitle = ctk.CTkLabel(
            footer,
            text=f"Registro e Qualificação • v{APP_VERSION}",
            font=(FONT_FAMILY, 9),
            text_color=TEXT_SOFT,
        )
        self.sidebar_footer_subtitle.pack(anchor="w", padx=10, pady=(0, 10))

        self._refresh_sidebar_layout()

    def _hide_notebook_header(self) -> None:
        segmented = getattr(self.notebook, "_segmented_button", None)
        if segmented is not None:
            segmented.grid_remove()

    def _toggle_sidebar(self) -> None:
        self.sidebar_collapsed = not self.sidebar_collapsed
        self._refresh_sidebar_layout()

    def _refresh_sidebar_layout(self) -> None:
        collapsed = self.sidebar_collapsed
        self.sidebar.configure(
            width=(
                self.sidebar_width_collapsed
                if collapsed
                else self.sidebar_width_expanded
            )
        )

        self.sidebar_title.configure(text="QLF" if collapsed else "QUALIFICADOR")
        self.sidebar_subtitle.configure(text="" if collapsed else "Painel notarial")
        self.btn_sidebar_toggle.configure(text="▶" if collapsed else "◀")

        for tab_name, button in self.sidebar_buttons.items():
            icon, label = self.sidebar_meta[tab_name]
            if collapsed:
                button.configure(text=icon, anchor="center", border_spacing=0)
            else:
                button.configure(text=f"{icon}  {label}", anchor="w", border_spacing=12)

        if collapsed:
            self.sidebar_footer_title.configure(text="")
            self.sidebar_footer_subtitle.configure(text=f"v{APP_VERSION}")
        else:
            self.sidebar_footer_title.configure(text="Acesso rápido")
            self.sidebar_footer_subtitle.configure(
                text=f"Registro e Qualificação • v{APP_VERSION}"
            )

    def _set_active_tab(self, tab_name: str) -> None:
        self.notebook.set(tab_name)
        self._update_sidebar_selection(tab_name)

    def _update_sidebar_selection(self, tab_name: str) -> None:
        for name, button in self.sidebar_buttons.items():
            is_active = name == tab_name
            button.configure(
                fg_color=ACCENT if is_active else "transparent",
                hover_color=ACCENT if is_active else SURFACE_SUBTLE,
                text_color=TEXT_PRIMARY if is_active else TEXT_MUTED,
                border_width=1 if is_active else 0,
                border_color=ACCENT_SOFT if is_active else SURFACE_SUBTLE,
            )

    def _open_external_link(self, url: str) -> None:
        try:
            webbrowser.open(url, new=2)
            self.status.configure(text=f"Abrindo {url}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Não foi possível abrir o link: {exc}")

    def _get_license_excerpt(self) -> str:
        license_path = self.base_dir / "LICENSE"
        if not license_path.exists():
            return (
                "Arquivo LICENSE não encontrado.\n\n"
                "Licença ativa: Uso Pessoal Não-Comercial.\n"
                "Para uso empresarial/comercial, é necessária licença específica."
            )

        try:
            content = license_path.read_text(encoding="utf-8")
            lines = [line.rstrip() for line in content.splitlines()[:36]]
            return (
                "\n".join(lines)
                + "\n\n[...] Consulte o arquivo LICENSE completo para todos os termos."
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"Falha ao ler licença: {exc}")
            return (
                "Não foi possível carregar o texto da licença.\n"
                "Consulte o arquivo LICENSE na raiz do projeto."
            )

    def _build_status_bar(self) -> None:
        # Frame para a barra de status
        status_frame = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=SURFACE_CARD,
            border_width=1,
            border_color=BORDER,
        )
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Label de status à esquerda
        self.status = ctk.CTkLabel(
            status_frame,
            text="Pronto",
            font=(FONT_FAMILY, 10),
            text_color=TEXT_PRIMARY,
            fg_color=SURFACE_CARD,
            corner_radius=0,
            anchor="w",
        )
        self.status.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=12)

        # Label de licença à direita
        license_label = ctk.CTkLabel(
            status_frame,
            text="Uso Pessoal • Empresas: Licença Comercial Requerida",
            font=(FONT_FAMILY, 9),
            text_color=TEXT_SOFT,
            fg_color=SURFACE_CARD,
            corner_radius=0,
            anchor="e",
        )
        license_label.pack(side=tk.RIGHT, ipady=6, padx=12)

        self.btn_clear_cache = ctk.CTkButton(
            status_frame,
            text="Limpar cache",
            command=self.handlers.on_clear_cache,
            width=126,
            height=30,
            corner_radius=15,
            fg_color=WARNING,
            hover_color=WARNING_HOVER,
            text_color=TEXT_PRIMARY,
            font=(FONT_FAMILY, 9, "bold"),
        )
        self.btn_clear_cache.pack(side=tk.RIGHT, padx=(0, 12), pady=4)

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
