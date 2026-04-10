# Static Site Generator Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Generate a static HTML site from crawled `output/` content with a course card homepage, course chapter lists, and rendered Markdown reading pages.

**Architecture:** A standalone `generate_site.py` script scans the `output/` directory, reads `index.md` files, and generates three layers of HTML pages (home → course → chapter). All pages reference a shared `style.css`. No server required — works with `file://` protocol.

**Tech Stack:** Python 3, `markdown` library (new dependency), existing project test patterns with `pytest`.

---

### Task 1: Directory Scanner

**Files:**
- Create: `generate_site.py`
- Create: `tests/test_generate_site.py`

**Step 1: Write the failing test**

```python
# tests/test_generate_site.py
import os
import tempfile

from generate_site import scan_output_dir


def test_scan_output_dir():
    with tempfile.TemporaryDirectory() as tmp:
        # Create fake course structure
        os.makedirs(os.path.join(tmp, "system-design", "01-intro"))
        os.makedirs(os.path.join(tmp, "system-design", "02-scale"))
        with open(os.path.join(tmp, "system-design", "01-intro", "index.md"), "w") as f:
            f.write("# Introduction\n\nHello")
        with open(os.path.join(tmp, "system-design", "02-scale", "index.md"), "w") as f:
            f.write("# Scale Up\n\nContent")

        courses = scan_output_dir(tmp)

        assert len(courses) == 1
        assert courses[0]["slug"] == "system-design"
        assert len(courses[0]["chapters"]) == 2
        assert courses[0]["chapters"][0]["number"] == 1
        assert courses[0]["chapters"][0]["slug"] == "01-intro"
        assert courses[0]["chapters"][0]["title"] == "Introduction"
        assert courses[0]["chapters"][1]["number"] == 2
        assert courses[0]["chapters"][1]["title"] == "Scale Up"


def test_scan_skips_dirs_without_index_md():
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "course-a", "01-has-md"))
        os.makedirs(os.path.join(tmp, "course-a", "02-no-md"))
        with open(os.path.join(tmp, "course-a", "01-has-md", "index.md"), "w") as f:
            f.write("# Chapter One\n")

        courses = scan_output_dir(tmp)
        assert len(courses[0]["chapters"]) == 1
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_generate_site.py -v`
Expected: FAIL with `ModuleNotFoundError` or `ImportError`

**Step 3: Write minimal implementation**

```python
# generate_site.py
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
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_generate_site.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add generate_site.py tests/test_generate_site.py
git commit -m "feat: scan output directory for course/chapter structure"
```

---

### Task 2: Course Name Formatting

**Files:**
- Modify: `generate_site.py`
- Modify: `tests/test_generate_site.py`

**Step 1: Write the failing test**

```python
# Add to tests/test_generate_site.py
from generate_site import format_course_name


def test_format_course_name_basic():
    assert format_course_name("system-design-interview") == "System Design Interview"


def test_format_course_name_genai():
    assert format_course_name("genai-system-design-interview") == "GenAI System Design Interview"


def test_format_course_name_ml():
    assert format_course_name("machine-learning-system-design-interview") == "Machine Learning System Design Interview"


def test_format_course_name_oo():
    assert format_course_name("object-oriented-design-interview") == "Object-Oriented Design Interview"


def test_format_course_name_short():
    assert format_course_name("tech-resume") == "Tech Resume"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_generate_site.py::test_format_course_name_basic -v`
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

```python
# Add to generate_site.py

# Special-case abbreviations for course slug → display name
_SLUG_OVERRIDES = {
    "genai": "GenAI",
    "ml": "ML",
    "oo": "OO",
}


def format_course_name(slug: str) -> str:
    """Convert a course slug to a human-readable name."""
    words = slug.split("-")
    result = []
    for word in words:
        if word in _SLUG_OVERRIDES:
            result.append(_SLUG_OVERRIDES[word])
        else:
            result.append(word.capitalize())
    return " ".join(result)
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_generate_site.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add generate_site.py tests/test_generate_site.py
git commit -m "feat: format course slugs into readable names"
```

---

### Task 3: Markdown Rendering

**Files:**
- Modify: `generate_site.py`
- Modify: `tests/test_generate_site.py`
- Modify: `requirements.txt`

**Step 1: Add dependency**

Add `markdown>=3.5.0` to `requirements.txt` and install:

```bash
pip install markdown>=3.5.0
```

**Step 2: Write the failing test**

```python
# Add to tests/test_generate_site.py
from generate_site import render_markdown


def test_render_markdown_basic():
    md = "# Hello\n\nSome **bold** text.\n"
    html = render_markdown(md)
    assert "<h1>Hello</h1>" in html
    assert "<strong>bold</strong>" in html


def test_render_markdown_code_block():
    md = "```python\nprint('hi')\n```\n"
    html = render_markdown(md)
    assert "<code" in html
    assert "print" in html


def test_render_markdown_images_preserved():
    md = "![diagram](images/figure-1.svg)\n"
    html = render_markdown(md)
    assert 'src="images/figure-1.svg"' in html
```

**Step 3: Run test to verify it fails**

Run: `python -m pytest tests/test_generate_site.py::test_render_markdown_basic -v`
Expected: FAIL with `ImportError`

**Step 4: Write minimal implementation**

```python
# Add to generate_site.py
import markdown as md_lib


def render_markdown(md_text: str) -> str:
    """Convert Markdown text to HTML."""
    return md_lib.markdown(md_text, extensions=["fenced_code", "tables"])
```

**Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_generate_site.py -v`
Expected: ALL PASS

**Step 6: Commit**

```bash
git add generate_site.py tests/test_generate_site.py requirements.txt
git commit -m "feat: render Markdown to HTML using markdown library"
```

---

### Task 4: HTML Templates and Page Generation

**Files:**
- Modify: `generate_site.py`
- Modify: `tests/test_generate_site.py`

**Step 1: Write the failing tests**

```python
# Add to tests/test_generate_site.py
from generate_site import generate_home_page, generate_course_page, generate_chapter_page


def test_generate_home_page():
    courses = [
        {"slug": "system-design-interview", "chapters": [{"slug": "01-intro", "number": 1, "title": "Intro"}]},
        {"slug": "tech-resume", "chapters": [{"slug": "01-ack", "number": 1, "title": "Ack"}, {"slug": "02-intro", "number": 2, "title": "Intro"}]},
    ]
    html = generate_home_page(courses)
    assert "My Courses" in html
    assert "System Design Interview" in html
    assert "Tech Resume" in html
    assert "1 chapters" in html or "1 chapter" in html
    assert "2 chapters" in html
    assert 'href="system-design-interview/index.html"' in html
    assert "style.css" in html


def test_generate_course_page():
    course = {
        "slug": "system-design-interview",
        "chapters": [
            {"slug": "01-intro", "number": 1, "title": "Introduction"},
            {"slug": "02-scale", "number": 2, "title": "Scale Up"},
        ],
    }
    html = generate_course_page(course)
    assert "System Design Interview" in html
    assert "Introduction" in html
    assert "Scale Up" in html
    assert 'href="01-intro/chapter.html"' in html
    assert 'href="../index.html"' in html
    assert "../style.css" in html


def test_generate_chapter_page():
    chapter = {"slug": "02-scale", "number": 2, "title": "Scale Up"}
    prev_ch = {"slug": "01-intro", "number": 1, "title": "Introduction"}
    next_ch = {"slug": "03-rate", "number": 3, "title": "Rate Limiter"}
    md_content = "# Scale Up\n\nSome content with **bold**.\n"

    html = generate_chapter_page(
        course_name="System Design Interview",
        chapter=chapter,
        md_content=md_content,
        prev_chapter=prev_ch,
        next_chapter=next_ch,
    )
    assert "Scale Up" in html
    assert "<strong>bold</strong>" in html
    assert 'href="../index.html"' in html
    assert 'href="../01-intro/chapter.html"' in html
    assert 'href="../03-rate/chapter.html"' in html
    assert "../../style.css" in html


def test_generate_chapter_page_no_prev_next():
    chapter = {"slug": "01-intro", "number": 1, "title": "Intro"}
    md_content = "# Intro\n\nOnly chapter.\n"
    html = generate_chapter_page(
        course_name="Test",
        chapter=chapter,
        md_content=md_content,
        prev_chapter=None,
        next_chapter=None,
    )
    assert "Intro" in html
    # No prev/next links
    assert "Previous" not in html
    assert "Next" not in html
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_generate_site.py::test_generate_home_page -v`
Expected: FAIL with `ImportError`

**Step 3: Write implementation**

Add to `generate_site.py` — three functions that return complete HTML strings using f-strings. Each page references `style.css` at the correct relative depth.

Key points for each template:
- `generate_home_page(courses)` — card grid with course name + chapter count, links to `{slug}/index.html`
- `generate_course_page(course)` — chapter list, links to `{slug}/chapter.html`, breadcrumb back to `../index.html`
- `generate_chapter_page(course_name, chapter, md_content, prev_chapter, next_chapter)` — rendered article, nav links, breadcrumb to `../index.html`

Implementation is straightforward HTML string building — see the code in the commit.

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_generate_site.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add generate_site.py tests/test_generate_site.py
git commit -m "feat: HTML page generation for home, course, and chapter views"
```

---

### Task 5: CSS Stylesheet

**Files:**
- Modify: `generate_site.py`

**Step 1: Add `generate_stylesheet` function**

This returns the CSS string. Key styles:
- Body: white background, system font stack
- Cards: CSS Grid, green (#2CB67D) border on hover, border-radius, shadow
- Course page: clean ordered list with generous spacing
- Chapter page: max-width 800px, comfortable line-height (1.7), image max-width 100%
- Code blocks: light gray background, padding, overflow-x scroll
- Nav: sticky top bar with breadcrumb, prev/next footer
- Responsive: single column on mobile

**Step 2: Write a simple test**

```python
# Add to tests/test_generate_site.py
from generate_site import generate_stylesheet


def test_generate_stylesheet_has_key_rules():
    css = generate_stylesheet()
    assert ".course-card" in css
    assert "max-width" in css
    assert "#2CB67D" in css or "#2cb67d" in css
```

**Step 3: Run tests**

Run: `python -m pytest tests/test_generate_site.py -v`
Expected: ALL PASS

**Step 4: Commit**

```bash
git add generate_site.py tests/test_generate_site.py
git commit -m "feat: shared CSS stylesheet for static site"
```

---

### Task 6: Main Orchestrator and CLI

**Files:**
- Modify: `generate_site.py`

**Step 1: Write integration test**

```python
# Add to tests/test_generate_site.py
def test_generate_site_end_to_end():
    with tempfile.TemporaryDirectory() as tmp:
        # Create fake course with 2 chapters
        c1 = os.path.join(tmp, "test-course", "01-intro")
        c2 = os.path.join(tmp, "test-course", "02-details")
        os.makedirs(c1)
        os.makedirs(c2)
        with open(os.path.join(c1, "index.md"), "w") as f:
            f.write("# Introduction\n\nFirst chapter.\n")
        with open(os.path.join(c2, "index.md"), "w") as f:
            f.write("# Details\n\nSecond chapter with **bold**.\n")

        from generate_site import generate_site
        generate_site(tmp)

        # Check files exist
        assert os.path.exists(os.path.join(tmp, "index.html"))
        assert os.path.exists(os.path.join(tmp, "style.css"))
        assert os.path.exists(os.path.join(tmp, "test-course", "index.html"))
        assert os.path.exists(os.path.join(tmp, "test-course", "01-intro", "chapter.html"))
        assert os.path.exists(os.path.join(tmp, "test-course", "02-details", "chapter.html"))

        # Check home page links to course
        with open(os.path.join(tmp, "index.html")) as f:
            home = f.read()
        assert "Test Course" in home
        assert "2 chapters" in home

        # Check chapter has rendered Markdown
        with open(os.path.join(tmp, "test-course", "02-details", "chapter.html")) as f:
            ch = f.read()
        assert "<strong>bold</strong>" in ch

        # Check chapter has prev/next nav
        assert "Introduction" in ch  # prev link text
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_generate_site.py::test_generate_site_end_to_end -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# Add to generate_site.py
import argparse


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
```

**Step 4: Run all tests**

Run: `python -m pytest tests/test_generate_site.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add generate_site.py tests/test_generate_site.py
git commit -m "feat: main site generator with CLI entry point"
```

---

### Task 7: Run Against Real Data and Verify

**Step 1: Generate the site**

```bash
python generate_site.py --output output
```

Expected output:
```
Generated site: 5 courses
  System Design Interview: 31 chapters
  GenAI System Design Interview: 11 chapters
  ...
```

**Step 2: Open in browser and verify**

Open `output/index.html` in browser. Verify:
- 5 course cards displayed in grid
- Clicking a card navigates to chapter list
- Clicking a chapter shows rendered Markdown with images
- Prev/Next navigation works
- Styling looks clean

**Step 3: Commit generated files to `.gitignore`**

The generated `style.css`, course `index.html`, and `chapter.html` files are
derived artifacts. Add to `.gitignore`:

```
output/index.html
output/style.css
output/*/index.html
output/*/*/chapter.html
```

**Step 4: Final commit**

```bash
git add .gitignore
git commit -m "chore: ignore generated site files"
```

---

### Task 8: Run Full Test Suite

**Step 1: Run all tests**

```bash
python -m pytest tests/ -v
```

Expected: ALL PASS (both existing crawl tests and new generate_site tests)

**Step 2: Verify no linting issues**

```bash
python -m py_compile generate_site.py
python -m py_compile crawl.py
```

Expected: No errors
