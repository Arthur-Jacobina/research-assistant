import re
from typing import List, Dict, Optional

from ingestion.arxiv.read import read_paper

#TODO: PARSE FORMULAS
def extract_abstract(main_text: str) -> Optional[str]:
    """Extract the abstract from the main LaTeX file."""
    abstract_match = re.search(
        r"\\begin\{abstract\}(.*?)\\end\{abstract\}", 
        main_text, 
        re.DOTALL
    )
    if abstract_match:
        return abstract_match.group(1).strip()
    return None


def extract_balanced_braces(text: str, start_pos: int) -> Optional[str]:
    """Extract content within balanced braces starting from start_pos."""
    if start_pos >= len(text) or text[start_pos] != '{':
        return None
    
    stack = []
    for i in range(start_pos, len(text)):
        if text[i] == '{':
            stack.append(i)
        elif text[i] == '}':
            stack.pop()
            if not stack:
                return text[start_pos + 1:i]
    
    return None


def extract_title(main_text: str) -> Optional[str]:
    """Extract the paper title from the main LaTeX file."""
    title_start = re.search(r"\\title\s*\{", main_text)
    if title_start:
        brace_pos = title_start.end() - 1
        title = extract_balanced_braces(main_text, brace_pos)
        
        if title:
            title = re.sub(r"\\vspace\*?\{[^}]*\}", "", title)
            title = re.sub(r"\\hspace\*?\{[^}]*\}", "", title)
            title = clean_latex_text(title)
            title = re.sub(r"\s+", " ", title)
            return title.strip()
    return None


def extract_authors(main_text: str) -> List[str]:
    """Extract author names from the main LaTeX file."""
    author_start = re.search(r"\\author\s*\{", main_text)
    if author_start:
        brace_pos = author_start.end() - 1
        authors_text = extract_balanced_braces(main_text, brace_pos)
        
        if authors_text:
            authors_text = re.sub(r"\\textsuperscript\{[^}]*\}", "", authors_text)
            authors_text = re.sub(r"\\textsubscript\{[^}]*\}", "", authors_text)
            authors_text = re.sub(r"\\textit\{[^}]*\}", "", authors_text)
            
            ieee_authors = re.findall(r"\\IEEEauthorblockN\{([^}]+)\}", authors_text)
            if ieee_authors:
                authors_text = " ".join(ieee_authors)
            
            authors_text = re.sub(r"\\(?:and|thanks|footnote)\{[^}]*\}", "", authors_text)
            authors_text = re.sub(r"\\\\", ",", authors_text)
            authors_text = re.sub(r"%.*$", "", authors_text, flags=re.MULTILINE)  # Remove comments
            authors = [a.strip() for a in authors_text.split(",") if a.strip() and len(a.strip()) > 2]
            authors = [a for a in authors if not any(x in a.lower() for x in ["university", "institute", "department", "equal"])]
            return authors
    return []

def clean_latex_text(text):
    """Clean LaTeX commands from text while preserving content."""
    text = re.sub(r"\\label\{[^}]*\}", "", text)
    text = re.sub(r"\\cite\{[^}]*\}", "", text)
    text = re.sub(r"\\ref\{[^}]*\}", "", text)
    text = re.sub(r"\\textsuperscript\{[^}]*\}", "", text)
    text = re.sub(r"\\textsubscript\{[^}]*\}", "", text)
    # Remove common formatting commands but keep their content
    text = re.sub(r"\\textbf\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textit\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\emph\{([^}]*)\}", r"\1", text)
    return text.strip()

def find_subsections(text):
    """Extract subsections from a section body."""
    subsection_pattern = r"\\subsection\{([^}]*)\}(.*?)(?=\\subsection\{|$)"
    matches = re.findall(subsection_pattern, text, re.DOTALL)
    
    subsections = []
    for title, body in matches:
        clean_title = clean_latex_text(title)
        subsections.append({
            "title": clean_title,
            "body": body.strip()
        })
    
    return subsections

def find_sections(tex):
    """Extract all sections with their titles and bodies from LaTeX text."""
    section_pattern = r"\\section\{([^}]*)\}(.*?)(?=\\section\{|$)"
    matches = re.findall(section_pattern, tex, re.DOTALL)
    
    sections = []
    for title, body in matches:
        clean_title = clean_latex_text(title)
        
        if not clean_title or clean_title.strip() == "":
            if "\\subsection" not in body and "\\subsubsection" not in body:
                continue
            clean_title = "[Untitled Section]"
        
        subsections = find_subsections(body)
        
        if subsections:
            intro_pattern = r"^(.*?)\\subsection\{"
            intro_match = re.search(intro_pattern, body, re.DOTALL)
            intro_text = intro_match.group(1).strip() if intro_match else ""
        else:
            intro_text = body.strip()
        
        sections.append({
            "title": clean_title,
            "intro": intro_text,
            "subsections": subsections,
            "full_body": body.strip()
        })
    
    return sections

def extract_citations(text: str) -> List[str]:
    """Extract all citation keys from the text."""
    citations = re.findall(r"\\cite\{([^}]+)\}", text)
    all_citations = []
    for cite in citations:
        all_citations.extend([c.strip() for c in cite.split(",")])
    return list(set(all_citations))


def parse_paper(paper_path: str) -> Dict:
    """
    Parse an ArXiv paper and extract structured information.
    
    Args:
        paper_path: Path to the extracted LaTeX paper directory
        
    Returns:
        Dictionary containing parsed paper structure with:
        - title: Paper title
        - abstract: Paper abstract
        - authors: List of authors
        - sections: List of parsed sections with subsections
        - all_citations: List of all citation keys used
    """
    all_tex_texts = read_paper(paper_path)

    title, abstract, authors = None, None, None

    for tex_text in all_tex_texts:
        if title is None:
            title = extract_title(tex_text)
        if abstract is None:
            abstract = extract_abstract(tex_text)
        if authors is None:
            authors = extract_authors(tex_text)

    all_sections = []
    all_citations = set()
    
    for tex_text in all_tex_texts:
        parsed_sections = find_sections(tex_text)
        for section in parsed_sections:
            citations = extract_citations(section["full_body"])
            all_citations.update(citations)
            all_sections.append(section)

    return {
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "sections": all_sections,
        "all_citations": sorted(list(all_citations)),
        "num_sections": len(all_sections)
    }