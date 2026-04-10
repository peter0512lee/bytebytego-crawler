from crawl import collect_image_urls, rewrite_image_paths

ARTICLE_HTML = """
<header><h1>Test</h1></header>
<p>Text before</p>
<img src="https://bytebytego.com/_next/image?url=%2Fcourse-images%2Fgenai%2Ffigure-1-1.png&amp;w=1080&amp;q=75" />
<p>Text middle</p>
<img src="https://bytebytego.com/_next/image?url=%2Fcourse-images%2Fgenai%2Ffigure-1-2.jpg&amp;w=1080&amp;q=75" />
<p>Text after</p>
"""


def test_collect_image_urls():
    urls = collect_image_urls(ARTICLE_HTML)
    assert len(urls) == 2
    assert "figure-1-1.png" in urls[0]
    assert "figure-1-2.jpg" in urls[1]


def test_rewrite_image_paths():
    url_map = {
        "https://bytebytego.com/_next/image?url=%2Fcourse-images%2Fgenai%2Ffigure-1-1.png&w=1080&q=75": "images/figure-1-1.png",
        "https://bytebytego.com/_next/image?url=%2Fcourse-images%2Fgenai%2Ffigure-1-2.jpg&w=1080&q=75": "images/figure-1-2.jpg",
    }
    result = rewrite_image_paths(ARTICLE_HTML, url_map)
    assert 'src="images/figure-1-1.png"' in result
    assert 'src="images/figure-1-2.jpg"' in result
    assert "bytebytego.com" not in result
