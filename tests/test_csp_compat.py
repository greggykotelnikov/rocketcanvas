"""Templates must not rely on markup the Content Security Policy blocks.

The CSP allows scripts/styles only via nonce'd <script>/<style> blocks, so
browsers silently ignore inline style="..." attributes and on*="..." event
handlers. Both caused real bugs here (dead buttons, panels that never hid).
"""
import glob
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = sorted(glob.glob(os.path.join(ROOT, "templates", "*.html")))
# Attributes inside HTML tags only (not CSS/JS text in <style>/<script>).
TAG_RE = re.compile(r"<[a-zA-Z][^<>]*>")
STYLE_ATTR = re.compile(r"\sstyle\s*=")
HANDLER_ATTR = re.compile(r"\son[a-z]+\s*=")


def tags_outside_scripts(html):
    html = re.sub(r"<script\b.*?</script>", "", html, flags=re.S | re.I)
    html = re.sub(r"<style\b.*?</style>", "", html, flags=re.S | re.I)
    return TAG_RE.findall(html)


@pytest.mark.parametrize("path", TEMPLATES, ids=os.path.basename)
def test_no_inline_styles_or_handlers(path):
    with open(path, encoding="utf-8") as f:
        tags = tags_outside_scripts(f.read())
    bad = [t for t in tags if STYLE_ATTR.search(t) or HANDLER_ATTR.search(t)]
    assert not bad, f"CSP will ignore these in {os.path.basename(path)}: {bad[:3]}"


def test_csp_has_no_unsafe_inline(client):
    csp = client.get("/login").headers["Content-Security-Policy"]
    assert "'unsafe-inline'" not in csp
