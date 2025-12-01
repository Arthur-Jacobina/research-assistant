import sys
from pathlib import Path

# Add parent directory to path to avoid module name conflicts
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import HTTPException
from api.ocr.models import (
    ArxivToOCRRequest, 
    ArxivToOCRResponse,
    ProcessDocumentRequest,
    ProcessDocumentResponse,
    ListElementsRequest,
    ListElementsResponse,
    ExtractSectionsRequest,
    ExtractSectionsResponse,
    ArxivToSupabaseRequest,
    ArxivToSupabaseResponse,
    Section
)
from ocr.graphor import upload_document, process_document, list_elements, get_all_elements, extract_sections
from database.supabase import insert_paper, insert_sections

async def handle_process_document(process_request: ProcessDocumentRequest) -> ProcessDocumentResponse:
    """
    Process an already-uploaded document with a specific parsing method.
    """
    try:
        result = process_document(
            file_name=process_request.file_name,
            partition_method=process_request.partition_method.value
        )
        
        return ProcessDocumentResponse(
            success=True,
            status=result.get("status", "success"),
            message=result.get("message", "Document processed successfully"),
            file_name=result.get("file_name", process_request.file_name),
            file_size=result.get("file_size"),
            file_type=result.get("file_type"),
            file_source=result.get("file_source"),
            project_id=result.get("project_id"),
            project_name=result.get("project_name"),
            partition_method=result.get("partition_method", process_request.partition_method.value)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process document: {str(e)}"
        )


async def handle_list_elements(list_elements_request: ListElementsRequest) -> ListElementsResponse:
    """List all elements from a processed document."""
    try:
        result = get_all_elements(file_name=list_elements_request.file_name)
        return ListElementsResponse(success=True, elements=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list elements: {str(e)}")


async def handle_extract_sections(sections_request: ExtractSectionsRequest) -> ExtractSectionsResponse:
    """
    Extract document sections, breaking down content between titles.
    Images are handled with separate description and base64 fields.
    """
    try:
        sections = extract_sections(file_name=sections_request.file_name)
        
        return ExtractSectionsResponse(
            success=True,
            file_name=sections_request.file_name,
            total_sections=len(sections),
            sections=sections
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract sections: {str(e)}"
        )


async def handle_arxiv_to_supabase(arxiv_request: ArxivToSupabaseRequest) -> ArxivToSupabaseResponse:
    """
    Complete pipeline: Download arXiv paper, process with OCR, extract sections, and save to database.
    """
    pdf_path = None
    
    try:
        # Step 1: Download PDF
        pdf_path, paper_title = download_arxiv_pdf(arxiv_request.paper_id)
        
        # Step 2: Upload to OCR service
        ocr_response = upload_document(pdf_path)
        file_name = ocr_response.get("file_name")
        
        if not file_name:
            raise Exception("Failed to get file name from OCR upload")
        
        # Step 3: Process document with specified method
        process_result = process_document(
            file_name=file_name,
            partition_method=arxiv_request.partition_method.value
        )
        
        if process_result.get("status") != "success":
            raise Exception(f"Document processing failed: {process_result.get('message')}")
        
        # Step 4: Extract sections
        sections = extract_sections(file_name=file_name)
        
        # Step 5: Save to database
        arxiv_url = f"https://arxiv.org/abs/{arxiv_request.paper_id}"
        paper_data = insert_paper(arxiv_request.paper_id, paper_title, arxiv_url)
        
        if not paper_data:
            raise Exception("Failed to insert paper into database")
        
        paper_db_id = paper_data.get("id")
        
        # Prepare sections for database
        sections_data = []
        section_titles = []
        
        for section in sections:
            section_num = section.get("section_number", 0)
            section_title = section.get("title", "")
            section_titles.append(f"Section {section_num}: {section_title}")
            
            # Convert content list to structured data
            content_items = section.get("content", [])
            images = section.get("images", [])
            
            sections_data.append({
                "section_number": section_num,
                "title": section_title,
                "content": content_items,
                "images": [img.get("description", "") for img in images]
            })
        
        # Insert sections into database
        sections_result = insert_sections(paper_db_id, sections_data)
        
        if not sections_result:
            raise Exception("Failed to insert sections into database")
        
        return ArxivToSupabaseResponse(
            success=True,
            paper_id=arxiv_request.paper_id,
            paper_title=paper_title,
            arxiv_url=arxiv_url,
            database_paper_id=paper_db_id,
            total_sections=len(sections),
            sections_preview=section_titles,
            message=f"Successfully processed and stored paper '{paper_title}' with {len(sections)} sections"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process arXiv paper to Supabase: {str(e)}"
        )
    finally:
        if pdf_path:
            cleanup_temp_file(pdf_path)

