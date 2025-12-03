import os

from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()

url: str = os.environ.get('SUPABASE_URL')
key: str = os.environ.get('SUPABASE_ANON_KEY')

supabase: Client = create_client(url, key)

def insert_paper(paper_id: str, title: str, arxiv_url: str):
    """Insert a paper record into the database.
    Returns the inserted paper data including the database ID.
    """
    try:
        response = supabase.table('papers').insert({
            'arxiv_id': paper_id,
            'title': title,
            'url': arxiv_url
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f'Error inserting paper: {e}')
        return None

def insert_sections(paper_db_id: str, sections: list):
    """Insert multiple sections for a paper.
    Each section should have: section_number, title, content, images.

    Args:
        paper_db_id: UUID string of the paper
        sections: List of section dictionaries
    """
    try:
        sections_data = []
        for section in sections:
            sections_data.append({
                'paper_id': paper_db_id,
                'section_number': section['section_number'],
                'title': section['title'],
                'content': section['content'],  # Store as JSON
                'images': section['images']  # Store as JSON
            })

        response = supabase.table('sections').insert(sections_data).execute()
        return response.data
    except Exception as e:
        print(f'Error inserting sections: {e}')
        return None

def get_paper(url: str):
    try:
        response = supabase.table('papers').select('*').eq('url', url).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f'Error getting paper: {e}')
        return None

def get_paper_by_arxiv_id(arxiv_id: str):
    """Get a paper by arXiv ID."""
    try:
        response = supabase.table('papers').select('*').eq('arxiv_id', arxiv_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f'Error getting paper by arXiv ID: {e}')
        return None


def delete_paper_sections(paper_db_id: str) -> bool | None:
    """Delete all sections for a paper."""
    try:
        supabase.table('sections').delete().eq('paper_id', paper_db_id).execute()
        return True
    except Exception as e:
        print(f'Error deleting sections: {e}')
        return False


def get_paper_with_sections(arxiv_id: str):
    """Get a paper and all its sections by arXiv ID."""
    try:
        # Get paper
        paper_response = supabase.table('papers').select('*').eq('arxiv_id', arxiv_id).execute()
        if not paper_response.data:
            return None

        paper = paper_response.data[0]

        # Get sections
        sections_response = supabase.table('sections').select('*').eq('paper_id', paper['id']).order('section_number').execute()
        paper['sections'] = sections_response.data if sections_response.data else []

        return paper
    except Exception as e:
        print(f'Error getting paper with sections: {e}')
        return None
