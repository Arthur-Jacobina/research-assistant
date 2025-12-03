"""
Neo4j operations for ingesting papers into the graph database.

Database schema:
    labels:
        :PAPER
        :SECTION
        :FORMULA
        :CITATION
    Relationships:
        (:SECTION) - [:WITHIN] -> (:PAPER) # root section to be the first section
        (:CITATION) - [:CITED_IN] -> (:SECTION)
        (:FORMULA) - [:USED_IN] -> (:SECTION)
        (:SECTION) - [:LEFT_CHILD] -> (:SECTION) # parent to child relationship
        (:SECTION) - [:RIGHT_SIBLING] -> (:SECTION) # sibling relationship
"""
from graph.insert.cyphers import *
from graph.config import driver

def insert_paper(arxiv_id: str, title: str, authors: list, abstract: str = None):
    """Insert a paper node into Neo4j."""
    with driver.session() as session:
        return session.execute_write(create_paper, arxiv_id, title, authors, abstract)

def insert_section(section_id: str, title: str, content: str):
    """Insert a section node into Neo4j."""
    with driver.session() as session:
        return session.execute_write(create_section, section_id, title, content)

def insert_formula(formula_id: str, latex: str):
    """Insert a formula node into Neo4j."""
    with driver.session() as session:
        return session.execute_write(create_formula, formula_id, latex)

def insert_citation(citation_id: str, citation_key: str):
    """Insert a citation node into Neo4j."""
    with driver.session() as session:
        return session.execute_write(create_citation, citation_id, citation_key)

def link_section_within_paper(arxiv_id: str, section_id: str):
    """Link a section to a paper with WITHIN relationship."""
    with driver.session() as session:
        return session.execute_write(link_section_to_paper, arxiv_id, section_id)

def link_citation_in_section(citation_id: str, section_id: str):
    """Link a citation to a section with CITED_IN relationship."""
    with driver.session() as session:
        return session.execute_write(link_citation_to_section, citation_id, section_id)

def link_formula_in_section(formula_id: str, section_id: str):
    """Link a formula to a section with USED_IN relationship."""
    with driver.session() as session:
        return session.execute_write(link_formula_to_section, formula_id, section_id)

def link_child_to_parent(parent_section_id: str, child_section_id: str):
    """Link a child section to its parent section with LEFT_CHILD relationship."""
    with driver.session() as session:
        return session.execute_write(link_section_child, parent_section_id, child_section_id)

def link_siblings(left_section_id: str, right_section_id: str):
    """Link sibling sections with RIGHT_SIBLING relationship."""
    with driver.session() as session:
        return session.execute_write(link_section_sibling, left_section_id, right_section_id)