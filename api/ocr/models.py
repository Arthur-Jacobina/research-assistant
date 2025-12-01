from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PartitionMethod(str, Enum):
    """Available document processing methods."""
    BASIC = 'basic'
    OCR = 'ocr'
    HI_RES = 'hi_res'
    HI_RES_FT = 'hi_res_ft'
    GRAPHORLM = 'graphorlm'
    MAI = 'mai'


class ArxivToOCRRequest(BaseModel):
    paper_id: str


class ArxivToOCRResponse(BaseModel):
    success: bool
    paper_id: str
    paper_title: str
    ocr_response: dict
    message: str


class ProcessDocumentRequest(BaseModel):
    file_name: str = Field(..., description='Name of the previously uploaded file')
    partition_method: PartitionMethod = Field(
        default=PartitionMethod.MAI,
        description='Processing method to use'
    )


class ProcessDocumentResponse(BaseModel):
    success: bool
    status: str
    message: str
    file_name: str
    file_size: int | None = None
    file_type: str | None = None
    file_source: str | None = None
    project_id: str | None = None
    project_name: str | None = None
    partition_method: str


class ListElementsRequest(BaseModel):
    file_name: str


class ListElementsResponse(BaseModel):
    success: bool
    elements: Any


class ExtractSectionsRequest(BaseModel):
    file_name: str = Field(..., description='Name of the processed file to extract sections from')


class ImageData(BaseModel):
    description: str = Field(..., description='Text description of the image')
    base64: str = Field(..., description='Base64 encoded image data')
    page: int
    position: int
    bounding_box: dict | None = None


class ContentItem(BaseModel):
    type: str = Field(..., description='Element type (e.g., Text, Table, etc.)')
    text: str
    page: int
    position: int


class Section(BaseModel):
    section_number: int
    title: str = Field(..., description='Section title, empty for content before first title')
    content: list[ContentItem]
    images: list[ImageData]


class ExtractSectionsResponse(BaseModel):
    success: bool
    file_name: str
    total_sections: int
    sections: list[Section]


class ArxivToSupabaseRequest(BaseModel):
    paper_id: str = Field(..., description="arXiv paper ID (e.g., '2301.12345')")
    partition_method: PartitionMethod = Field(
        default=PartitionMethod.GRAPHORLM,
        description='Processing method to use, defaults to graphorlm'
    )


class ArxivToSupabaseResponse(BaseModel):
    success: bool
    paper_id: str
    paper_title: str
    arxiv_url: str
    database_paper_id: str | None = Field(None, description='UUID of the paper in database')
    total_sections: int
    message: str
    sections_preview: list[str] | None = Field(
        None,
        description='List of section titles for preview'
    )

