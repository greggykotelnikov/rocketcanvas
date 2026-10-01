"""Every local <script>/<link> integrity hash must match the file on disk.

A mismatch makes the browser silently refuse to run the script or apply
the stylesheet, which no server-side test would otherwise notice.
"""
import base64
import glob
import hashlib
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG_RE = re.compile(r"<(?:script|link)\b[^>]*>")
STATIC_RE = re.compile(r"""url_for\('static',\s*filename='([^']+)'\)""")
SRI_RE = re.compile(r'integrity="(sha384-[^"]+)"')


def local_tags_with_sri():
    for template in sorted(glob.glob(os.path.join(ROOT, "templates", "*.html"))):
        with open(template, encoding="utf-8") as f:
            for tag in TAG_RE.findall(f.read()):
                static, sri = STATIC_RE.search(tag), SRI_RE.search(tag)
                if static and sri:
                    yield os.path.basename(template), static.group(1), sri.group(1)


CASES = list(local_tags_with_sri())


def test_found_tags():
    assert len(CASES) >= 8


@pytest.mark.parametrize("template,path,expected", CASES, ids=[f"{t}:{p}" for t, p, _ in CASES])
def test_sri_matches_file(template, path, expected):
    with open(os.path.join(ROOT, "static", path), "rb") as f:
        actual = "sha384-" + base64.b64encode(hashlib.sha384(f.read()).digest()).decode()
    assert actual == expected, (
        f"{template} pins static/{path} with a stale integrity hash; "
        f"run: python scripts/sri_hashes.py static/{path}"
    )
