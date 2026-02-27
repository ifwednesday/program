"""Sistema de histórico de documentos gerados"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class HistoryManager:
    """Gerenciador de histórico de documentos"""

    def __init__(
        self,
        history_file: str = "history.json",
        max_items: int = 10,
        store_full_data: bool = False,
        mask_cpf: bool = True,
    ):
        self.history_file = Path(history_file)
        self.max_items = max_items
        self.store_full_data = store_full_data
        self.mask_cpf = mask_cpf
        self._history: List[Dict] = []
        self.load()

    @staticmethod
    def _only_digits(value: str) -> str:
        return "".join(ch for ch in (value or "") if ch.isdigit())

    def _mask_document(self, value: str) -> str:
        digits = self._only_digits(value)
        if len(digits) != 11:
            return value or ""
        return f"{digits[0:3]}.***.***-{digits[9:11]}"

    def _build_compact_data(self, data: Dict[str, str]) -> Dict[str, str]:
        allowlist = [
            "nome",
            "cpf",
            "cnpj",
            "razao_social",
            "nome_representante",
            "tipo_imovel",
            "cidade_imovel",
        ]
        compact = {k: data.get(k, "") for k in allowlist if data.get(k)}
        if "cpf" in compact and self.mask_cpf:
            compact["cpf"] = self._mask_document(compact["cpf"])
        return compact

    def _prepare_data(self, data: Dict[str, str]) -> Dict[str, str]:
        if self.store_full_data:
            prepared = dict(data)
            if self.mask_cpf and "cpf" in prepared:
                prepared["cpf"] = self._mask_document(prepared["cpf"])
            return prepared
        return self._build_compact_data(data)

    def load(self) -> None:
        """Carrega histórico do arquivo"""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self._history = json.load(f)
                logger.info(f"Histórico carregado: {len(self._history)} itens")
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao ler histórico: {e}")
                self._history = []
            except Exception as e:
                logger.error(f"Erro ao carregar histórico: {e}")
                self._history = []
        else:
            self._history = []

    def save(self) -> None:
        """Salva histórico no arquivo"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self._history, f, indent=2, ensure_ascii=False)
            logger.debug(f"Histórico salvo: {len(self._history)} itens")
        except Exception as e:
            logger.error(f"Erro ao salvar histórico: {e}")

    def add(self, doc_type: str, data: Dict[str, str]) -> None:
        """Adiciona entrada ao histórico"""
        raw_cpf = data.get("cpf", "")
        cpf_key = self._only_digits(raw_cpf)
        stored_cpf = self._mask_document(raw_cpf) if self.mask_cpf else raw_cpf

        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": doc_type,
            "nome": data.get("nome", ""),
            "cpf": stored_cpf,
            "cpf_key": cpf_key,
            "data": self._prepare_data(data),
        }

        # Remover duplicatas (mesmo CPF e tipo)
        if cpf_key:
            self._history = [
                h
                for h in self._history
                if not (
                    (
                        h.get("cpf_key")
                        or self._only_digits(str(h.get("cpf", "")))
                    )
                    == cpf_key
                    and h.get("type") == doc_type
                )
            ]

        # Adicionar no início
        self._history.insert(0, entry)

        # Limitar tamanho
        if len(self._history) > self.max_items:
            self._history = self._history[: self.max_items]

        self.save()
        logger.info(f"Entrada adicionada ao histórico: {doc_type} - {data.get('nome')}")

    def get_recent(self, doc_type: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Obtém entradas recentes do histórico"""
        if doc_type:
            filtered = [h for h in self._history if h.get("type") == doc_type]
            return filtered[:limit]
        return self._history[:limit]

    def get_by_cpf(self, cpf: str) -> Optional[Dict]:
        """Busca entrada por CPF"""
        cpf_key = self._only_digits(cpf)
        for entry in self._history:
            entry_cpf = entry.get("cpf_key") or self._only_digits(str(entry.get("cpf", "")))
            if entry_cpf == cpf_key:
                return entry
        return None

    def clear(self) -> None:
        """Limpa todo o histórico"""
        self._history = []
        self.save()
        logger.info("Histórico limpo")

    def get_all_cpfs(self) -> List[str]:
        """Retorna lista de todos os CPFs únicos no histórico"""
        cpfs = []
        seen = set()
        for entry in self._history:
            cpf = entry.get("cpf", "")
            if cpf and cpf not in seen:
                cpfs.append(cpf)
                seen.add(cpf)
        return cpfs

    def get_display_items(self, limit: int = 10) -> List[str]:
        """Retorna lista formatada para exibição em dropdown"""
        items = []
        for entry in self._history[:limit]:
            nome = entry.get("nome", "Sem nome")
            cpf = entry.get("cpf", "")
            timestamp = entry.get("timestamp", "")

            # Formatar data/hora
            try:
                dt = datetime.fromisoformat(timestamp)
                date_str = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                date_str = ""

            # Formatar item
            if cpf:
                display = f"{nome} - CPF: {cpf}"
            else:
                display = nome

            if date_str:
                display += f" ({date_str})"

            items.append(display)

        return items


# Instância global
_history_instance: Optional[HistoryManager] = None


def get_history_manager() -> HistoryManager:
    """Obtém instância global do gerenciador de histórico"""
    global _history_instance
    if _history_instance is None:
        from .config import get_config

        config = get_config()
        max_items = config.get("historico.max_items", 10)
        store_full_data = config.get("historico.store_full_data", False)
        mask_cpf = config.get("historico.mask_cpf", True)
        _history_instance = HistoryManager(
            max_items=max_items,
            store_full_data=store_full_data,
            mask_cpf=mask_cpf,
        )
    return _history_instance

