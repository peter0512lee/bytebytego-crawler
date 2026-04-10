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
