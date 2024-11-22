import argparse
import re

from typing import List, Optional
from datetime import datetime
from pathlib import Path

from sql import Database, Paper


class MarkdownExporter:
    def __init__(self, db: Database):
        self.db = db

    def generate_markdown(self, papers: List[Paper], title: str = "Research Paper Summaries") -> str:
        """Generate markdown content from a list of papers."""
        # Sort papers by title
        papers = sorted(papers, key=lambda x: x.title.lower())
        
        md_content = f"# {title}\n\n"
        md_content += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by [PubSummarizer](https://github.com/Logan-Lin/PubSummarizer)*\n\n"

        for paper in papers:
            md_content += self._format_paper(paper)

        return md_content

    def _format_paper(self, paper: Paper) -> str:
        """Format a single paper into markdown."""
        md_text = f"## {paper.title}\n\n"
        
        if paper.summary:
            # Split summary into topics and main summary
            clean_summary = paper.summary.replace('**', '').replace('__', '')
            
            # Extract topics, TL;DR, and summary sections
            sections = clean_summary.split('[')
            for section in sections:
                section_lower = section.lower()
                if section_lower.startswith('topics:]'):
                    topics = re.sub(r'(?i)Topics:]', '', section).strip()
                    md_text += "### Topics\n\n"
                    md_text += f"{topics}\n\n"
                elif section_lower.startswith('tl;dr:]'):
                    tldr = re.sub(r'(?i)TL;DR:]', '', section).strip()
                    md_text += "### TL;DR\n\n"
                    md_text += f"{tldr}\n\n"
                elif section_lower.startswith('summary:]'):
                    summary = re.sub(r'(?i)Summary:]', '', section).strip()
                    md_text += "### Summary\n\n"
                    md_text += f"{summary}\n\n"

        if paper.pdf_url:
            md_text += f"**Paper URL**: [{paper.pdf_url}]({paper.pdf_url})\n\n"
        
        md_text += "---\n\n"
        return md_text

    def export_to_file(self, output_path: str, filters: Optional[dict] = None, title: str = "Research Paper Summaries") -> None:
        """
        Export papers from database to a markdown file.
        
        Args:
            output_path: Path where the markdown file will be saved
            filters: Optional filters to apply when querying papers
            title: Custom title for the markdown document
        """
        papers = self.db.get_papers(filters)
        
        if not papers:
            raise ValueError("No papers found in the database with the given filters")

        # Generate markdown content with custom title
        md_content = self.generate_markdown(papers, title)

        # Ensure the output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)


class ObsidianExporter:
    def __init__(self, db: Database):
        self.db = db

    def generate_markdown(self, papers: List[Paper], title: str = "Research Paper Summaries") -> str:
        """Generate Obsidian-style markdown content from a list of papers."""
        # Sort papers by title
        papers = sorted(papers, key=lambda x: x.title.lower())

        md_content = "---\n"
        md_content += f"title: {title}\n"
        md_content += "---\n\n"

        md_content += f"*Generated by [PubSummarizer](https://github.com/Insights-Ac/PubSummarizer)*\n\n"

        for paper in papers:
            md_content += self._format_paper(paper)

        return md_content

    def _format_paper(self, paper: Paper) -> str:
        """Format a single paper into Obsidian-style markdown."""
        # Main content
        md_text = "---\n\n"

        md_text += f"### {paper.title}\n\n"
        
        if paper.summary:
            # Split summary into topics and main summary
            clean_summary = paper.summary.replace('**', '').replace('__', '')

            # Process each section
            sections = clean_summary.split('[')
            for section in sections:
                section_lower = section.lower()
                if section_lower.startswith('topics:]'):
                    topics = re.sub(r'(?i)Topics:]', '', section).strip()
                    topic_list = [t.strip() for t in topics.split(',')]
                    md_text += "**Topics:** "
                    topic_tags = []
                    for topic in topic_list:
                        topic_clean = topic.replace(' ', '-').replace('\'', '')
                        topic_tags.append(f"#{topic_clean.lower()}")
                    md_text += ", ".join(topic_tags) + "\n\n"
                elif section_lower.startswith('tl;dr:]'):
                    tldr = re.sub(r'(?i)TL;DR:]', '', section).strip()
                    md_text += "#### TL;DR\n\n"
                    md_text += f"{tldr}\n\n"
                elif section_lower.startswith('summary:]'):
                    summary = re.sub(r'(?i)Summary:]', '', section).strip()
                    md_text += "#### Summary\n\n"
                    md_text += f"{summary}\n\n"

        if paper.pdf_url:
            md_text += f"📄 [Paper Link]({paper.pdf_url})\n\n"
        
        return md_text

    def export_to_file(self, output_path: str, filters: Optional[dict] = None, title: str = "Research Paper Summaries") -> None:
        """
        Export papers from database to an Obsidian-style markdown file.
        
        Args:
            output_path: Path where the markdown file will be saved
            filters: Optional filters to apply when querying papers
            title: Custom title for the markdown document
        """
        papers = self.db.get_papers(filters)
        
        if not papers:
            raise ValueError("No papers found in the database with the given filters")

        md_content = self.generate_markdown(papers, title)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)


class WebExporter:
    def __init__(self, db: Database):
        self.db = db
        
    def generate_html(self, papers: List[Paper], title: str = "Research Paper Summaries") -> str:
        """Generate HTML content from a list of papers."""
        # Sort papers by title
        papers = sorted(papers, key=lambda x: x.title.lower())
        
        # Convert papers to JSON-friendly format
        papers_data = []
        for paper in papers:
            paper_dict = {
                "title": paper.title,
                "pdf_url": paper.pdf_url,
                "topics": [],
                "tldr": "",
                "summary": ""
            }
            
            if paper.summary:
                clean_summary = paper.summary.replace('**', '').replace('__', '')
                sections = clean_summary.split('[')
                
                for section in sections:
                    section_lower = section.lower()
                    if section_lower.startswith('topics:]'):
                        topics = re.sub(r'(?i)Topics:]', '', section).strip()
                        paper_dict["topics"] = [t.strip() for t in topics.split(',')]
                    elif section_lower.startswith('tl;dr:]'):
                        paper_dict["tldr"] = re.sub(r'(?i)TL;DR:]', '', section).strip()
                    elif section_lower.startswith('summary:]'):
                        paper_dict["summary"] = re.sub(r'(?i)Summary:]', '', section).strip()
            
            papers_data.append(paper_dict)

        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PubSummarizer - {title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://unpkg.com/masonry-layout@4/dist/masonry.pkgd.min.js"></script>
    <style>
        .filter-controls {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }}
        @media (max-width: 991px) {{
            .search-box {{
                margin-bottom: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container py-4">
        <h1 class="mb-4">{title}</h1>
        <p class="text-muted"><em>Generated by <a href="https://github.com/Logan-Lin/PubSummarizer">PubSummarizer</a></em></p>
        
        <div class="filter-controls">
            <div class="d-flex flex-md-row flex-column gap-3">
                <div class="flex-grow-1">
                    <input type="text" class="form-control search-box" id="searchInput" 
                           placeholder="Search in titles, topics, TL;DR, and summaries...">
                </div>
                <div class="btn-group" role="group" aria-label="Section toggles">
                    <input type="checkbox" class="btn-check" id="showTopics" checked autocomplete="off">
                    <label class="btn btn-outline-primary" for="showTopics">Topics</label>

                    <input type="checkbox" class="btn-check" id="showTldr" checked autocomplete="off">
                    <label class="btn btn-outline-primary" for="showTldr">TL;DR</label>

                    <input type="checkbox" class="btn-check" id="showSummary" checked autocomplete="off">
                    <label class="btn btn-outline-primary" for="showSummary">Summary</label>
                </div>
            </div>
        </div>

        <div id="papers-container" class="row" data-masonry='{{"percentPosition": true }}'></div>
    </div>

    <script>
        // Store papers data
        const papersData = {papers_json};
        
        // Function to filter papers based on search input
        function filterPapers(searchText) {{
            if (!searchText) return papersData;
            
            searchText = searchText.toLowerCase();
            return papersData.filter(paper => {{
                const titleMatch = paper.title.toLowerCase().includes(searchText);
                const topicsMatch = paper.topics.some(topic => 
                    topic.toLowerCase().includes(searchText)
                );
                const tldrMatch = paper.tldr.toLowerCase().includes(searchText);
                const summaryMatch = paper.summary.toLowerCase().includes(searchText);
                
                return titleMatch || topicsMatch || tldrMatch || summaryMatch;
            }});
        }}
        
        // Function to create paper card HTML
        function createPaperCard(paper) {{
            const showTopics = document.getElementById('showTopics').checked;
            const showTldr = document.getElementById('showTldr').checked;
            const showSummary = document.getElementById('showSummary').checked;

            const topicsHtml = (showTopics && paper.topics.length > 0)
                ? `<div class="mb-3">
                     <div class="d-flex gap-2 flex-wrap">
                       ${{paper.topics.map(topic => `<span class="badge text-bg-info">${{topic}}</span>`).join('')}}
                     </div>
                   </div>`
                : '';
                
            const tldrHtml = (showTldr && paper.tldr)
                ? `<div class="mb-3">
                     <h3 class="h5">TL;DR</h3>
                     <p class="card-text">${{paper.tldr}}</p>
                   </div>`
                : '';
                
            const summaryHtml = (showSummary && paper.summary)
                ? `<div class="mb-3">
                     <h3 class="h5">Summary</h3>
                     <p class="card-text">${{paper.summary}}</p>
                   </div>`
                : '';
                
            const urlHtml = paper.pdf_url
                ? `<p class="card-text"><a href="${{paper.pdf_url}}" class="btn btn-outline-primary btn-sm">Download Paper</a></p>`
                : '';
                
            return `
                <div class="col-sm-12 col-lg-6 col-xl-4 mb-4">
                    <div class="card shadow-sm">
                        <div class="card-body">
                            <h3 class="card-title h4">${{paper.title}}</h3>
                            ${{topicsHtml}}
                            ${{tldrHtml}}
                            ${{summaryHtml}}
                            ${{urlHtml}}
                        </div>
                    </div>
                </div>
            `;
        }}

        // Render papers
        function renderPapers() {{
            const searchText = document.getElementById('searchInput').value;
            const filteredPapers = filterPapers(searchText);
            
            const container = document.getElementById('papers-container');
            container.innerHTML = filteredPapers.map(createPaperCard).join('');
            
            // Initialize Masonry layout
            new Masonry(container, {{
                percentPosition: true
            }});
        }}

        // Add event listeners
        document.getElementById('searchInput').addEventListener('input', renderPapers);
        document.getElementById('showTopics').addEventListener('change', renderPapers);
        document.getElementById('showTldr').addEventListener('change', renderPapers);
        document.getElementById('showSummary').addEventListener('change', renderPapers);

        // Render papers when page loads
        document.addEventListener('DOMContentLoaded', renderPapers);
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
        import json
        return html_content.format(
            title=title,
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            papers_json=json.dumps(papers_data)
        )

    def export_to_file(self, output_path: str, filters: Optional[dict] = None, title: str = "Research Paper Summaries") -> None:
        """
        Export papers from database to an HTML file.
        
        Args:
            output_path: Path where the HTML file will be saved
            filters: Optional filters to apply when querying papers
            title: Custom title for the HTML page
        """
        papers = self.db.get_papers(filters)
        
        if not papers:
            raise ValueError("No papers found in the database with the given filters")

        html_content = self.generate_html(papers, title)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)


def export_papers(db_url: str, output_path: str, format: str = 'markdown', filters: Optional[dict] = None, title: str = "Research Paper Summaries") -> None:
    """
    Convenience function to export papers from a database to either markdown, Obsidian, or HTML format.
    
    Args:
        db_url: Database URL to connect to
        output_path: Path where the output file will be saved
        format: Output format - either 'markdown', 'obsidian', or 'html' (default: 'markdown')
        filters: Optional filters to apply when querying papers
        title: Custom title for the output document
    """
    db = Database(db_url)
    
    if format.lower() == 'markdown':
        exporter = MarkdownExporter(db)
    elif format.lower() == 'obsidian':
        exporter = ObsidianExporter(db)
    elif format.lower() == 'html':
        exporter = WebExporter(db)
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'markdown', 'obsidian', or 'html'")
        
    exporter.export_to_file(output_path, filters, title)
    print(f"Exported papers to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export papers from a database")
    parser.add_argument("--db_url", type=str, required=True, help="Database URL")
    parser.add_argument("--output_path", type=str, required=True, help="Output path for the file")
    parser.add_argument("--format", type=str, choices=['markdown', 'obsidian', 'html'], default='markdown', 
                      help="Output format (markdown, obsidian, or html)")
    parser.add_argument("--filters", type=dict, help="Filters to apply when querying papers", default={})
    parser.add_argument("--title", type=str, default="Research Paper Summaries",
                      help="Custom title for the output document")
    args = parser.parse_args()

    export_papers(args.db_url, args.output_path, args.format, args.filters, args.title)
