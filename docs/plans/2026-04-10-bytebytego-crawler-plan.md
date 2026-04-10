# ByteByteGo Course Crawler — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** A Python CLI that crawls ByteByteGo course chapters and saves them locally as HTML + Markdown with downloaded images.

**Architecture:** Single-file CLI (`crawl.py`) that uses `requests` to fetch course pages with cookie auth, `BeautifulSoup` to extract `<article>` content and `__NEXT_DATA__` TOC, downloads images locally, rewrites image paths, and uses `markdownify` for Markdown conversion.

**Tech Stack:** Python 3, requests, beautifulsoup4, markdownify, python-dotenv

---

### Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `crawl.py` (empty placeholder)

**Step 1: Create requirements.txt**

```
requests>=2.31.0
beautifulsoup4>=4.12.0
markdownify>=0.13.0
python-dotenv>=1.0.0
```

**Step 2: Create .gitignore**

```
.env
output/
__pycache__/
*.pyc
.venv/
```

**Step 3: Create .env.example**

```
BYTEBYTEGO_COOKIE=your_cookie_string_here
```

**Step 4: Create empty crawl.py**

```python
"""ByteByteGo course crawler."""
```

**Step 5: Install dependencies**

Run: `cd /Users/peter_j_li/dev/personal/bytebytego-crawler && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

**Step 6: Init git and commit**

Run:
```bash
git init
git add requirements.txt .gitignore .env.example crawl.py
git commit -m "chore: scaffold project with dependencies"
```

---

### Task 2: TOC Fetching — Extract Chapter List from Page

**Files:**
- Modify: `crawl.py`
- Create: `tests/test_toc.py`

**Step 1: Write the failing test**

```python
# tests/test_toc.py
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
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/peter_j_li/dev/personal/bytebytego-crawler && source .venv/bin/activate && python -m pytest tests/test_toc.py -v`
Expected: FAIL — `ImportError: cannot import name 'parse_toc'`

**Step 3: Write minimal implementation**

```python
# crawl.py
"""ByteByteGo course crawler."""

import json

from bs4 import BeautifulSoup


def parse_toc(html: str) -> list[dict] | None:
    """Extract table of contents from __NEXT_DATA__ JSON embedded in page."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script:
        return None
    data = json.loads(script.string)
    return data["props"]["pageProps"]["toc"]
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_toc.py -v`
Expected: 2 passed

**Step 5: Commit**

```bash
git add crawl.py tests/test_toc.py
git commit -m "feat: parse TOC from __NEXT_DATA__ JSON"
```

---

### Task 3: Article Extraction — Extract `<article>` HTML

**Files:**
- Modify: `crawl.py`
- Create: `tests/test_article.py`

**Step 1: Write the failing test**

```python
# tests/test_article.py
from crawl import extract_article

FAKE_HTML = """
<html><body>
<nav>some nav</nav>
<article class="style_learnContent__K5K7M">
  <header><h1>Test Title</h1></header>
  <p>Hello world</p>
  <img src="https://bytebytego.com/_next/image?url=figure-1-1.png&w=1080" />
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
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_article.py -v`
Expected: FAIL — `ImportError: cannot import name 'extract_article'`

**Step 3: Write minimal implementation**

Add to `crawl.py`:

```python
def extract_article(html: str) -> str | None:
    """Extract the <article> inner HTML from the page."""
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article")
    if not article:
        return None
    return article.decode_contents()
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_article.py -v`
Expected: 2 passed

**Step 5: Commit**

```bash
git add crawl.py tests/test_article.py
git commit -m "feat: extract article HTML from page"
```

---

### Task 4: Image Processing — Download Images and Rewrite Paths

**Files:**
- Modify: `crawl.py`
- Create: `tests/test_images.py`

**Step 1: Write the failing test**

```python
# tests/test_images.py
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
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_images.py -v`
Expected: FAIL — `ImportError`

**Step 3: Write minimal implementation**

Add to `crawl.py`:

```python
from urllib.parse import urlparse, parse_qs, unquote
import os
import re


def collect_image_urls(article_html: str) -> list[str]:
    """Extract all image URLs from article HTML."""
    soup = BeautifulSoup(article_html, "html.parser")
    urls = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            urls.append(src)
    return urls


def _filename_from_url(url: str) -> str:
    """Derive a clean filename from a bytebytego image URL."""
    parsed = urlparse(url)
    # Next.js image URLs have the real path in the 'url' query param
    qs = parse_qs(parsed.query)
    if "url" in qs:
        real_path = unquote(qs["url"][0])
        return os.path.basename(real_path)
    # Fallback: use the URL path basename
    return os.path.basename(parsed.path)


def rewrite_image_paths(
    article_html: str, url_map: dict[str, str]
) -> str:
    """Replace image src URLs with local paths using the url_map."""
    soup = BeautifulSoup(article_html, "html.parser")
    for img in soup.find_all("img"):
        src = img.get("src")
        if src and src in url_map:
            img["src"] = url_map[src]
    return soup.decode_contents()
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_images.py -v`
Expected: 2 passed

**Step 5: Commit**

```bash
git add crawl.py tests/test_images.py
git commit -m "feat: collect image URLs and rewrite paths"
```

---

### Task 5: Markdown Conversion

**Files:**
- Modify: `crawl.py`
- Create: `tests/test_markdown.py`

**Step 1: Write the failing test**

```python
# tests/test_markdown.py
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
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_markdown.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Add to `crawl.py`:

```python
from markdownify import markdownify


def html_to_markdown(html: str) -> str:
    """Convert HTML to Markdown."""
    return markdownify(html, heading_style="ATX", strip=["script", "style"])
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_markdown.py -v`
Expected: 2 passed

**Step 5: Commit**

```bash
git add crawl.py tests/test_markdown.py
git commit -m "feat: HTML to Markdown conversion"
```

---

### Task 6: HTTP Client — Page Fetching with Cookie Auth

**Files:**
- Modify: `crawl.py`

**Step 1: Implement fetch functions**

Add to `crawl.py`:

```python
import time
import requests
from dotenv import load_dotenv

BASE_URL = "https://bytebytego.com"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def create_session(cookie: str) -> requests.Session:
    """Create an HTTP session with cookie auth and browser-like headers."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Cookie": cookie,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return session


def fetch_page(session: requests.Session, course: str, chapter: str) -> str | None:
    """Fetch a chapter page. Returns HTML string or None on failure."""
    url = f"{BASE_URL}/courses/{course}/{chapter}"
    for attempt in range(2):
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.text
            print(f"  [WARN] HTTP {resp.status_code} for {chapter}")
            if attempt == 0:
                time.sleep(2)
        except requests.RequestException as e:
            print(f"  [WARN] Request failed for {chapter}: {e}")
            if attempt == 0:
                time.sleep(2)
    return None


def download_image(
    session: requests.Session, url: str, dest: str
) -> bool:
    """Download an image to dest path. Returns True on success."""
    try:
        resp = session.get(url, timeout=30)
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(resp.content)
            return True
        print(f"  [WARN] Image HTTP {resp.status_code}: {url}")
    except requests.RequestException as e:
        print(f"  [WARN] Image download failed: {e}")
    return False
```

**Step 2: Commit**

```bash
git add crawl.py
git commit -m "feat: HTTP client with cookie auth and retry"
```

---

### Task 7: Main CLI — Wire Everything Together

**Files:**
- Modify: `crawl.py`

**Step 1: Implement main function and CLI**

Add to `crawl.py`:

```python
import argparse
import sys


def crawl_chapter(
    session: requests.Session,
    course: str,
    chapter_info: dict,
    output_dir: str,
) -> bool:
    """Crawl a single chapter. Returns True on success."""
    chapter_num = chapter_info["chapter"]
    chapter_id = chapter_info["id"]
    title = chapter_info["title"]
    dir_name = f"{chapter_num:02d}-{chapter_id}"
    chapter_dir = os.path.join(output_dir, dir_name)
    images_dir = os.path.join(chapter_dir, "images")

    print(f"\n[{chapter_num:02d}] {title}")
    print(f"  Fetching {chapter_id}...")

    html = fetch_page(session, course, chapter_id)
    if not html:
        print(f"  [SKIP] Failed to fetch chapter")
        return False

    article_html = extract_article(html)
    if not article_html:
        print(f"  [SKIP] No <article> found — may require paid access")
        return False

    # Download images
    image_urls = collect_image_urls(article_html)
    url_map = {}
    if image_urls:
        os.makedirs(images_dir, exist_ok=True)
        for img_url in image_urls:
            filename = _filename_from_url(img_url)
            local_path = f"images/{filename}"
            dest = os.path.join(chapter_dir, local_path)
            if download_image(session, img_url, dest):
                url_map[img_url] = local_path
                print(f"  Downloaded {filename}")
            time.sleep(0.5)

    # Rewrite image paths and save HTML
    if url_map:
        article_html = rewrite_image_paths(article_html, url_map)

    os.makedirs(chapter_dir, exist_ok=True)

    html_path = os.path.join(chapter_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"<!DOCTYPE html>\n<html><head><meta charset='utf-8'>"
                f"<title>{title}</title></head><body>\n")
        f.write(article_html)
        f.write("\n</body></html>")
    print(f"  Saved {html_path}")

    # Convert to Markdown
    md = html_to_markdown(article_html)
    md_path = os.path.join(chapter_dir, "index.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(md)
    print(f"  Saved {md_path}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Crawl ByteByteGo courses")
    parser.add_argument("course", help="Course slug (e.g. genai-system-design-interview)")
    parser.add_argument("--chapter", help="Crawl only this chapter slug")
    parser.add_argument("--output", default="output", help="Output directory (default: output)")
    args = parser.parse_args()

    load_dotenv()
    cookie = os.environ.get("BYTEBYTEGO_COOKIE", "")
    if not cookie:
        print("[ERROR] BYTEBYTEGO_COOKIE not set in .env")
        sys.exit(1)

    session = create_session(cookie)
    output_dir = os.path.join(args.output, args.course)

    # Fetch TOC from the first chapter (or the specified chapter)
    first_slug = args.chapter or "introduction-and-overview"
    print(f"Fetching table of contents from {first_slug}...")
    html = fetch_page(session, args.course, first_slug)
    if not html:
        print("[ERROR] Failed to fetch initial page")
        sys.exit(1)

    toc = parse_toc(html)
    if not toc:
        print("[ERROR] Could not parse table of contents")
        sys.exit(1)

    print(f"Found {len(toc)} chapters in '{args.course}'")

    # Filter to specific chapter if requested
    if args.chapter:
        toc = [ch for ch in toc if ch["id"] == args.chapter]
        if not toc:
            print(f"[ERROR] Chapter '{args.chapter}' not found")
            sys.exit(1)

    # Crawl each chapter
    success = 0
    for chapter_info in toc:
        if crawl_chapter(session, args.course, chapter_info, output_dir):
            success += 1
        time.sleep(1.5)  # Rate limit between chapters

    print(f"\nDone! {success}/{len(toc)} chapters saved to {output_dir}/")


if __name__ == "__main__":
    main()
```

**Step 2: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All tests pass

**Step 3: Commit**

```bash
git add crawl.py
git commit -m "feat: main CLI wiring all components together"
```

---

### Task 8: Manual Integration Test

**Step 1: Create .env with your cookie**

Add your ByteByteGo cookie to `.env`:
```
BYTEBYTEGO_COOKIE=<your_cookie>
```

**Step 2: Test with a free chapter first**

Run: `python crawl.py genai-system-design-interview --chapter introduction-and-overview`

Expected:
- `output/genai-system-design-interview/01-introduction-and-overview/index.html` created
- `output/genai-system-design-interview/01-introduction-and-overview/index.md` created
- Images downloaded to `images/` subdirectory

**Step 3: Verify output quality**

- Open `index.html` in browser — article should render correctly with images
- Open `index.md` — should be readable Markdown with image references

**Step 4: Run full crawl**

Run: `python crawl.py genai-system-design-interview`

Expected: All 11 chapters downloaded (paid chapters require valid cookie)

**Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete ByteByteGo course crawler"
```
