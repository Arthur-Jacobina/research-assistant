import os
import tempfile
import tarfile

from arxiv import (
    Client as ArxivClient,
    Search,
)

def _normalize_paper_id(paper_id: str) -> str:
    return paper_id.replace("arxiv:", "").strip()

def download_paper(paper_id: str) -> tuple[str, str, str]:
    """
    Download the LaTeX source of an arXiv paper to a temporary directory.
    
    Args:
        paper_id: The arXiv paper ID (e.g., "2301.07041")
    
    Returns:
        Tuple[str, str, str]: (temp_dir, extracted_source_dir, paper_title)
    """
    try:    
        paper = next(ArxivClient().results(Search(id_list=[_normalize_paper_id(paper_id)])))

        temp_dir = tempfile.mkdtemp(prefix="arxiv_latex_")
        
        source_path = paper.download_source(dirpath=temp_dir, filename=f"{paper_id}_source.tar.gz")
        
        extract_subdir = os.path.join(temp_dir, paper_id)
        os.makedirs(extract_subdir, exist_ok=True)
        
        with tarfile.open(source_path, 'r:gz') as tar:
            tar.extractall(path=extract_subdir, filter='data')
        
        with tarfile.open(source_path, 'r') as tar:
            tar.extractall(path=extract_subdir, filter='data')
        
        os.remove(source_path)

    except Exception as e:
        raise ValueError(f"Error downloading paper: {e!s}")
    else:
        return temp_dir, extract_subdir, paper.title

if __name__ == "__main__":
    temp_dir, extract_subdir, paper_title = download_arxiv_source("2304.08467")
    print(f"Downloaded paper to {temp_dir}")
    print(f"Extracted source to {extract_subdir}")
    print(f"Paper title: {paper_title}")