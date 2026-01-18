#!/usr/bin/env python3
"""
Markdown to HTML converter with KaTeX math, Mermaid diagrams, and link redirection support.

Usage:
    python md_to_html.py input.md [-o output.html] [--redirect-base URL]
"""

import argparse
import re
import sys
import yaml
from pathlib import Path
from typing import Union, Optional, IO, Any
from urllib.parse import quote, urlparse

import pydantic
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

StrPath = Union[str, Path]


class MarkdownToHtmlConverterConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid", frozen=False)
    title: Optional[str] = None
    title_from_metadata: bool = True
    title_from_h1: bool = True
    title_from_filename: bool = True
    title_fallback: Optional[str] = None
    redirect_base: Optional[str] = None


class MarkdownToHtmlConverterRuntime():
    md: MarkdownIt
    
    def __init__(self, config: Optional[MarkdownToHtmlConverterConfig] = None, **kwargs):
        if "md" not in kwargs:
            self.md = create_md_parser(
                redirect_base=config.redirect_base if config is not None else None
            )
        else:
            assert isinstance(kwargs['md'], MarkdownIt)
            self.md = kwargs['md']

    def shutdown(self):
        pass


def str_to_bool(value):
    """
    Convert string to boolean. Supports case-insensitive variants:
    True: '1', 'yes', 'true', 'on', 'y', 't'
    False: '0', 'no', 'false', 'off', 'n', 'f'
    
    Args:
        value: String value to convert
    
    Returns:
        Boolean value
    
    Raises:
        ValueError: If the value cannot be parsed as a boolean
    """
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, str):
        value_lower = value.lower().strip()
        if value_lower in ('1', 'yes', 'true', 'on', 'y', 't'):
            return True
        elif value_lower in ('0', 'no', 'false', 'off', 'n', 'f'):
            return False
    raise ValueError(f"Cannot convert '{value}' to boolean")


def extract_yaml_frontmatter(markdown_content: str) -> tuple[dict | None, str]:
    """
    Extract YAML frontmatter from markdown content.
    
    Args:
        markdown_content: The raw markdown content
    
    Returns:
        Tuple of (metadata dict or None, markdown content without frontmatter)
    """
    # Check if content starts with ---
    if not markdown_content.startswith('---\n'):
        return None, markdown_content
    
    # Find the closing ---
    match = re.match(r'^---\n(.*?)\n---\n', markdown_content, re.DOTALL)
    if not match:
        return None, markdown_content
    
    frontmatter_text = match.group(1)
    markdown_without_frontmatter = markdown_content[match.end():]
    
    try:
        metadata = yaml.safe_load(frontmatter_text)
        return metadata, markdown_without_frontmatter
    except yaml.YAMLError:
        return None, markdown_content


def extract_first_h1(html_content: str) -> str | None:
    """
    Extract the text content of the first H1 tag from HTML.
    
    Args:
        html_content: The HTML content to search
    
    Returns:
        The text content of the first H1, or None if not found
    """
    match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
    if match:
        # Remove any HTML tags from the h1 content
        h1_text = re.sub(r'<[^>]+>', '', match.group(1))
        return h1_text.strip()
    return None


def determine_title(
    title: str | None,
    metadata: dict | None,
    html_body: str,
    filename_stem: str,
    title_fallback: str | None,
    title_from_metadata: bool,
    title_from_h1: bool,
    title_from_filename: bool
) -> str:
    """
    Determine the document title based on precedence rules.
    
    Precedence order:
    1. User supplied title (--title)
    2. Title from YAML frontmatter (if --title-from-metadata=1)
    3. First H1 (if --title-from-h1=1)
    4. User supplied fallback title (--title-fallback)
    5. Filename without extension (if --title-from-filename=1)
    6. Empty string
    
    Args:
        title: User supplied title
        metadata: Parsed YAML frontmatter metadata
        html_body: Rendered HTML body content
        filename_stem: Input filename without extension
        title_fallback: User supplied fallback title
        title_from_metadata: Whether to use title from metadata
        title_from_h1: Whether to use first H1 as title
        title_from_filename: Whether to use filename as title
    
    Returns:
        Determined title string
    """
    # 1. User supplied title
    if title:
        return title
    
    # 2. Title from YAML frontmatter
    if title_from_metadata and metadata and 'title' in metadata:
        metadata_title = metadata['title']
        if metadata_title and isinstance(metadata_title, str):
            return metadata_title
    
    # 3. First H1
    if title_from_h1:
        h1_title = extract_first_h1(html_body)
        if h1_title:
            return h1_title
    
    # 4. User supplied fallback title
    if title_fallback:
        return title_fallback
    
    # 5. Filename without extension
    if title_from_filename:
        return filename_stem
    
    # 6. Empty string
    return ""


def create_link_redirect_plugin(redirect_base: str):
    """
    Create a plugin that redirects external links through a specified base URL.
    
    Args:
        redirect_base: Base URL for redirection, e.g., "https://custom.local/redirect?target="
    """
    def link_redirect_plugin(md: MarkdownIt):
        # Store the original link_open renderer
        original_link_open = md.renderer.rules.get("link_open")
        
        def render_link_open(tokens, idx, options, env):
            token = tokens[idx]
            
            # token.attrs is a dictionary in modern markdown-it-py
            if token.attrs and "href" in token.attrs:
                href = token.attrs["href"]
                parsed = urlparse(href)
                
                # Redirect external links (those with a scheme like http/https)
                if parsed.scheme in ("http", "https"):
                    encoded_url = quote(href, safe="")
                    new_href = f"{redirect_base}{encoded_url}"
                    token.attrs["href"] = new_href
            
            # Call original renderer or default
            if original_link_open:
                return original_link_open(tokens, idx, options, env)
            return md.renderer.renderToken(tokens, idx, options, env)
        
        md.renderer.rules["link_open"] = render_link_open
    
    return link_redirect_plugin


def mermaid_plugin(md: MarkdownIt):
    """
    Plugin to render mermaid code blocks as <div class="mermaid"> elements.
    """
    original_fence = md.renderer.rules.get("fence")
    
    def render_fence(tokens, idx, options, env):
        token = tokens[idx]
        info = token.info.strip() if token.info else ""
        
        if info.lower() == "mermaid":
            # Render mermaid code block as a div for mermaid.js to process
            content = token.content
            return f'<div class="mermaid">\n{content}</div>\n'
        
        # Fall back to original fence renderer
        if original_fence:
            return original_fence(tokens, idx, options, env)
        
        # Default fence rendering
        return md.renderer.renderToken(tokens, idx, options, env)
    
    md.renderer.rules["fence"] = render_fence


def create_md_parser(redirect_base: str | None = None) -> MarkdownIt:
    """
    Create and configure the Markdown parser with all plugins.
    
    Args:
        redirect_base: Optional base URL for link redirection.
    
    Returns:
        Configured MarkdownIt instance.
    """
    md = MarkdownIt("commonmark", {"html": True, "typographer": True})
    
    # Enable common extensions
    md.enable("table")
    md.enable("strikethrough")
    
    # Add KaTeX math support via dollarmath plugin
    # Supports $inline$ and $$block$$ math
    md.use(dollarmath_plugin, allow_space=True, allow_digits=True, double_inline=True)
    
    # Add Mermaid diagram support
    md.use(mermaid_plugin)
    
    # Add link redirection if specified
    if redirect_base:
        md.use(create_link_redirect_plugin(redirect_base))
    
    return md

def minify_css(content):
    """
    Minify css but preserve newline for minimal readablity.
    
    :param content: the css content
    """
    # Remove css comments
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    # Remove starting white sapces
    content = re.sub(r"^\s+", "", content, flags=re.MULTILINE)
    return content

def minify_js(content):
    # Remove html comments 
    content = re.sub(r"(?<=[;])?\s*//[^\n]*", "", content, flags=re.MULTILINE)
    # Remove starting white sapces
    content = re.sub(r"^\s+", "", content, flags=re.MULTILINE)
    return content

def minify_html(content):
    # Remove html comments 
    content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
    # Remove starting white sapces
    content = re.sub(r"^\s+", "", content, flags=re.MULTILINE)
    return content

def generate_html_document(body_content: str, title: str = "Document") -> str:
    """
    Wrap the converted markdown body in a complete HTML document with KaTeX and Mermaid assets.
    
    Args:
        body_content: The HTML body content from markdown conversion.
        title: Document title.
    
    Returns:
        Complete HTML document string.
    """
    main_css = '''
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            color: #333;
        }
        
        h1, h2, h3, h4, h5, h6 {
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: 600;
        }
        
        code {
            background-color: #f4f4f4;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 0.9em;
        }
        
        pre {
            background-color: #f4f4f4;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }
        
        pre code {
            background-color: transparent;
            padding: 0;
        }
        
        blockquote {
            border-left: 4px solid #ddd;
            margin-left: 0;
            padding-left: 1em;
            color: #666;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 0.5em;
            text-align: left;
        }
        
        th {
            background-color: #f4f4f4;
        }
        
        img {
            max-width: 100%;
            height: auto;
        }
        
        a {
            color: #0366d6;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        /* KaTeX display math styling */
        .math-display {
            overflow-x: auto;
            padding: 0.5em 0;
        }
        
        /* Mermaid diagram container */
        .mermaid {
            text-align: center;
            margin: 1em 0;
        }\
'''
    main_js = '''
        // Initialize Mermaid
        mermaid.initialize({ startOnLoad: true, theme: 'default' });
        
        // Render KaTeX math
        document.addEventListener("DOMContentLoaded", function() {
            // Render inline math (class="math inline")
            document.querySelectorAll('.math.inline').forEach(function(el) {
                katex.render(el.textContent, el, {
                    throwOnError: false,
                    displayMode: false
                });
            });
            
            // Render display math (class="math block")
            document.querySelectorAll('.math.block').forEach(function(el) {
                katex.render(el.textContent, el, {
                    throwOnError: false,
                    displayMode: true
                });
            });
        });\
    '''
    html_format_str = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <!-- KaTeX CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" crossorigin="anonymous">
    
    <!-- KaTeX JS -->
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" crossorigin="anonymous"></script>
    
    <!-- Mermaid JS -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    
    <style>
        {main_css}
    </style>
</head>
<body>
    {body_content}
    <script>
        {main_js}
    </script>
</body>
</html>'''
    main_css = minify_css(main_css)
    main_js = minify_js(main_js)
    html_format_str = minify_html(html_format_str)
    html_content = html_format_str.format(
        title=title,
        main_css=main_css,
        body_content=body_content,
        main_js=main_js
    )
    return html_content


class MarkdownToHtmlConverter:
    """Converts Markdown files to HTML with embedded resources."""
    Config = MarkdownToHtmlConverterConfig
    Runtime = MarkdownToHtmlConverterRuntime

    def __init__(self, config: MarkdownToHtmlConverterConfig, runtime: Optional[MarkdownToHtmlConverterRuntime] = None):
        self.config = config
        self.runtime = runtime if runtime is not None else self.Runtime(config=config)

    def convert(self, file: Union[StrPath, bytes, IO[bytes]], title: Optional[str]) -> str:
        # Resolve content and filename stem
        markdown_content = ""
        filename_stem = ""

        if isinstance(file, (str, Path)):
            input_path = Path(file)
            markdown_content = input_path.read_text(encoding="utf-8")
            filename_stem = input_path.stem
        elif isinstance(file, bytes):
            markdown_content = file.decode("utf-8")
            filename_stem = "document"
        elif hasattr(file, "read"): # IO[bytes]
             content = file.read()
             if isinstance(content, bytes):
                 markdown_content = content.decode("utf-8")
             else:
                 markdown_content = str(content)
             filename_stem = "document"
        else:
            raise ValueError(f"Unsupported file type: {type(file)}")
        
        # Extract YAML frontmatter
        metadata, markdown_without_frontmatter = extract_yaml_frontmatter(markdown_content)
        
        # Use runtime markdown parser
        html_body = self.runtime.md.render(markdown_without_frontmatter)
        
        # Determine title using config and precedence
        determined_title = determine_title(
            title=title or self.config.title,
            metadata=metadata,
            html_body=html_body,
            filename_stem=filename_stem,
            title_fallback=self.config.title_fallback,
            title_from_metadata=self.config.title_from_metadata,
            title_from_h1=self.config.title_from_h1,
            title_from_filename=self.config.title_from_filename
        )
        
        # Generate complete HTML document
        html_document = generate_html_document(html_body, determined_title)
        return html_document


def convert_markdown_to_html(
    input_path: Path,
    output_path: Path | None = None,
    redirect_base: str | None = None,
    title: str | None = None,
    title_fallback: str | None = None,
    title_from_metadata: bool = True,
    title_from_h1: bool = True,
    title_from_filename: bool = True
) -> Path:
    """
    Legacy wrapper for backward compatibility.
    Convert a markdown file to HTML.
    """
    config = MarkdownToHtmlConverterConfig(
        title=title,
        title_fallback=title_fallback,
        title_from_metadata=title_from_metadata,
        title_from_h1=title_from_h1,
        title_from_filename=title_from_filename,
        redirect_base=redirect_base
    )
    converter = MarkdownToHtmlConverter(config)
    html_content = converter.convert(input_path, title=title)
    
    if output_path is None:
        output_path = input_path.with_suffix(".html")
        
    output_path.write_text(html_content, encoding="utf-8", newline='\n')
    return output_path


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown to HTML with KaTeX math, Mermaid diagrams, and link redirection support.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python md_to_html.py document.md
    python md_to_html.py document.md -o output.html
    python md_to_html.py document.md --redirect-base "https://custom.local/redirect?target="
    python md_to_html.py document.md --title "My Document"
        """
    )
    
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the input Markdown file"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Path to the output HTML file (default: input filename with .html extension)"
    )
    
    parser.add_argument(
        "--redirect-base",
        type=str,
        default=None,
        help="Base URL for redirecting external links (e.g., 'https://custom.local/redirect?target=')"
    )
    
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Document title (highest priority)"
    )
    
    parser.add_argument(
        "--title-fallback",
        type=str,
        default=None,
        help="Fallback document title (used if higher priority sources are unavailable)"
    )
    
    parser.add_argument(
        "--title-from-metadata",
        type=str_to_bool,
        default=True,
        help="Use title from YAML frontmatter (default: 1/true/yes)"
    )
    
    parser.add_argument(
        "--title-from-h1",
        type=str_to_bool,
        default=True,
        help="Use first H1 heading as title (default: 1/true/yes)"
    )
    
    parser.add_argument(
        "--title-from-filename",
        type=str_to_bool,
        default=True,
        help="Use filename (without extension) as title (default: 1/true/yes)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    if not args.input.is_file():
        print(f"Error: Input path is not a file: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Convert
    try:
        config = MarkdownToHtmlConverterConfig(
            title=args.title,
            title_fallback=args.title_fallback,
            title_from_metadata=args.title_from_metadata,
            title_from_h1=args.title_from_h1,
            title_from_filename=args.title_from_filename,
            redirect_base=args.redirect_base
        )
        converter = MarkdownToHtmlConverter(config)
        html_content = converter.convert(args.input, title=args.title)
        
        output_path = args.output
        if output_path is None:
            output_path = args.input.with_suffix(".html")
            
        output_path.write_text(html_content, encoding="utf-8", newline='\n')
        print(f"Successfully converted to: {output_path}")
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
