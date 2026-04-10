from crawl import html_to_markdown


def test_html_to_markdown_basic():
    html = "<h1>Title</h1><p>Hello <strong>world</strong></p>"
    md = html_to_markdown(html)
    assert "# Title" in md
    assert "**world**" in md


def test_html_to_markdown_images():
    html = '<p>See below:</p><img src="images/fig.png" />'
    md = html_to_markdown(html)
    assert "![" in md
    assert "images/fig.png" in md
