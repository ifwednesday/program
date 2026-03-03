"""Compatibilidade de imports para extração de documentos.

Módulos concretos ficam em `app/extractors/`.
"""

from __future__ import annotations

try:
    from .extractors import (
        DocumentExtractor,
        ExtractionResult,
        ExtractorProtocol,
        GeminiDocumentExtractor,
        create_document_extractor,
    )
except Exception:
    from extractors import (  # type: ignore
        DocumentExtractor,
        ExtractionResult,
        ExtractorProtocol,
        GeminiDocumentExtractor,
        create_document_extractor,
    )

__all__ = [
    "DocumentExtractor",
    "ExtractionResult",
    "ExtractorProtocol",
    "GeminiDocumentExtractor",
    "create_document_extractor",
]
