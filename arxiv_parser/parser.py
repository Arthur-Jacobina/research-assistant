from bs4 import BeautifulSoup
import requests
from typing import List, Optional
import re
from arxiv_parser.utils import MarkdownCleaner

class ArxivParser:
    """Parser for converting ArXiv HTML papers to Markdown format."""
    
    def __init__(self, url: str):
        """Initialize parser with ArXiv paper URL."""
        self.url = url
        self.soup = self._fetch_and_parse(url)
        self.markdown_lines: List[str] = []
    
    # ===== Data Fetching Layer =====
    
    def _fetch_and_parse(self, url: str) -> BeautifulSoup:
        """Fetch HTML from URL and parse it with BeautifulSoup."""
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    
    # ===== Element Extraction Layer =====
    
    def _extract_title(self) -> Optional[str]:
        """Extract paper title from HTML."""
        title = self.soup.find('h1', class_='ltx_title_document')
        return title.get_text(strip=True) if title else None
    
    def _extract_authors(self) -> Optional[str]:
        """Extract authors from HTML."""
        authors_div = self.soup.find('div', class_='ltx_authors')
        return authors_div.get_text(strip=True) if authors_div else None
    
    def _extract_abstract(self) -> Optional[str]:
        """Extract abstract from HTML."""
        abstract_div = self.soup.find('div', class_='ltx_abstract')
        return abstract_div.get_text(strip=True) if abstract_div else None
    
    def _extract_sections(self) -> List:
        """Extract all main sections from HTML."""
        return self.soup.find_all('section', class_='ltx_section')
    
    def _extract_bibliography(self) -> Optional:
        """Extract bibliography section from HTML."""
        return self.soup.find('section', class_='ltx_bibliography')
    
    # ===== Markdown Formatting Layer =====
    
    def _format_title(self, title: str) -> None:
        """Format and append title to markdown."""
        self.markdown_lines.append(f"# {title}\n")
    
    def _format_authors(self, authors: str) -> None:
        """Format and append authors to markdown."""
        self.markdown_lines.append(f"**Authors:** {authors}\n")
    
    def _format_abstract(self, abstract: str) -> None:
        """Format and append abstract to markdown."""
        self.markdown_lines.append("## Abstract\n")
        self.markdown_lines.append(f"{abstract}\n")
    
    def _format_section_title(self, section_title: str) -> None:
        """Format and append section title to markdown."""
        self.markdown_lines.append(f"\n## {section_title}\n")
    
    def _format_subsection_title(self, subsection_title: str) -> None:
        """Format and append subsection title to markdown."""
        self.markdown_lines.append(f"\n### {subsection_title}\n")
    
    def _format_paragraph(self, paragraph_text: str) -> None:
        """Format and append paragraph to markdown."""
        if paragraph_text:
            self.markdown_lines.append(f"{paragraph_text}\n")
    
    def _format_table(self, table_element) -> None:
        """Format and append table to markdown."""
        caption = table_element.find('figcaption')
        if caption:
            self.markdown_lines.append(f"\n**{caption.get_text(strip=True)}**\n")
        
        table_elem = table_element.find('table')
        if table_elem:
            self.markdown_lines.append("\n| Table content |\n|---|\n")
    
    def _format_figure(self, figure_element) -> None:
        """Format and append figure to markdown."""
        caption = figure_element.find('figcaption')
        if caption:
            self.markdown_lines.append(f"\n**{caption.get_text(strip=True)}**\n")
        
        img = figure_element.find('img')
        if img and img.get('src'):
            self.markdown_lines.append(f"![Figure]({img['src']})\n")
    
    def _format_bibliography_item(self, bib_item_text: str) -> None:
        """Format and append bibliography item to markdown."""
        # Remove reference numbers like [1]
        cleaned_text = re.sub(r'^\[\d+\]', '', bib_item_text)
        self.markdown_lines.append(f"- {cleaned_text}\n")
    
    # ===== Content Processing Layer =====
    
    def _should_skip_paragraph(self, paragraph) -> bool:
        """Check if paragraph should be skipped (contains headers)."""
        return bool(paragraph.find(['h2', 'h3', 'h4']))
    
    def _process_paragraphs(self, paragraphs: List, skip_headers: bool = True) -> None:
        """Process and format a list of paragraphs."""
        for para in paragraphs:
            if skip_headers and self._should_skip_paragraph(para):
                continue
            para_text = para.get_text(strip=True)
            self._format_paragraph(para_text)
    
    def _process_tables(self, tables: List) -> None:
        """Process and format a list of tables."""
        for table in tables:
            self._format_table(table)
    
    def _process_figures(self, figures: List) -> None:
        """Process and format a list of figures."""
        for figure in figures:
            self._format_figure(figure)
    
    def _process_subsection(self, subsection) -> None:
        """Process a single subsection with its content."""
        # Extract and format subsection title
        subsection_title = subsection.find('h3', class_='ltx_title_subsection')
        if subsection_title:
            self._format_subsection_title(subsection_title.get_text(strip=True))
        
        # Process paragraphs within subsection
        paragraphs = subsection.find_all('div', class_='ltx_para')
        self._process_paragraphs(paragraphs)
    
    def _process_section_content(self, section) -> None:
        """Process content of a section (paragraphs, tables, figures)."""
        # Check for subsections
        subsections = section.find_all('section', class_='ltx_subsection')
        
        if subsections:
            for subsection in subsections:
                self._process_subsection(subsection)
        else:
            # Process paragraphs directly under section
            paragraphs = section.find_all('div', class_='ltx_para', recursive=False)
            self._process_paragraphs(paragraphs)
        
        # Process tables in section
        tables = section.find_all('figure', class_='ltx_table')
        self._process_tables(tables)
        
        # Process figures in section
        figures = section.find_all('figure', class_='ltx_figure')
        self._process_figures(figures)
    
    def _process_section(self, section) -> None:
        """Process a single section with its title and content."""
        # Extract and format section title
        section_title = section.find('h2', class_='ltx_title_section')
        if section_title:
            self._format_section_title(section_title.get_text(strip=True))
        else:
            # Fallback to getting text from section
            title_text = section.get_text(strip=True).split('\n')[0] if section else ""
            if title_text:
                self._format_section_title(title_text)
        
        # Process section content
        self._process_section_content(section)
    
    # ===== Main Parsing Orchestration =====
    
    def _parse_metadata(self) -> None:
        """Parse and format paper metadata (title, authors, abstract)."""
        title = self._extract_title()
        if title:
            self._format_title(title)
        
        authors = self._extract_authors()
        if authors:
            self._format_authors(authors)
        
        abstract = self._extract_abstract()
        if abstract:
            self._format_abstract(abstract)
    
    def _parse_sections(self) -> None:
        """Parse and format all sections of the paper."""
        sections = self._extract_sections()
        for section in sections:
            self._process_section(section)
    
    def _parse_bibliography(self) -> None:
        """Parse and format bibliography/references."""
        bibliography = self._extract_bibliography()
        if not bibliography:
            return
        
        self.markdown_lines.append("\n## References\n")
        bib_items = bibliography.find_all('li', class_='ltx_bibitem')
        
        for item in bib_items:
            ref_text = item.get_text(strip=True)
            self._format_bibliography_item(ref_text)
    
    def _parse_paper(self) -> str:
        """
        Main entry point: Parse entire paper and return markdown.
        
        Returns:
            str: Complete paper in markdown format
        """
        self.markdown_lines = []  # Reset markdown lines
        
        # Parse in logical order
        self._parse_metadata()
        self._parse_sections()
        self._parse_bibliography()
        
        return '\n'.join(self.markdown_lines)

    def parse_url_to_markdown(self, url: str, clean: bool = True) -> str:
        """
        Parse ArXiv paper from URL to markdown.
        
        Args:
            url: ArXiv HTML URL
            clean: Whether to clean the markdown output
            
        Returns:
            str: Markdown formatted paper
        """
        markdown = self._parse_paper()
        
        if clean:
            markdown = MarkdownCleaner.clean(markdown)
        
        return markdown
    
    def parse_and_save(self, url: str, output_path: str) -> None:
        """
        Parse ArXiv paper and save to file.
        
        Args:
            url: ArXiv HTML URL
            output_path: Path to save markdown file
        """
        markdown = self.parse_url_to_markdown(url)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"Conversion complete! Markdown saved to: {output_path}")

