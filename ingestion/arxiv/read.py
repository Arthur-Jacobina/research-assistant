import os
from pathlib import Path
import traceback

def read_paper(paper_path: str) -> str:
    try:        
        all_tex_files = list(Path(paper_path).rglob("*.tex"))
        all_tex_texts = []
        for file in all_tex_files:
            with open(file, "r") as f:
                text = f.read()
                all_tex_texts.append(text)
    
    except Exception as e:
        raise Exception(f"Error reading paper: {e!s} {traceback.format_exc()}")
    else:
        return all_tex_texts