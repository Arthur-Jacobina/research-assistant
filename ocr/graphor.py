from typing import Dict, List, Any, Optional
from ocr.utils import graphor_fetch


def upload_document(file_path: str) -> dict:
    """
    Upload a document to GraphorLM for processing.
    """
    with open(file_path, "rb") as f:
        return graphor_fetch("upload", files={"file": f})


def process_document(file_name: str, partition_method: str = "mai") -> dict:
    """
    Process an uploaded document using specified partition method.
    """
    return graphor_fetch("process", json={
        "file_name": file_name,
        "partition_method": partition_method
    })


def list_elements(
    file_name: str,
    page: int = 1,
    page_size: int = 20,
    filter_options: Optional[Dict[str, Any]] = None
) -> dict:
    """List elements from a document.
    """
    payload = {
        "file_name": file_name,
        "page": page,
        "page_size": page_size,
        "filter": filter_options or {}
    }
    
    return graphor_fetch("elements", json=payload, timeout=30)


def get_all_elements(
    file_name: str,
    filter_options: Optional[Dict[str, Any]] = None,
    page_size: int = 100
) -> List[Dict[str, Any]]:
    """
    Retrieve all elements from a document by paginating through all pages.
    """
    all_elements = []
    page = 1
    
    while True:
        response = list_elements(file_name, page, page_size, filter_options)
        all_elements.extend(response['items'])
        
        if page >= response['total_pages']:
            break
        page += 1
    
    return all_elements


def extract_tables(file_name: str) -> List[Dict[str, Any]]:
    """
    Extract all tables from a document.
    """
    elements = get_all_elements(file_name, filter_options={"type": "Table"})
    
    return [
        {
            "content": item['page_content'],
            "page": item['metadata']['page_number'],
            "position": item['metadata']['position'],
            "html": item['metadata'].get('text_as_html', ''),
            "bounding_box": item['metadata'].get('bounding_box')
        }
        for item in elements
    ]


def extract_by_type(
    file_name: str,
    element_type: str
) -> List[Dict[str, Any]]:
    """
    Extract all elements of a specific type from a document.
    """
    elements = get_all_elements(file_name, filter_options={"type": element_type})
    
    return [
        {
            "content": item['page_content'],
            "page": item['metadata']['page_number'],
            "type": item['metadata']['element_type'],
            "position": item['metadata']['position'],
            "html": item['metadata'].get('text_as_html', ''),
            "bounding_box": item['metadata'].get('bounding_box')
        }
        for item in elements
    ]


def get_document_structure(file_name: str) -> Dict[str, Any]:
    """
    Get a hierarchical structure analysis of the document.
    """
    titles = extract_by_type(file_name, "Title")
    content_elements = get_all_elements(
        file_name,
        filter_options={"elementsToRemove": ["Footer", "PageNumber"]}
    )
    
    type_counts = {}
    total_chars = 0
    page_numbers = set()
    
    for element in content_elements:
        element_type = element['metadata']['element_type']
        type_counts[element_type] = type_counts.get(element_type, 0) + 1
        total_chars += len(element['page_content'])
        page_numbers.add(element['metadata']['page_number'])
    
    return {
        "outline": [
            {
                "title": title['content'],
                "page": title['page'],
                "level": _detect_heading_level(title.get('html', ''))
            }
            for title in titles
        ],
        "content_summary": {
            "element_distribution": type_counts,
            "total_characters": total_chars,
            "average_element_length": total_chars / len(content_elements) if content_elements else 0
        },
        "total_elements": len(content_elements),
        "pages": sorted(page_numbers)
    }

def _detect_heading_level(html: str) -> int:
    """
    Detect heading level from HTML tags.
    """
    if '<h1>' in html:
        return 1
    elif '<h2>' in html:
        return 2
    elif '<h3>' in html:
        return 3
    elif '<h4>' in html:
        return 4
    else:
        return 5


def extract_sections(file_name: str) -> List[Dict[str, Any]]:
    """
    Break down the document into sections based on titles.
    Each section contains content between one title and the next.
    Images are handled with separate description and base64 fields.
    
    Returns:
        List of sections, each with:
        - section_number: int
        - title: str (empty for sections before the first title)
        - content: List of content elements
        - images: List of image objects with description and base64 separate
    """
    # Get all elements sorted by position
    all_elements = get_all_elements(
        file_name,
        filter_options={"elementsToRemove": ["Footer", "PageNumber"]}
    )
    
    # Sort by page number and position
    all_elements.sort(key=lambda x: (
        x['metadata']['page_number'],
        x['metadata']['position']
    ))
    
    sections = []
    current_section = {
        "title": "",
        "content": [],
        "images": []
    }
    section_number = 1
    
    for element in all_elements:
        element_type = element['metadata']['element_type']
        
        if element_type == "Title":
            # Save current section if it has content
            if current_section["content"] or current_section["images"]:
                sections.append({
                    "section_number": section_number,
                    **current_section
                })
                section_number += 1
            
            # Start new section with this title
            current_section = {
                "title": element['page_content'],
                "content": [],
                "images": []
            }
        
        elif element_type == "Image":
            # Handle images separately with description and base64
            image_data = {
                "description": element['page_content'],  # Description text
                "base64": element['metadata'].get('image_base64', ''),  # Base64 data
                "page": element['metadata']['page_number'],
                "position": element['metadata']['position'],
                "bounding_box": element['metadata'].get('bounding_box')
            }
            current_section["images"].append(image_data)
        
        else:
            # Regular content element
            content_item = {
                "type": element_type,
                "text": element['page_content'],
                "page": element['metadata']['page_number'],
                "position": element['metadata']['position']
            }
            current_section["content"].append(content_item)
    
    # Add the last section
    if current_section["content"] or current_section["images"]:
        sections.append({
            "section_number": section_number,
            **current_section
        })
    
    return sections
