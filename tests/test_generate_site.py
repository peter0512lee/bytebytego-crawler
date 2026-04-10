import os
import tempfile

from generate_site import (
    scan_output_dir,
    format_course_name,
    render_markdown,
    generate_home_page,
    generate_course_page,
    generate_chapter_page,
    generate_stylesheet,
)


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
    assert "Previous" not in html
    assert "Next" not in html


def test_generate_stylesheet_has_key_rules():
    css = generate_stylesheet()
    assert ".course-card" in css
    assert "max-width" in css
    assert "#2CB67D" in css or "#2cb67d" in css


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
