import json
from crawl import parse_toc

FAKE_HTML = """
<html>
<head></head>
<body>
<script id="__NEXT_DATA__" type="application/json">
{
  "props": {
    "pageProps": {
      "toc": [
        {"course": "test-course", "id": "chapter-one", "chapter": 1, "title": "Chapter One", "free": true},
        {"course": "test-course", "id": "chapter-two", "chapter": 2, "title": "Chapter Two"}
      ]
    }
  }
}
</script>
</body>
</html>
"""


def test_parse_toc_extracts_chapters():
    toc = parse_toc(FAKE_HTML)
    assert len(toc) == 2
    assert toc[0]["id"] == "chapter-one"
    assert toc[0]["chapter"] == 1
    assert toc[0]["title"] == "Chapter One"
    assert toc[1]["id"] == "chapter-two"


def test_parse_toc_missing_next_data():
    toc = parse_toc("<html><body></body></html>")
    assert toc is None
