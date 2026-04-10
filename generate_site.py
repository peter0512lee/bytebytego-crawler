"""Generate a static HTML site from crawled ByteByteGo output."""

import os
import re


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
