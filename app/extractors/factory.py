"""Factory do provider de extração de documentos."""

from __future__ import annotations

import os
from typing import List, Tuple

from .gemini import GeminiDocumentExtractor
from .local import DocumentExtractor, ExtractorProtocol


def create_document_extractor() -> Tuple[ExtractorProtocol, List[str]]:
    """
    Define provedor de extração.

    Variáveis:
    - EXTRACTION_PROVIDER=gemini|ml|local|auto (default: auto)
    - GEMINI_API_KEY=...
    - GEMINI_MODEL=gemini-2.5-flash (opcional)
    - ML_DOC_MODEL_PATH=app/models/doc_classifier.joblib (opcional)
    """
    provider = os.environ.get("EXTRACTION_PROVIDER", "auto").strip().lower()
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    warnings: List[str] = []

    if provider in {"gemini", "auto"} and api_key:
        return GeminiDocumentExtractor(api_key=api_key), warnings

    if provider == "gemini" and not api_key:
        warnings.append(
            "EXTRACTION_PROVIDER=gemini está ativo, mas GEMINI_API_KEY não foi definido; usado extrator local."
        )

    if provider in {"ml", "machine", "hybrid"}:
        model_path = os.environ.get(
            "ML_DOC_MODEL_PATH", "app/models/doc_classifier.joblib"
        ).strip()
        try:
            try:
                from ..ml_extraction import MLHybridDocumentExtractor
            except Exception:
                from ml_extraction import MLHybridDocumentExtractor  # type: ignore
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"Extrator ML indisponível ({exc}); usado extrator local.")
        else:
            extractor = MLHybridDocumentExtractor(model_path=model_path)
            return extractor, warnings

    return DocumentExtractor(), warnings
