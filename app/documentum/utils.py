"""
Markdown Rendering Utilities
"""

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.nl2br import Nl2BrExtension


def render_markdown(text):
    """
    Convert Markdown to HTML with GitHub-flavored extensions
    
    Features:
    - Syntax highlighting for code blocks
    - Tables
    - Table of contents
    - Fenced code blocks
    - Auto-convert newlines to <br>
    """
    
    md = markdown.Markdown(
        extensions=[
            FencedCodeExtension(),
            CodeHiliteExtension(
                linenums=False,
                css_class='highlight',
                guess_lang=True
            ),
            TableExtension(),
            TocExtension(
                permalink=True,
                permalink_class='headerlink',
                permalink_title='Link to this section'
            ),
            Nl2BrExtension(),
            'markdown.extensions.extra',
            'markdown.extensions.sane_lists',
        ],
        output_format='html5'
    )
    
    return md.convert(text)


def extract_toc(text):
    """
    Extract table of contents from Markdown
    
    Returns:
        str: HTML table of contents
    """
    md = markdown.Markdown(
        extensions=[
            TocExtension(
                permalink=False,
                baselevel=2
            )
        ]
    )
    md.convert(text)
    return md.toc
