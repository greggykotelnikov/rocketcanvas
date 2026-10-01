"""
List <script src> and stylesheet <link> tags in templates that lack an
SRI integrity attribute. Exits non-zero if any are missing.

Usage (from anywhere):  python scripts/check_sri.py
"""
import os
import re
import sys

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")

SCRIPT_RE = re.compile(r"<script[^>]*src=[^>]*>")
STYLESHEET_RE = re.compile(r"""<link[^>]*rel=['"]stylesheet['"][^>]*>""")


def main():
    count = 0
    for root, _, files in os.walk(TEMPLATES_DIR):
        for name in sorted(files):
            if not name.endswith(".html"):
                continue
            with open(os.path.join(root, name), encoding="utf-8") as f:
                content = f.read()
            for tag in SCRIPT_RE.findall(content) + STYLESHEET_RE.findall(content):
                if "integrity" not in tag:
                    print(f"Missing SRI in {name}: {tag}")
                    count += 1
    print(f"Total missing: {count}")
    return 1 if count else 0


if __name__ == "__main__":
    sys.exit(main())
