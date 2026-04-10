"""ByteByteGo course crawler."""

import argparse
import json
import os
import sys
import time
from urllib.parse import urlparse, parse_qs, unquote

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from markdownify import markdownify
import requests


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


def download_image(session: requests.Session, url: str, dest: str) -> bool:
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
