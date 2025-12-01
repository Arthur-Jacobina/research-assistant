from pydantic import BaseModel, Field
from typing import Optional, Any


class GetPaperRequest(BaseModel):
    arxiv_id: str = Field(..., description="arXiv paper ID (e.g., '2301.12345')")


class PaperSection(BaseModel):
    id: str = Field(..., description="Section UUID in database")
    section_number: int
    title: str
    content: Any = Field(..., description="Section content (can be text or structured data)")
    images: list[str] = Field(default=[], description="List of image filenames")
    created_at: Optional[str] = None


class GetPaperResponse(BaseModel):
    success: bool
    paper_id: str
    database_id: str = Field(..., description="UUID of the paper in database")
    title: str
    url: str
    created_at: Optional[str] = None
    total_sections: int
    sections: list[PaperSection]


class ParseLatexRequest(BaseModel):
    paper_id: str = Field(..., description="arXiv paper ID (e.g., '2301.12345')")


class ParsedSection(BaseModel):
    section_number: int
    title: str
    content: str


class ParseLatexResponse(BaseModel):
    success: bool
    paper_id: str
    title: str
    arxiv_url: str
    abstract: Optional[str] = None
    total_sections: int
    sections: list[ParsedSection]
    database_paper_id: str = Field(..., description="UUID of the paper in database")

