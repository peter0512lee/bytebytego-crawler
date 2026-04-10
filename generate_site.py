"""Generate a static HTML site from crawled ByteByteGo output."""

import os
import re
import markdown as md_lib


# Special-case abbreviations for course slug → display name
_SLUG_OVERRIDES = {
    "genai": "GenAI",
    "ml": "ML",
    "object-oriented": "Object-Oriented",
}


def format_course_name(slug: str) -> str:
    """Convert a course slug to a human-readable name."""
    # Handle multi-word phrases first (e.g., "object-oriented")
    for phrase, replacement in _SLUG_OVERRIDES.items():
        if "-" in phrase:
            # Replace the phrase, preserving hyphens in the replacement
            slug = slug.replace(phrase, replacement.replace("-", "\x00"))

    words = slug.split("-")
    result = []
    for word in words:
        # Restore hyphens in multi-word replacements
        if "\x00" in word:
            result.append(word.replace("\x00", "-"))
        elif word in _SLUG_OVERRIDES:
            result.append(_SLUG_OVERRIDES[word])
        else:
            result.append(word.capitalize())
    return " ".join(result)


def _extract_title_from_md(md_path: str) -> str:
    """Read the first # heading from a Markdown file."""
    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
    # Fallback: derive from directory name
    slug = os.path.basename(os.path.dirname(md_path))
    # Strip leading number prefix like "01-"
    slug = re.sub(r"^\d+-", "", slug)
    return slug.replace("-", " ").title()


def scan_output_dir(output_dir: str) -> list[dict]:
    """Scan output directory and return structured course/chapter data."""
    courses = []
    for course_slug in sorted(os.listdir(output_dir)):
        course_path = os.path.join(output_dir, course_slug)
        if not os.path.isdir(course_path):
            continue

        chapters = []
        for chapter_dir in sorted(os.listdir(course_path)):
            chapter_path = os.path.join(course_path, chapter_dir)
            if not os.path.isdir(chapter_path):
                continue

            md_path = os.path.join(chapter_path, "index.md")
            if not os.path.exists(md_path):
                continue

            # Extract chapter number from directory name (e.g. "02-scale" → 2)
            match = re.match(r"^(\d+)-", chapter_dir)
            number = int(match.group(1)) if match else 0

            title = _extract_title_from_md(md_path)

            chapters.append({
                "slug": chapter_dir,
                "number": number,
                "title": title,
            })

        if chapters:
            courses.append({
                "slug": course_slug,
                "chapters": chapters,
            })

    return courses


def render_markdown(md_text: str) -> str:
    """Convert Markdown text to HTML."""
    return md_lib.markdown(md_text, extensions=["fenced_code", "tables"])


def generate_home_page(courses: list[dict]) -> str:
    """Generate HTML for the home page listing all courses."""
    course_cards = []
    for course in courses:
        course_name = format_course_name(course["slug"])
        num_chapters = len(course["chapters"])
        chapter_text = "chapter" if num_chapters == 1 else "chapters"

        course_cards.append(f'''
            <a href="{course["slug"]}/index.html" class="course-card">
                <h2>{course_name}</h2>
                <p>{num_chapters} {chapter_text}</p>
            </a>
        ''')

    course_grid = "\n".join(course_cards)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <title>My Courses</title>
</head>
<body>
    <h1>My Courses</h1>
    <div class="course-grid">
        {course_grid}
    </div>
</body>
</html>'''


def generate_course_page(course: dict) -> str:
    """Generate HTML for a course page listing all chapters."""
    course_name = format_course_name(course["slug"])

    chapter_items = []
    for chapter in course["chapters"]:
        chapter_items.append(
            f'<li><a href="{chapter["slug"]}/chapter.html">{chapter["title"]}</a></li>'
        )

    chapter_list = "\n".join(chapter_items)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../style.css">
    <title>{course_name}</title>
</head>
<body>
    <nav class="breadcrumb">
        <a href="../index.html">Home</a> &gt; {course_name}
    </nav>
    <h1>{course_name}</h1>
    <ol class="chapter-list">
        {chapter_list}
    </ol>
</body>
</html>'''


def generate_chapter_page(
    course_name: str,
    chapter: dict,
    md_content: str,
    prev_chapter: dict | None,
    next_chapter: dict | None,
) -> str:
    """Generate HTML for a chapter reading page."""
    # Render markdown to HTML
    article_html = render_markdown(md_content)

    # Build navigation links
    nav_links = []
    if prev_chapter:
        nav_links.append(
            f'<a href="../{prev_chapter["slug"]}/chapter.html">'
            f'← Previous: {prev_chapter["title"]}</a>'
        )
    if next_chapter:
        nav_links.append(
            f'<a href="../{next_chapter["slug"]}/chapter.html">'
            f'Next: {next_chapter["title"]} →</a>'
        )

    chapter_nav = ""
    if nav_links:
        nav_html = " | ".join(nav_links)
        chapter_nav = f'<nav class="chapter-nav">{nav_html}</nav>'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../../style.css">
    <title>{chapter["title"]} - {course_name}</title>
</head>
<body>
    <nav>
        <a href="../index.html">← {course_name}</a>
    </nav>
    <article class="article-content">
        {article_html}
    </article>
    {chapter_nav}
</body>
</html>'''
