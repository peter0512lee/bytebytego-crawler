"""ByteByteGo course crawler."""

import json
import os
from urllib.parse import urlparse, parse_qs, unquote

from bs4 import BeautifulSoup
from markdownify import markdownify


def parse_toc(html: str) -> list[dict] | None:
    """Extract table of contents from __NEXT_DATA__ JSON embedded in page."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script:
        return None
    data = json.loads(script.string)
    return data["props"]["pageProps"]["toc"]


def extract_article(html: str) -> str | None:
    """Extract the <article> inner HTML from the page."""
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article")
    if not article:
        return None
    return article.decode_contents()


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
    qs = parse_qs(parsed.query)
    if "url" in qs:
        real_path = unquote(qs["url"][0])
        return os.path.basename(real_path)
    return os.path.basename(parsed.path)


def rewrite_image_paths(article_html: str, url_map: dict[str, str]) -> str:
    """Replace image src URLs with local paths using the url_map."""
    soup = BeautifulSoup(article_html, "html.parser")
    for img in soup.find_all("img"):
        src = img.get("src")
        if src and src in url_map:
            img["src"] = url_map[src]
    return soup.decode_contents()


def html_to_markdown(html: str) -> str:
    """Convert HTML to Markdown."""
    return markdownify(html, heading_style="ATX", strip=["script", "style"])
