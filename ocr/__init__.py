"""OCR integration module for GraphorLM API."""

from ocr.graphor import (
    extract_by_type,
    extract_sections,
    extract_tables,
    get_all_elements,
    get_document_structure,
    list_elements,
    process_document,
    upload_document,
)
from ocr.utils import graphor_fetch


__all__ = [
    'DocumentAnalyzer',
    'extract_by_type',
    'extract_sections',
    'extract_tables',
    'get_all_elements',
    'get_document_structure',
    'graphor_fetch',
    'list_elements',
    'process_document',
    'upload_document'
]

