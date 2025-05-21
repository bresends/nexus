#!/usr/bin/env python3
"""
A simple script to test markdown conversion.
"""

from src.utils.markdown_helper import md_to_html

def test_markdown_conversion():
    # Test basic markdown
    test_input = """
# Heading 1

## Heading 2

This is **bold** text and this is *italic* text.

- List item 1
- List item 2
- List item 3

1. Numbered item 1
2. Numbered item 2

[Link to Google](https://www.google.com)

> This is a blockquote

```python
def hello_world():
    print("Hello, world!")
```
    """

    html_output = md_to_html(test_input)
    print("Markdown conversion result:")
    print(html_output)
    print("\nConverted successfully!")

if __name__ == "__main__":
    test_markdown_conversion()
