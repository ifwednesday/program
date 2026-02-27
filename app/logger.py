"""Sistema de logging estruturado"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    enabled: bool = True,
    level: str = "INFO",
    max_file_size_mb: int = 10,
    backup_count: int = 3,
) -> None:
    """Configura sistema de logging da aplicação"""
    if not enabled:
        logging.disable(logging.CRITICAL)
        return

    # Criar diretório de logs se não existir
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Arquivo de log
    log_file = log_dir / "qualificador.log"

    # Configurar formato
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Converter nível de string para constante
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = level_map.get(level.upper(), logging.INFO)

    # Configurar logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remover handlers existentes
    root_logger.handlers.clear()

    # Handler para arquivo com rotação
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_file_size_mb * 1024 * 1024,  # Converter MB para bytes
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Handler para console (apenas erros e acima)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.ERROR)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    logging.info("Sistema de logging inicializado")
    logging.info(f"Nível de log: {level}")
    logging.info(f"Arquivo de log: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """Obtém logger para módulo específico"""
    return logging.getLogger(name)

