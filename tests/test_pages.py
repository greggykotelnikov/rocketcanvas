"""Smoke tests: every page renders, and every static file it links exists."""
import os
import re

import pytest
from urllib.parse import unquote

import app as appmod

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["/profile", "/dashboard", "/analytics", "/gallery", "/garage",
         "/heatmap", "/hitbox", "/recommend", "/offline"]
STATIC_RE = re.compile(r"""(?:src|href)="(/static/[^"?#]+)""")


@pytest.fixture
def no_api(monkeypatch):
    monkeypatch.setattr(appmod, "search_replays_by_player", lambda p, count: {"list": []})


@pytest.mark.parametrize("path", PAGES)
def test_page_renders(auth_client, no_api, path):
    resp = auth_client.get(path)
    assert resp.status_code == 200, path


@pytest.mark.parametrize("path", ["/login", "/register", "/manifest.json", "/sw.js"])
def test_public_pages_render(client, path):
    assert client.get(path).status_code == 200


def test_static_links_point_to_existing_files(auth_client, no_api):
    missing = set()
    for page in PAGES:
        html = auth_client.get(page).get_data(as_text=True)
        for url in STATIC_RE.findall(html):
            rel = unquote(url[len("/static/"):])
            # User uploads and git-ignored licensed music aren't in the repo.
            if rel.startswith(("uploads/", "sounds/bgm/")):
                continue
            if not os.path.exists(os.path.join(ROOT, "static", *rel.split("/"))):
                missing.add(f"{page}: {url}")
    assert not missing, sorted(missing)
