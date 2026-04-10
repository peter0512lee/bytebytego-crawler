"""ByteByteGo course crawler.

Uses Playwright to render pages (content is client-side rendered via MDX/JSX),
then extracts the <article> HTML from the DOM.
"""

import argparse
import json
import os
import sys
import time
from urllib.parse import parse_qs, unquote, urlparse

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from markdownify import markdownify
from playwright.sync_api import sync_playwright


def parse_toc(html: str) -> list[dict] | None:
    """Extract table of contents from __NEXT_DATA__ JSON embedded in page."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script:
        return None
    data = json.loads(script.string)
    page_props = data["props"]["pageProps"]
    return page_props.get("toc")


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


def _parse_cookie_string(cookie_str: str) -> list[dict]:
    """Parse a cookie header string into Playwright cookie objects."""
    cookies = []
    for pair in cookie_str.split(";"):
        pair = pair.strip()
        if "=" in pair:
            name, value = pair.split("=", 1)
            cookies.append({
                "name": name.strip(),
                "value": value.strip(),
                "domain": ".bytebytego.com",
                "path": "/",
            })
    return cookies


def fetch_rendered_page(context, course: str, chapter: str | None = None) -> tuple[str | None, str | None]:
    """Fetch a chapter page using Playwright, wait for article to render.

    Returns (page_source_html, rendered_article_html) tuple.
    page_source_html is used for TOC parsing, rendered_article_html for content.
    If chapter is None, navigates to the course index (which redirects to default chapter).
    """
    if chapter:
        url = f"{BASE_URL}/courses/{course}/{chapter}"
    else:
        url = f"{BASE_URL}/courses/{course}"
    page = context.new_page()
    try:
        page.goto(url, wait_until="networkidle", timeout=60000)
        # Wait for article to render
        try:
            page.wait_for_selector("article", timeout=15000)
        except Exception:
            # Article might not render (e.g. paywall redirect)
            source = page.content()
            return source, None

        source = page.content()
        article_html = page.evaluate("""
            () => {
                const article = document.querySelector('article');
                return article ? article.innerHTML : null;
            }
        """)
        return source, article_html
    except Exception as e:
        print(f"  [WARN] Playwright error for {chapter}: {e}")
        return None, None
    finally:
        page.close()


def download_image_playwright(context, url: str, dest: str) -> bool:
    """Download an image using Playwright's request context."""
    try:
        response = context.request.get(url, timeout=30000)
        if response.ok:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(response.body())
            return True
        print(f"  [WARN] Image HTTP {response.status}: {url}")
    except Exception as e:
        print(f"  [WARN] Image download failed: {e}")
    return False


def crawl_chapter(
    context,
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

    _source, article_html = fetch_rendered_page(context, course, chapter_id)
    if not article_html:
        print(f"  [SKIP] No <article> found — may require paid access")
        return False

    # Download images
    image_urls = collect_image_urls(article_html)
    url_map = {}
    if image_urls:
        os.makedirs(images_dir, exist_ok=True)
        for img_url in image_urls:
            # Resolve relative URLs
            if img_url.startswith("/"):
                full_url = f"{BASE_URL}{img_url}"
            else:
                full_url = img_url
            filename = _filename_from_url(full_url)
            local_path = f"images/{filename}"
            dest = os.path.join(chapter_dir, local_path)
            if download_image_playwright(context, full_url, dest):
                url_map[img_url] = local_path
                print(f"  Downloaded {filename}")
            time.sleep(0.3)

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

    cookies = _parse_cookie_string(cookie)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
        )
        context.add_cookies(cookies)

        output_dir = os.path.join(args.output, args.course)

        # Fetch TOC by navigating to course index (redirects to default chapter)
        print(f"Fetching table of contents for '{args.course}'...")
        source, _article = fetch_rendered_page(context, args.course)
        if not source:
            print("[ERROR] Failed to fetch initial page")
            browser.close()
            sys.exit(1)

        toc = parse_toc(source)
        if not toc:
            print("[ERROR] Could not parse table of contents")
            browser.close()
            sys.exit(1)

        print(f"Found {len(toc)} chapters in '{args.course}'")

        # Filter to specific chapter if requested
        if args.chapter:
            toc = [ch for ch in toc if ch["id"] == args.chapter]
            if not toc:
                print(f"[ERROR] Chapter '{args.chapter}' not found")
                browser.close()
                sys.exit(1)

        # If we already fetched the first chapter's article, use it
        if args.chapter and _article:
            # We already have it, save directly
            success = 0
            if crawl_chapter(context, args.course, toc[0], output_dir):
                success = 1
        else:
            # Crawl each chapter
            success = 0
            for chapter_info in toc:
                if crawl_chapter(context, args.course, chapter_info, output_dir):
                    success += 1
                time.sleep(1.5)  # Rate limit between chapters

        browser.close()

    print(f"\nDone! {success}/{len(toc)} chapters saved to {output_dir}/")


if __name__ == "__main__":
    main()
