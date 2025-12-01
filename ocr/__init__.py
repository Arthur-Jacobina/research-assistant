"""OCR integration module for GraphorLM API."""

from ocr.graphor import (
    upload_document,
    process_document,
    list_elements,
    get_all_elements,
    extract_tables,
    extract_by_type,
    get_document_structure,
    extract_sections,
)
from ocr.utils import graphor_fetch

__all__ = [
    "upload_document",
    "process_document",
    "list_elements",
    "get_all_elements",
    "extract_tables",
    "extract_by_type",
    "get_document_structure",
    "extract_sections",
    "DocumentAnalyzer",
    "graphor_fetch"
]

