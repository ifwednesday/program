import logging
import re
from typing import Dict, Mapping, Set

logger = logging.getLogger(__name__)

_PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")

# Cache de templates em memória
_template_cache: Dict[str, str] = {}


def find_placeholders(template_text: str) -> Set[str]:
    keys: Set[str] = set()
    for match in _PLACEHOLDER_PATTERN.finditer(template_text):
        keys.add(match.group(1))
    return keys


def render_template(
    template_text: str, values: Mapping[str, object], strict: bool = False
) -> str:
    def _replace(match: re.Match) -> str:
        key = match.group(1)
        if key in values and values[key] is not None:
            return str(values[key])
        if strict:
            raise KeyError(f"Placeholder '{key}' não fornecido")
        return match.group(0)

    return _PLACEHOLDER_PATTERN.sub(_replace, template_text)


def load_template(template_path: str, use_cache: bool = True) -> str:
    """Carrega template de arquivo com suporte a cache"""
    if use_cache and template_path in _template_cache:
        logger.debug(f"Template carregado do cache: {template_path}")
        return _template_cache[template_path]

    try:
        from pathlib import Path

        path = Path(template_path)
        if not path.exists():
            raise FileNotFoundError(f"Template não encontrado: {template_path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if use_cache:
            _template_cache[template_path] = content
            logger.debug(f"Template carregado e cacheado: {template_path}")

        return content
    except Exception as e:
        logger.error(f"Erro ao carregar template {template_path}: {e}")
        raise


def clear_template_cache() -> None:
    """Limpa cache de templates"""
    count = len(_template_cache)
    _template_cache.clear()
    logger.info(f"Cache de templates limpo: {count} templates removidos")


def get_cache_info() -> Dict[str, object]:
    """Retorna informações sobre o cache"""
    return {
        "cached_templates": len(_template_cache),
        "cache_keys": list(_template_cache.keys()),
    }
