# Static Site Generator for ByteByteGo Crawler

## Problem

The crawler outputs raw HTML/Markdown files per chapter, but there's no unified
browsing experience. Users must navigate the file system to find content. We want
a "My Courses" page similar to bytebytego.com/my-courses that shows all courses
as cards, with drill-down into chapters.

## Decision

Generate pure static HTML files from the existing `output/` directory. No server
required — double-click `output/index.html` to browse.

## Architecture

### Page Hierarchy

```
output/
├── index.html                          ← Home: course card grid
├── style.css                           ← Shared stylesheet
├── {course}/
│   ├── index.html                      ← Course: chapter list
│   ├── {chapter}/
│   │   ├── chapter.html                ← Rendered reading page (NEW)
│   │   ├── index.html                  ← Raw crawled HTML (existing)
│   │   ├── index.md                    ← Raw crawled Markdown (existing)
│   │   └── images/                     ← Downloaded images (existing)
```

### Page Templates

#### 1. Home Page (`output/index.html`)

- Title: "My Courses"
- CSS grid of course cards
- Each card shows: course name (human-readable), chapter count
- Click card → `{course}/index.html`

#### 2. Course Page (`output/{course}/index.html`)

**Note:** This overwrites the existing directory listing. Currently there is no
`index.html` at the course level, so this is safe.

- Breadcrumb: Home > Course Name
- Course title as heading
- Ordered list of chapters (number + title)
- Click chapter → `{chapter}/chapter.html`

#### 3. Chapter Page (`output/{course}/{chapter}/chapter.html`)

Named `chapter.html` to avoid overwriting existing `index.html`.

- Top nav: ← Back to course
- Rendered Markdown content with images
- Bottom nav: Previous Chapter / Next Chapter

### Course Name Mapping

Derive human-readable names from directory slugs:

| Slug | Display Name |
|------|-------------|
| system-design-interview | System Design Interview |
| genai-system-design-interview | GenAI System Design Interview |
| machine-learning-system-design-interview | Machine Learning System Design Interview |
| object-oriented-design-interview | Object-Oriented Design Interview |
| tech-resume | Tech Resume |

Strategy: split on `-`, title-case each word, with special cases for
abbreviations (GenAI, ML, OO).

### Chapter Metadata

Extract chapter number and title from directory name pattern `{NN}-{slug}`.
Title derived from the first `# heading` in `index.md`, falling back to
slug-based title-casing.

## Technical Details

### New File: `generate_site.py`

Standalone script (not a crawl.py subcommand) to keep concerns separate.

```
python generate_site.py [--output output]
```

### Dependencies

- `markdown` — Python Markdown library for `.md` → HTML conversion
- No other new dependencies

### Styling

- Single `style.css` file at `output/` root
- Clean white background, green accent (#2CB67D matching ByteByteGo theme)
- Responsive card grid (CSS Grid)
- Article page: max-width 800px, comfortable reading line-height
- Code block styling with background
- Image max-width: 100%

### How It Works

1. Scan `output/` for course directories
2. For each course, scan for chapter directories
3. Read `index.md` from each chapter, extract title from `# heading`
4. Render Markdown → HTML using `markdown` library
5. Generate `chapter.html` wrapping rendered content in template
6. Generate course `index.html` with chapter list
7. Generate root `index.html` with course cards
8. Write shared `style.css`

### Integration with Crawler

The generator reads from `output/` and is completely independent of the crawler.
Run it after crawling:

```bash
python crawl.py system-design-interview
python generate_site.py
```

## Out of Scope

- Search functionality
- Dark mode toggle
- Course cover images (not available in crawled data)
- Table of contents sidebar within chapters
