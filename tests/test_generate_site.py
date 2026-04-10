import os
import tempfile

from generate_site import scan_output_dir, format_course_name, render_markdown


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
