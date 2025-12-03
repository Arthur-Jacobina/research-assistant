def create_paper(tx, arxiv_id: str, title: str, authors: list, abstract: str = None):
    """Create a paper node in Neo4j."""
    query = """
    MERGE (p:PAPER {arxiv_id: $arxiv_id})
    SET p.title = $title, 
        p.authors = $authors, 
        p.abstract = $abstract,
        p.url = $url
    RETURN p
    """
    result = tx.run(query, 
                    arxiv_id=arxiv_id, 
                    title=title, 
                    authors=authors,
                    abstract=abstract,
                    url=f"https://arxiv.org/abs/{arxiv_id}")
    return result.single()

def create_section(tx, section_id: str, title: str, content: str):
    """Create a section node in Neo4j."""
    query = """
    MERGE (s:SECTION {section_id: $section_id})
    SET s.title = $title, s.content = $content
    RETURN s
    """
    result = tx.run(query, section_id=section_id, title=title, content=content)
    return result.single()

def create_formula(tx, formula_id: str, latex: str):
    """Create a formula node in Neo4j."""
    query = """
    MERGE (f:FORMULA {formula_id: $formula_id})
    SET f.latex = $latex
    RETURN f
    """
    result = tx.run(query, formula_id=formula_id, latex=latex)
    return result.single()

def create_citation(tx, citation_id: str, citation_key: str):
    """Create a citation node in Neo4j."""
    query = """
    MERGE (c:CITATION {citation_id: $citation_id})
    SET c.citation_key = $citation_key
    RETURN c
    """
    result = tx.run(query, citation_id=citation_id, citation_key=citation_key)
    return result.single()

def link_section_to_paper(tx, arxiv_id: str, section_id: str):
    """Link a section to a paper with WITHIN relationship."""
    query = """
    MATCH (p:PAPER {arxiv_id: $arxiv_id})
    MATCH (s:SECTION {section_id: $section_id})
    MERGE (s) - [:WITHIN] -> (p)
    RETURN s
    """
    result = tx.run(query, arxiv_id=arxiv_id, section_id=section_id)
    return result.single()

def link_citation_to_section(tx, citation_id: str, section_id: str):
    """Link a citation to a section with CITED_IN relationship."""
    query = """
    MATCH (c:CITATION {citation_id: $citation_id})
    MATCH (s:SECTION {section_id: $section_id})
    MERGE (c) - [:CITED_IN] -> (s)
    RETURN c
    """
    result = tx.run(query, citation_id=citation_id, section_id=section_id)
    return result.single()

def link_formula_to_section(tx, formula_id: str, section_id: str):
    """Link a formula to a section with USED_IN relationship."""
    query = """
    MATCH (f:FORMULA {formula_id: $formula_id})
    MATCH (s:SECTION {section_id: $section_id})
    MERGE (f) - [:USED_IN] -> (s)
    RETURN f
    """
    result = tx.run(query, formula_id=formula_id, section_id=section_id)
    return result.single()

def link_section_child(tx, parent_section_id: str, child_section_id: str):
    """Link a child section to its parent section with LEFT_CHILD relationship."""
    query = """
    MATCH (parent:SECTION {section_id: $parent_section_id})
    MATCH (child:SECTION {section_id: $child_section_id})
    MERGE (parent) - [:LEFT_CHILD] -> (child)
    RETURN parent, child
    """
    result = tx.run(query, parent_section_id=parent_section_id, child_section_id=child_section_id)
    return result.single()

def link_section_sibling(tx, left_section_id: str, right_section_id: str):
    """Link sibling sections with RIGHT_SIBLING relationship."""
    query = """
    MATCH (left:SECTION {section_id: $left_section_id})
    MATCH (right:SECTION {section_id: $right_section_id})
    MERGE (left) - [:RIGHT_SIBLING] -> (right)
    RETURN left, right
    """
    result = tx.run(query, left_section_id=left_section_id, right_section_id=right_section_id)
    return result.single()