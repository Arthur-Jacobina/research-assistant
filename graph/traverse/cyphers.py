def find_paper(tx, arxiv_id: str):
    """Find a paper node in Neo4j."""
    query = """
    MATCH (p:PAPER {arxiv_id: $arxiv_id})
    RETURN p
    """
    result = tx.run(query, arxiv_id=arxiv_id)
    return result.single()

def find_section(tx, title: str):
    """Find a section node in Neo4j."""
    query = """
    MATCH (s:SECTION {title: $title})
    RETURN s
    """
    result = tx.run(query, title=title)
    return result.single()

def find_formula(tx, formula_id: str):
    """Find a formula node in Neo4j."""
    query = """
    MATCH (f:FORMULA {formula_id: $formula_id})
    RETURN f
    """
    result = tx.run(query, formula_id=formula_id)
    return result.single()

def find_citation(tx, citation_id: str):
    """Find a citation node in Neo4j."""
    query = """
    MATCH (c:CITATION {citation_id: $citation_id})
    RETURN c
    """
    result = tx.run(query, citation_id=citation_id)
    return result.single()

def find_formula_in_section(tx, formula_id: str, title: str):
    """Find a formula node in a section node in Neo4j."""
    query = """
    MATCH (f:FORMULA {formula_id: $formula_id})
    MATCH (s:SECTION {title: $title})
    MATCH (f) - [:USED_IN] -> (s)
    RETURN f
    """
    result = tx.run(query, formula_id=formula_id, title=title)
    return list(result)

def find_citation_in_section(tx, citation_id: str, title: str):
    """Find a citation node in a section node in Neo4j."""
    query = """
    MATCH (c:CITATION {citation_id: $citation_id})
    MATCH (s:SECTION {title: $title})
    MATCH (c) - [:CITED_IN] -> (s)
    RETURN c
    """
    result = tx.run(query, citation_id=citation_id, title=title)
    return list(result)

def find_sections_in_paper(tx, paper_id: str):
    """Find all section nodes in a paper node in Neo4j."""
    query = """
    MATCH (p:PAPER {arxiv_id: $paper_id})
    MATCH (s:SECTION) - [:WITHIN] -> (p)
    RETURN s
    """
    result = tx.run(query, paper_id=paper_id)
    return list(result)

def find_subsections(tx, title: str):
    """Find all subsection nodes in a section node in Neo4j."""
    query = """
    MATCH (s:SECTION {title: $title})-[:LEFT_CHILD]->(first_child)
    MATCH (first_child)-[:RIGHT_SIBLING*0..]->(subsection)
    RETURN subsection
    """
    result = tx.run(query, title=title)
    return list(result)