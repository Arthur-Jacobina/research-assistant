import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Chunk:
    """Represents a text chunk with metadata"""
    page_content: str
    metadata: Dict[str, Any]
    
    def __repr__(self):
        return f"Chunk(content_length={len(self.page_content)}, metadata={self.metadata})"


def chunk_paper(markdown_text: str, 
                min_chunk_size: int = 200, 
                max_chunk_size: int = 1500,
                target_chunk_size: int = 1000) -> List[Chunk]:
    """
    Production-ready chunking for research papers.
    
    Splits markdown text by headers, merges small chunks, and splits large chunks.
    Preserves document hierarchy and metadata.
    
    Args:
        markdown_text: The markdown text to chunk
        min_chunk_size: Minimum chunk size in characters (default: 200)
        max_chunk_size: Maximum chunk size in characters (default: 1500)
        target_chunk_size: Target size when splitting large chunks (default: 1000)
    
    Returns:
        List of Chunk objects with content and metadata
    """
    # Split by markdown headers
    chunks = split_by_headers(markdown_text)
    
    # Post-process: merge small chunks, split large ones
    processed_chunks = []
    
    for i, chunk in enumerate(chunks):
        content_length = len(chunk.page_content)
        
        if content_length < min_chunk_size and processed_chunks:
            # Merge with previous chunk
            prev_chunk = processed_chunks[-1]
            prev_chunk.page_content += '\n\n' + chunk.page_content
            # Update metadata to indicate merged content
            if 'merged_from' not in prev_chunk.metadata:
                prev_chunk.metadata['merged_from'] = []
            prev_chunk.metadata['merged_from'].append(chunk.metadata)
            
        elif content_length > max_chunk_size:
            # Split by paragraphs
            sub_chunks = split_by_paragraphs(chunk, max_size=target_chunk_size)
            processed_chunks.extend(sub_chunks)
            
        else:
            processed_chunks.append(chunk)
    
    return processed_chunks


def split_by_headers(markdown_text: str) -> List[Chunk]:
    """
    Split markdown text by headers (h1, h2, h3).
    
    Returns chunks with hierarchical metadata about section structure.
    """
    # Pattern to match headers: # Title, ## Section, ### Subsection
    header_pattern = r'^(#{1,3})\s+(.+?)$'
    
    lines = markdown_text.split('\n')
    chunks = []
    
    current_content = []
    current_metadata = {
        'title': None,
        'section': None,
        'subsection': None,
    }
    
    for line in lines:
        match = re.match(header_pattern, line)
        
        if match:
            # Save previous chunk if it has content
            if current_content:
                content = '\n'.join(current_content).strip()
                if content:
                    chunks.append(Chunk(
                        page_content=content,
                        metadata=current_metadata.copy()
                    ))
                current_content = []
            
            # Update metadata based on header level
            header_level = len(match.group(1))
            header_text = match.group(2).strip()
            
            if header_level == 1:
                current_metadata['title'] = header_text
                current_metadata['section'] = None
                current_metadata['subsection'] = None
            elif header_level == 2:
                current_metadata['section'] = header_text
                current_metadata['subsection'] = None
            elif header_level == 3:
                current_metadata['subsection'] = header_text
            
            # Include the header in the content
            current_content.append(line)
        else:
            current_content.append(line)
    
    # Don't forget the last chunk
    if current_content:
        content = '\n'.join(current_content).strip()
        if content:
            chunks.append(Chunk(
                page_content=content,
                metadata=current_metadata.copy()
            ))
    
    return chunks


def split_by_paragraphs(chunk: Chunk, max_size: int = 1000) -> List[Chunk]:
    """
    Split a large chunk into smaller chunks by paragraphs.
    
    Attempts to keep chunks under max_size while respecting paragraph boundaries.
    """
    text = chunk.page_content
    paragraphs = re.split(r'\n\n+', text)
    
    sub_chunks = []
    current_content = []
    current_size = 0
    
    for para in paragraphs:
        para_size = len(para)
        
        # If a single paragraph is larger than max_size, split by sentences
        if para_size > max_size:
            if current_content:
                # Save current accumulation
                sub_chunks.append(Chunk(
                    page_content='\n\n'.join(current_content),
                    metadata={**chunk.metadata, 'split_method': 'paragraph'}
                ))
                current_content = []
                current_size = 0
            
            # Split the large paragraph by sentences
            sentence_chunks = split_by_sentences(para, max_size)
            for sent_chunk in sentence_chunks:
                sub_chunks.append(Chunk(
                    page_content=sent_chunk,
                    metadata={**chunk.metadata, 'split_method': 'sentence'}
                ))
        
        elif current_size + para_size > max_size and current_content:
            # Save current chunk and start a new one
            sub_chunks.append(Chunk(
                page_content='\n\n'.join(current_content),
                metadata={**chunk.metadata, 'split_method': 'paragraph'}
            ))
            current_content = [para]
            current_size = para_size
        
        else:
            # Add to current chunk
            current_content.append(para)
            current_size += para_size
    
    # Don't forget the last chunk
    if current_content:
        sub_chunks.append(Chunk(
            page_content='\n\n'.join(current_content),
            metadata={**chunk.metadata, 'split_method': 'paragraph'}
        ))
    
    return sub_chunks if sub_chunks else [chunk]


def split_by_sentences(text: str, max_size: int = 1000) -> List[str]:
    """
    Split text by sentences when paragraphs are too large.
    
    Uses a simple sentence boundary detection pattern.
    """
    # Simple sentence splitting (can be improved with nltk/spacy if needed)
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
    sentences = re.split(sentence_pattern, text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence_size = len(sentence)
        
        if current_size + sentence_size > max_size and current_chunk:
            # Save current chunk
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_size = sentence_size
        else:
            current_chunk.append(sentence)
            current_size += sentence_size
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks if chunks else [text]


def get_chunk_statistics(chunks: List[Chunk]) -> Dict[str, Any]:
    """
    Get statistics about the chunks for debugging and optimization.
    """
    sizes = [len(chunk.page_content) for chunk in chunks]
    
    return {
        'total_chunks': len(chunks),
        'min_size': min(sizes) if sizes else 0,
        'max_size': max(sizes) if sizes else 0,
        'avg_size': sum(sizes) / len(sizes) if sizes else 0,
        'total_characters': sum(sizes),
    }


def print_chunk_preview(chunks: List[Chunk], num_chunks: int = 3):
    """
    Print a preview of the first few chunks for debugging.
    """
    for i, chunk in enumerate(chunks[:num_chunks]):
        print(f"\n{'='*60}")
        print(f"Chunk {i+1}")
        print(f"Metadata: {chunk.metadata}")
        print(f"Length: {len(chunk.page_content)} characters")
        print(f"Preview:\n{chunk.page_content[:200]}...")
        print(f"{'='*60}")


# Example usage
if __name__ == "__main__":
    # Test with sample markdown
    sample_text = """
# zELO: ELO-inspired Training Method for Rerankers and Embedding Models

**Authors:** Nicholas PipitoneGhita Houir AlamiAdvaith AvadhanamAnton KaminskyiAshley Khoo

## 1Abstract

We introduce a novel training methodology namedzELO, which optimizes retrieval performance via the analysis that ranking tasks are statically equivalent to a Thurstone model.

## 2Summary of Contributions

### 2.1zELO: A novel Elo-based multi-stage training pipeline

We introduce a novel multi-stage training process inspired by Elo scoring systems.

### 2.2Open-source reranker models released

We release two fully open-weight rerankers trained on thezELOMethod.
"""
    
    chunks = chunk_paper(sample_text)
    print_chunk_preview(chunks)
    print("\nStatistics:", get_chunk_statistics(chunks))

