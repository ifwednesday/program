"""Extratores de documentos organizados por provider."""

from .factory import create_document_extractor
from .gemini import GeminiDocumentExtractor
from .local import DocumentExtractor, ExtractionResult, ExtractorProtocol

__all__ = [
    "DocumentExtractor",
    "ExtractionResult",
    "ExtractorProtocol",
    "GeminiDocumentExtractor",
    "create_document_extractor",
]
