# ByteByteGo Course Crawler — Design

## Goal

A CLI tool to crawl ByteByteGo course articles and save them locally as HTML + Markdown with images.

## Target Site Analysis

- **Tech stack**: Next.js (SSR)
- **Content location**: Each chapter page embeds full article in `<article>` HTML tag
- **Table of contents**: Available in `__NEXT_DATA__` JSON → `pageProps.toc`
- **Authentication**: Cookie-based; free chapters (1-2) accessible without auth, paid chapters (3+) require a valid session cookie
- **URL pattern**: `https://bytebytego.com/courses/{course-slug}/{chapter-slug}`

## Architecture

### Output Structure

```
output/
└── {course-slug}/
    ├── 01-introduction-and-overview/
    │   ├── index.html
    │   ├── index.md
    │   └── images/
    │       ├── figure-1-1.png
    │       └── ...
    ├── 02-gmail-smart-compose/
    │   ├── index.html
    │   ├── index.md
    │   └── images/
    └── ...
```

### Data Flow

1. CLI receives course slug (e.g. `genai-system-design-interview`)
2. Fetch first chapter page with Cookie header
3. Parse `__NEXT_DATA__` JSON to extract `pageProps.toc` (full chapter list)
4. For each chapter:
   a. Fetch page HTML
   b. Extract `<article>` content via BeautifulSoup
   c. Download all `<img>` sources to local `images/` directory
   d. Rewrite `<img src>` to point to local paths
   e. Save cleaned HTML as `index.html`
   f. Convert to Markdown via `markdownify` and save as `index.md`

### CLI Interface

```bash
# Crawl entire course
python crawl.py genai-system-design-interview

# Crawl a specific chapter
python crawl.py genai-system-design-interview --chapter introduction-and-overview
```

### Authentication

- Read `BYTEBYTEGO_COOKIE` from `.env` file
- Attach as `Cookie` header on every request

### Error Handling

- Invalid/expired cookie on paid chapter → warn and skip, continue with next chapter
- Network error → retry once, then skip with warning
- Image download failure → warn but don't interrupt article saving

### Rate Limiting

- 1-2 second delay between page requests
- Sequential fetching (no concurrency)

## Tech Stack

- Python 3
- `requests` — HTTP client
- `beautifulsoup4` — HTML parsing
- `markdownify` — HTML to Markdown conversion
- `python-dotenv` — .env loading

## Approach Decision

Chose **pure HTTP + BeautifulSoup** over Playwright (too heavy) and Next.js data API (bundled JS content requires extra processing). The `<article>` tag contains fully rendered HTML, making direct parsing the simplest path.
