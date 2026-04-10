from crawl import extract_article

FAKE_HTML = """
<html><body>
<nav>some nav</nav>
<article class="style_learnContent__K5K7M">
  <header><h1>Test Title</h1></header>
  <p>Hello world</p>
  <img src="https://bytebytego.com/_next/image?url=figure-1-1.png&amp;w=1080" />
</article>
<footer>some footer</footer>
</body></html>
"""


def test_extract_article_returns_html():
    html = extract_article(FAKE_HTML)
    assert "<h1>Test Title</h1>" in html
    assert "<p>Hello world</p>" in html
    assert "some nav" not in html
    assert "some footer" not in html


def test_extract_article_no_article_tag():
    result = extract_article("<html><body><p>no article</p></body></html>")
    assert result is None
