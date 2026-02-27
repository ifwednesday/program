"""Sistema de configuração externa"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Configurações padrão (fallback caso config.json não exista)
DEFAULT_CONFIG = {
    "defaults": {
        "tratamento": "Sr.",
        "nacionalidade": "brasileiro",
        "estado_civil": "solteiro",
        "orgao_rg": "SSP",
        "uf_rg": "MT",
        "cnh_uf": "MT",
        "profissao": "do lar",
        "logradouro": "Rua Campo Novo",
        "numero": "56",
        "bairro": "Sant'Ana",
        "cidade": "Nova Xavantina-MT",
        "cep": "78690-000",
        "email": "não declarado",
        "genero_terminacao": "o",
    },
    "ui": {"theme": "dark", "font_size": 11, "window_width": 1400, "window_height": 900},
    "logging": {
        "enabled": True,
        "level": "INFO",
        "max_file_size_mb": 10,
        "backup_count": 3,
    },
    "historico": {
        "enabled": True,
        "max_items": 10,
        "store_full_data": False,
        "mask_cpf": True,
    },
}


class Config:
    """Gerenciador de configurações da aplicação"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Carrega configurações do arquivo JSON"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                logger.info(f"Configurações carregadas de {self.config_file}")
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao ler config.json: {e}. Usando padrões.")
                self._config = DEFAULT_CONFIG.copy()
            except Exception as e:
                logger.error(f"Erro inesperado ao carregar config: {e}")
                self._config = DEFAULT_CONFIG.copy()
        else:
            logger.info("config.json não encontrado. Usando configurações padrão.")
            self._config = DEFAULT_CONFIG.copy()
            self.save()  # Criar arquivo com padrões

    def save(self) -> None:
        """Salva configurações no arquivo JSON"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configurações salvas em {self.config_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Define valor de configuração"""
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def get_defaults(self) -> Dict[str, str]:
        """Obtém todos os valores padrão consolidados"""
        defaults = {}
        defaults.update(self._config.get("defaults", {}))
        defaults.update(self._config.get("defaults_casados", {}))
        defaults.update(self._config.get("defaults_empresa", {}))
        defaults.update(self._config.get("defaults_imovel", {}))
        return defaults


# Instância global de configuração
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Obtém instância global de configuração"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

