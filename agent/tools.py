from typing import Optional

from database.qdrant import get_paper
from arxiv_parser.parser import ArxivParser
from database.qdrant import insert_paper

def get_paper_text(url: str, query: Optional[str] = None) -> str:
    """Get the text of a paper from a url."""
    paper = get_paper(url, query)
    if paper is not None:
        return paper["markdown"]
    else:
        parser = ArxivParser(url)
        markdown = parser.parse_url_to_markdown(url)
        insert_paper(url, markdown)
        return markdown