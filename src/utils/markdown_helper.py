import markdown
import bleach
from markupsafe import Markup

def md_to_html(text):
    """
    Convert markdown text to safe HTML

    Args:
        text: Markdown text to convert

    Returns:
        Markup: Safe HTML markup that can be rendered in templates
    """
    if not text:
        return Markup("")

    # Convert markdown to HTML
    html = markdown.markdown(
        text,
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists',
        ]
    )

    # Define allowed tags and attributes for security
    allowed_tags = [
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'br',
        'ul', 'ol', 'li', 'strong', 'em', 'a', 'pre', 'code',
        'blockquote', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'img', 'span', 'div', 'strike', 'del'
    ]

    allowed_attrs = {
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        '*': ['class', 'style']
    }

    # Sanitize the HTML for security
    clean_html = bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )

    # Return as a Markup object so Jinja knows it's safe HTML
    return Markup(clean_html)
