from graph.traverse.cyphers import *
from graph.config import driver

def search_paper(arxiv_id: str):
    """Search for a paper node in Neo4j."""
    with driver.session() as session:
        records = session.execute_read(find_paper, arxiv_id)
        return records.data()

def search_section(title: str):
    """Search for a section node in Neo4j."""
    with driver.session() as session:
        records = session.execute_read(find_section, title)
        return records.data()   

def search_formula(formula_id: str):
    """Search for a formula node in Neo4j."""
    with driver.session() as session:
        records = session.execute_read(find_formula, formula_id)
        return records.data()

def search_citation(citation_id: str):
    """Search for a citation node in Neo4j."""
    with driver.session() as session:
        records = session.execute_read(find_citation, citation_id)
        return records.data()

def search_formula_in_section(formula_id: str, title: str):
    """Search for a formula node in a section node in Neo4j."""
    with driver.session() as session:
        records = session.execute_read(find_formula_in_section, formula_id, title)
        return records.data()

def search_citation_in_section(citation_id: str, title: str):
    """Search for a citation node in a section node in Neo4j."""
    with driver.session() as session:
        records = session.execute_read(find_citation_in_section, citation_id, title)
        return records.data()

def search_sections_in_paper(paper_id: str):
    """Search for all section nodes in a paper node in Neo4j."""
    with driver.session() as session:
        records = session.execute_read(find_sections_in_paper, paper_id)
        return [x.data() for x in records]

def search_subsections(title: str):
    """Search for all subsection nodes in a section node in Neo4j."""
    with driver.session() as session:
        records = session.execute_read(find_subsections, title)
        return [x.data() for x in records]