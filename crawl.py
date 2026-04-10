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
