from graph.traverse.operations import *

def get_paper(paper_id: str) -> str:
    """Get the text of a paper from a paper id."""
    paper = search_paper(paper_id)
    return paper['p']['title'], paper['p']['abstract'], paper['p']['authors']

def get_sections(paper_id: str) -> list[str]:
    """Get the sections of a paper from a paper id."""
    sections = search_sections_in_paper(paper_id)
    return [section['s']['title'] for section in sections]

def get_section(title: str) -> str:
    """Get the text of a section from a section id."""
    section = search_section(title)
    return section['s']['content']

def get_subsections(title: str) -> list[str]:
    """Get the subsections from a section"""
    subsections = search_subsections(title)
    return [subsection['subsection']['title'] for subsection in subsections]