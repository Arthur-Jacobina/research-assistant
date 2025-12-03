from ingestion.arxiv.download import *
from ingestion.arxiv.parse import *
from graph.insert.operations import *

#TODO: FORMULAS AND CITATIONS
def ingest_paper(paper_id: str):
    """
    Ingest a paper into Neo4j with a tree-like graph structure.
    """
    temp_dir, paper_path, paper_title = download_paper(paper_id)
    paper = parse_paper(paper_path)
    
    insert_paper(
        arxiv_id=paper_id,
        title=paper['title'],
        authors=paper['authors'] or [],
        abstract=paper['abstract']
    )
    
    sections = paper["sections"]
    
    if not sections:
        raise ValueError("No sections found in paper")
        return
    
    for idx, section in enumerate(sections):
        section_id = f"{paper_id}_section_{idx}"
        section['_id'] = section_id
        
        insert_section(
            section_id=section_id,
            title=section['title'],
            content=section.get('intro', '') or section.get('full_body', '')
        )
        
        if idx == 0:
            link_section_within_paper(paper_id, section_id)
        
        if idx > 0:
            link_section_within_paper(paper_id, section_id)
            prev_section_id = sections[idx - 1]['_id']
            link_siblings(prev_section_id, section_id)
        
        subsections = section.get('subsections', [])
        for sub_idx, subsection in enumerate(subsections):
            subsection_id = f"{section_id}_subsection_{sub_idx}"
            subsection['_id'] = subsection_id
            
            insert_section(
                section_id=subsection_id,
                title=subsection['title'],
                content=subsection.get('body', '')
            )
            
            if sub_idx == 0:
                link_child_to_parent(section_id, subsection_id)
            
            if sub_idx > 0:
                prev_subsection_id = subsections[sub_idx - 1]['_id']
                link_siblings(prev_subsection_id, subsection_id)
    

if __name__ == "__main__":
    ingest_paper("2508.15144")