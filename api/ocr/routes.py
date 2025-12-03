from fastapi import APIRouter

from api.ocr.services import (
    handle_arxiv_to_supabase,
    handle_extract_sections,
    handle_list_elements,
    handle_process_document,
)


router = APIRouter(tags=['ocr'])

router.post('/arxiv/full-process')(handle_arxiv_to_supabase)
router.post('/ocr/process')(handle_process_document)
router.post('/ocr/list-elements')(handle_list_elements)
router.post('/ocr/extract-sections')(handle_extract_sections)

