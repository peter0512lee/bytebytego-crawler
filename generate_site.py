"""Generate a static HTML site from crawled ByteByteGo output."""

import argparse
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


def generate_stylesheet() -> str:
    """Generate CSS stylesheet for the static site."""
    return '''/* Reset and Base Styles */
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 2rem;
    background: #FFFFFF;
    color: #1A1A2E;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
}

/* Home Page Title */
body > h1 {
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 3rem;
    color: #1A1A2E;
}

/* Course Grid - Home Page */
.course-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
    max-width: 1200px;
    margin: 0 auto;
}

.course-card {
    display: block;
    background: #FFFFFF;
    border: 2px solid transparent;
    border-radius: 12px;
    padding: 1.5rem;
    text-decoration: none;
    color: inherit;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.course-card:hover {
    border-color: #2CB67D;
    box-shadow: 0 4px 16px rgba(44, 182, 125, 0.15);
    transform: translateY(-2px);
}

.course-card h2 {
    margin: 0 0 0.5rem 0;
    font-size: 1.2rem;
    color: #1A1A2E;
}

.course-card p {
    margin: 0;
    color: #6B7280;
    font-size: 0.9rem;
}

/* Breadcrumb Navigation */
.breadcrumb {
    padding: 1rem 0;
    max-width: 800px;
    margin: 0 auto;
    font-size: 0.95rem;
}

.breadcrumb a {
    color: #2CB67D;
    text-decoration: none;
    transition: color 0.2s ease;
}

.breadcrumb a:hover {
    color: #239863;
    text-decoration: underline;
}

/* Chapter List - Course Page */
.chapter-list {
    max-width: 800px;
    margin: 2rem auto;
    padding: 0;
    list-style-position: inside;
}

.chapter-list li {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #E5E7EB;
    transition: background-color 0.2s ease;
}

.chapter-list li:hover {
    background-color: #F0FDF4;
}

.chapter-list a {
    text-decoration: none;
    color: #1A1A2E;
    display: inline;
}

.chapter-list a:hover {
    color: #2CB67D;
}

/* Article Content - Chapter Page */
.article-content {
    max-width: 800px;
    margin: 2rem auto;
    padding: 0 1rem;
    line-height: 1.7;
}

.article-content h1 {
    margin-top: 2rem;
    margin-bottom: 1rem;
    font-size: 2.25rem;
    color: #1A1A2E;
    line-height: 1.2;
}

.article-content h2 {
    margin-top: 2rem;
    margin-bottom: 1rem;
    font-size: 1.75rem;
    color: #1A1A2E;
    line-height: 1.3;
}

.article-content h3 {
    margin-top: 2rem;
    margin-bottom: 1rem;
    font-size: 1.35rem;
    color: #1A1A2E;
    line-height: 1.4;
}

.article-content p {
    margin-bottom: 1rem;
}

.article-content img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1.5rem auto;
    border-radius: 8px;
}

.article-content code {
    background: #F4F4F4;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.9em;
    font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace;
}

.article-content pre {
    background: #F4F4F4;
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
    line-height: 1.4;
    margin: 1rem 0;
}

.article-content pre code {
    background: none;
    padding: 0;
    font-size: 0.9rem;
}

.article-content blockquote {
    border-left: 4px solid #2CB67D;
    margin: 1.5rem 0;
    padding-left: 1rem;
    color: #6B7280;
    font-style: italic;
}

.article-content table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
}

.article-content table th,
.article-content table td {
    padding: 0.75rem;
    border: 1px solid #E5E7EB;
    text-align: left;
}

.article-content table th {
    background: #F9FAFB;
    font-weight: 600;
}

.article-content ul,
.article-content ol {
    margin: 1rem 0;
    padding-left: 2rem;
}

.article-content li {
    margin-bottom: 0.5rem;
}

/* Chapter Navigation - Bottom of Chapter Page */
.chapter-nav {
    max-width: 800px;
    margin: 3rem auto 2rem;
    padding: 1rem 0;
    border-top: 1px solid #E5E7EB;
    display: flex;
    justify-content: space-between;
    gap: 1rem;
}

.chapter-nav a {
    color: #2CB67D;
    text-decoration: none;
    transition: color 0.2s ease;
}

.chapter-nav a:hover {
    color: #239863;
    text-decoration: underline;
}

/* Responsive Design */
@media (max-width: 600px) {
    body {
        padding: 1rem;
    }

    .course-grid {
        grid-template-columns: 1fr;
    }

    body > h1 {
        font-size: 2rem;
    }

    .article-content {
        padding: 0 0.5rem;
    }

    .article-content h1 {
        font-size: 1.75rem;
    }

    .article-content h2 {
        font-size: 1.5rem;
    }

    .article-content h3 {
        font-size: 1.25rem;
    }

    .chapter-nav {
        flex-direction: column;
    }
}
'''


def generate_site(output_dir: str) -> None:
    """Generate the complete static site from crawled output."""
    courses = scan_output_dir(output_dir)

    # Write shared stylesheet
    css_path = os.path.join(output_dir, "style.css")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(generate_stylesheet())

    # Write home page
    home_path = os.path.join(output_dir, "index.html")
    with open(home_path, "w", encoding="utf-8") as f:
        f.write(generate_home_page(courses))

    for course in courses:
        course_dir = os.path.join(output_dir, course["slug"])

        # Write course page
        course_page_path = os.path.join(course_dir, "index.html")
        with open(course_page_path, "w", encoding="utf-8") as f:
            f.write(generate_course_page(course))

        # Write chapter pages
        chapters = course["chapters"]
        for i, chapter in enumerate(chapters):
            chapter_dir = os.path.join(course_dir, chapter["slug"])
            md_path = os.path.join(chapter_dir, "index.md")

            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            prev_ch = chapters[i - 1] if i > 0 else None
            next_ch = chapters[i + 1] if i < len(chapters) - 1 else None

            course_name = format_course_name(course["slug"])
            html = generate_chapter_page(course_name, chapter, md_content, prev_ch, next_ch)

            chapter_html_path = os.path.join(chapter_dir, "chapter.html")
            with open(chapter_html_path, "w", encoding="utf-8") as f:
                f.write(html)

    print(f"Generated site: {len(courses)} courses")
    for course in courses:
        print(f"  {format_course_name(course['slug'])}: {len(course['chapters'])} chapters")


def main():
    parser = argparse.ArgumentParser(description="Generate static HTML site from crawled output")
    parser.add_argument("--output", default="output", help="Output directory (default: output)")
    args = parser.parse_args()
    generate_site(args.output)


if __name__ == "__main__":
    main()
