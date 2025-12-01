from fastapi import HTTPException
from api.paper.models import (
    GetPaperRequest,
    GetPaperResponse,
    PaperSection,
    ParseLatexRequest,
    ParseLatexResponse,
    ParsedSection
)
from arxiv_parser.latex_parser import parse_arxiv_latex
from database.supabase import (
    insert_paper,
    insert_sections,
    get_paper_with_sections,
    get_paper_by_arxiv_id,
    delete_paper_sections
)


async def handle_get_paper(paper_request: GetPaperRequest) -> GetPaperResponse:
    """
    Get a paper and all its sections from the database by arXiv ID.
    """
    try:
        # Get paper with sections from database
        paper_data = get_paper_with_sections(paper_request.arxiv_id)
        
        if not paper_data:
            raise HTTPException(
                status_code=404,
                detail=f"Paper with arXiv ID '{paper_request.arxiv_id}' not found in database"
            )
        
        # Convert sections to response model
        sections = [
            PaperSection(
                id=str(section.get("id")),
                section_number=section.get("section_number"),
                title=section.get("title"),
                content=section.get("content"),
                images=section.get("images", []),
                created_at=section.get("created_at")
            )
            for section in paper_data.get("sections", [])
        ]
        
        return GetPaperResponse(
            success=True,
            paper_id=paper_data.get("arxiv_id"),
            database_id=str(paper_data.get("id")),
            title=paper_data.get("title"),
            url=paper_data.get("url"),
            created_at=paper_data.get("created_at"),
            total_sections=len(sections),
            sections=sections
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve paper: {str(e)}"
        )


async def handle_parse_latex(latex_request: ParseLatexRequest) -> ParseLatexResponse:
    """
    Download and parse an arXiv paper's LaTeX source, extracting sections and content.
    If paper already exists in database, returns the cached version for optimization.
    """
    try:
        # Check if paper already exists in database
        existing_paper = get_paper_with_sections(latex_request.paper_id)
        
        if existing_paper and existing_paper.get("sections"):
            # Paper exists with sections, return cached data (optimization)
            sections = [
                ParsedSection(
                    section_number=section.get("section_number"),
                    title=section.get("title"),
                    content=section.get("content", "")
                )
                for section in existing_paper.get("sections", [])
            ]
            
            # Extract abstract (section 0)
            abstract = None
            for section in sections:
                if section.section_number == 0:
                    abstract = section.content
                    break
            
            return ParseLatexResponse(
                success=True,
                paper_id=existing_paper.get("arxiv_id"),
                title=existing_paper.get("title"),
                arxiv_url=existing_paper.get("url"),
                abstract=abstract,
                total_sections=len(sections),
                sections=sections,
                database_paper_id=str(existing_paper.get("id"))
            )
        
        # Paper doesn't exist or has no sections, parse from LaTeX source
        parsed_data = parse_arxiv_latex(latex_request.paper_id)
        
        # Convert sections to response model
        sections = [
            ParsedSection(
                section_number=section['section_number'],
                title=section['title'],
                content=section['content']
            )
            for section in parsed_data['sections']
        ]
        
        # Save to database
        arxiv_url = parsed_data['arxiv_url']
        
        if existing_paper:
            # Paper exists but no sections, reuse paper ID
            database_paper_id = existing_paper.get("id")
        else:
            # Insert new paper
            paper_data = insert_paper(
                latex_request.paper_id,
                parsed_data['title'],
                arxiv_url
            )
            
            if not paper_data:
                raise Exception("Failed to insert paper into database")
            
            database_paper_id = paper_data.get("id")
        
        # Prepare sections for database (only non-appendix integer sections)
        sections_to_insert = [
            {
                "section_number": section['section_number'],
                "title": section['title'],
                "content": section['content'],
                "images": []
            }
            for section in parsed_data['sections']
            if isinstance(section['section_number'], int)
        ]
        
        # Insert sections
        if sections_to_insert:
            result = insert_sections(database_paper_id, sections_to_insert)
            if not result:
                raise Exception("Failed to insert sections into database")
        
        return ParseLatexResponse(
            success=True,
            paper_id=parsed_data['paper_id'],
            title=parsed_data['title'],
            arxiv_url=parsed_data['arxiv_url'],
            abstract=parsed_data.get('abstract'),
            total_sections=len(sections),
            sections=sections,
            database_paper_id=database_paper_id
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse LaTeX: {str(e)}"
        )

