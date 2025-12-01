"""LaTeX parser for arXiv papers - extracts sections, content, and figures from LaTeX source."""

import os
import re
import shutil
import tarfile
import tempfile

from pathlib import Path

import arxiv


def download_arxiv_source(paper_id: str) -> tuple[str, str, str]:
    """Download the LaTeX source of an arXiv paper to a temporary directory.

    Args:
        paper_id: The arXiv paper ID (e.g., "2301.07041")

    Returns:
        Tuple[str, str, str]: (temp_dir, extracted_source_dir, paper_title)
    """
    # Clean paper ID
    paper_id = paper_id.replace('arxiv:', '').strip()

    # Search for the paper
    search = arxiv.Search(id_list=[paper_id])

    try:
        paper = next(arxiv.Client().results(search))
    except StopIteration:
        raise ValueError(f'Paper with ID {paper_id} not found on arXiv')

    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix='arxiv_latex_')

    # Download the source
    source_path = paper.download_source(dirpath=temp_dir, filename=f'{paper_id}_source.tar.gz')

    # Extract the tarball
    extract_subdir = os.path.join(temp_dir, paper_id)
    os.makedirs(extract_subdir, exist_ok=True)

    try:
        with tarfile.open(source_path, 'r:gz') as tar:
            tar.extractall(path=extract_subdir, filter='data')
    except tarfile.ReadError:
        # Sometimes the file is not gzipped, try without compression
        with tarfile.open(source_path, 'r') as tar:
            tar.extractall(path=extract_subdir, filter='data')

    # Clean up the tarball
    os.remove(source_path)

    return temp_dir, extract_subdir, paper.title


def find_main_tex_file(source_dir: str) -> str | None:
    """Find the main LaTeX file in the source directory."""
    tex_files = list(Path(source_dir).rglob('*.tex'))

    if not tex_files:
        return None

    # Look for files with \documentclass or \begin{document}
    for tex_file in tex_files:
        try:
            with open(tex_file, encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if r'\documentclass' in content or r'\begin{document}' in content:
                    return str(tex_file)
        except:
            continue

    # If no main file found, return the first .tex file
    return str(tex_files[0]) if tex_files else None


def resolve_input_files(tex_content: str, base_dir: str, visited: set | None = None) -> str:
    r"""Recursively resolve and inline all \\input{} commands in LaTeX content."""
    if visited is None:
        visited = set()

    input_pattern = r'\\input\{([^}]+)\}'

    def replace_input(match):
        filename = match.group(1).strip()

        if not filename.endswith('.tex'):
            filename += '.tex'

        full_path = os.path.join(base_dir, filename)

        if full_path in visited:
            return f'% Circular reference to {filename}'

        if os.path.exists(full_path):
            visited.add(full_path)
            try:
                with open(full_path, encoding='utf-8', errors='ignore') as f:
                    included_content = f.read()
                    return resolve_input_files(included_content, os.path.dirname(full_path), visited)
            except Exception as e:
                return f'% Error reading {filename}: {e}'
        else:
            return f'% File not found: {filename}'

    return re.sub(input_pattern, replace_input, tex_content)


def extract_title(tex_content: str) -> str | None:
    """Extract paper title from LaTeX."""
    title_pattern = r'\\title\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    match = re.search(title_pattern, tex_content, re.DOTALL)

    if match:
        title = match.group(1).strip()
        # For titles, we do want to clean LaTeX formatting commands
        # but preserve mathematical content
        title = re.sub(r'\\textbf\{([^}]+)\}', r'\1', title)
        title = re.sub(r'\\textit\{([^}]+)\}', r'\1', title)
        title = re.sub(r'\\emph\{([^}]+)\}', r'\1', title)
        title = re.sub(r'\\text[a-z]{2}\{([^}]+)\}', r'\1', title)
        title = re.sub(r'\s+', ' ', title)
        return title.strip()

    return None


def extract_abstract(tex_content: str) -> str | None:
    """Extract abstract content from LaTeX."""
    abstract_pattern = r'\\begin\{abstract\}(.*?)\\end\{abstract\}'
    match = re.search(abstract_pattern, tex_content, re.DOTALL | re.IGNORECASE)

    if match:
        abstract = match.group(1).strip()
        # Keep raw LaTeX for KaTeX rendering
        # Only remove comments
        abstract = re.sub(r'(?m)^%.*$', '', abstract)  # Remove comment lines
        abstract = re.sub(r'(?m)\s*%.*$', '', abstract)  # Remove inline comments
        abstract = re.sub(r'\n\s*\n\s*\n+', '\n\n', abstract)  # Remove excessive blank lines
        return abstract.strip()

    return None


def parse_latex_sections(tex_content: str) -> list[dict]:
    """Parse LaTeX content to extract sections and their content."""
    sections = []
    current_section_num = 0
    in_appendix = False
    appendix_section_num = 0

    section_pattern = r'\\[Ss]ection\*?\s*\{([^}]*)\}'
    subsection_pattern = r'\\[Ss]ubsection\*?\s*\{([^}]+)\}'
    appendix_pattern = r'\\appendices'

    lines = tex_content.split('\n')

    for i, line in enumerate(lines):
        if re.search(appendix_pattern, line, re.IGNORECASE):
            in_appendix = True
            continue

        section_match = re.search(section_pattern, line, re.IGNORECASE)
        subsection_match = re.search(subsection_pattern, line, re.IGNORECASE)

        if section_match:
            title = section_match.group(1).strip()

            if in_appendix:
                appendix_section_num += 1
                if not title:
                    title = f'Appendix {chr(64 + appendix_section_num)}'
                else:
                    # Clean only formatting commands, preserve math
                    title = re.sub(r'\\textbf\{([^}]+)\}', r'\1', title)
                    title = re.sub(r'\\textit\{([^}]+)\}', r'\1', title)
                    title = re.sub(r'\\emph\{([^}]+)\}', r'\1', title)
                    title = f'Appendix {chr(64 + appendix_section_num)}: {title}'

                section_num = f'A{appendix_section_num}'
            else:
                current_section_num += 1
                section_num = current_section_num

                # Clean only formatting commands, preserve math
                title = re.sub(r'\\textbf\{([^}]+)\}', r'\1', title)
                title = re.sub(r'\\textit\{([^}]+)\}', r'\1', title)
                title = re.sub(r'\\emph\{([^}]+)\}', r'\1', title)

                if not title:
                    title = 'Untitled Section'

            current_section = {
                'number': section_num,
                'title': title,
                'type': 'section',
                'figures': [],
                'line': i,
                'line_start': i,
                'is_appendix': in_appendix
            }
            sections.append(current_section)
        elif subsection_match:
            title = subsection_match.group(1).strip()
            # Clean only formatting commands, preserve math
            title = re.sub(r'\\textbf\{([^}]+)\}', r'\1', title)
            title = re.sub(r'\\textit\{([^}]+)\}', r'\1', title)
            title = re.sub(r'\\emph\{([^}]+)\}', r'\1', title)

            parent_num = section_num if in_appendix else current_section_num
            subsection_num = len([s for s in sections if s.get('parent') == parent_num]) + 1

            subsection = {
                'number': f'{parent_num}.{subsection_num}',
                'title': title,
                'type': 'subsection',
                'parent': parent_num,
                'figures': [],
                'line': i,
                'line_start': i,
                'is_appendix': in_appendix
            }
            sections.append(subsection)

    # Extract content for each section
    lines_list = tex_content.split('\n')
    for idx, section in enumerate(sections):
        if section['type'] == 'section':
            start_line = section['line_start'] + 1

            end_line = len(lines_list)
            for next_section in sections[idx + 1:]:
                if next_section['type'] == 'section':
                    end_line = next_section['line_start']
                    break

            content_lines = lines_list[start_line:end_line]
            content = '\n'.join(content_lines)

            # Keep raw LaTeX content for KaTeX rendering
            # Only do minimal cleanup: remove comments and excessive whitespace
            content_cleaned = re.sub(r'(?m)^%.*$', '', content)  # Remove comment lines
            content_cleaned = re.sub(r'(?m)\s*%.*$', '', content_cleaned)  # Remove inline comments
            content_cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', content_cleaned)  # Remove excessive blank lines
            content_cleaned = content_cleaned.strip()

            section['content'] = content_cleaned

    return sections


def parse_arxiv_latex(paper_id: str) -> dict:
    """Download and parse an arXiv paper's LaTeX source.

    Args:
        paper_id: arXiv paper ID (e.g., "2301.07041")

    Returns:
        Dictionary with paper data including sections and content
    """
    temp_dir = None

    try:
        # Download and extract source
        temp_dir, source_dir, arxiv_title = download_arxiv_source(paper_id)

        # Find main .tex file
        main_tex_file = find_main_tex_file(source_dir)

        if not main_tex_file:
            raise ValueError('Could not find main LaTeX file')

        # Read LaTeX content
        with open(main_tex_file, encoding='utf-8', errors='ignore') as f:
            original_content = f.read()

        # Extract title from LaTeX (fallback to arXiv title)
        paper_title = extract_title(original_content)
        if not paper_title:
            paper_title = arxiv_title

        # Resolve all \input{} commands
        base_dir = os.path.dirname(main_tex_file)
        tex_content = resolve_input_files(original_content, base_dir)

        # Extract abstract
        abstract = extract_abstract(tex_content)

        # Parse sections
        sections = parse_latex_sections(tex_content)

        # Filter to main sections only (skip appendix)
        main_sections = [s for s in sections if s['type'] == 'section' and not s.get('is_appendix', False)]

        # Prepare result
        result = {
            'paper_id': paper_id,
            'title': paper_title,
            'arxiv_url': f'https://arxiv.org/abs/{paper_id}',
            'abstract': abstract,
            'total_sections': len(main_sections),
            'sections': []
        }

        # Add abstract as section 0
        if abstract:
            result['sections'].append({
                'section_number': 0,
                'title': 'Abstract',
                'content': abstract
            })

        # Add main sections
        for section in main_sections:
            result['sections'].append({
                'section_number': section['number'],
                'title': section['title'],
                'content': section.get('content', '')
            })

        return result

    finally:
        # Cleanup temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

