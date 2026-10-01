"""
Print sha384 SRI hashes for local JS and CSS files, for pasting into the
integrity="..." attributes in templates after editing a static file.

Usage (from anywhere):  python scripts/sri_hashes.py [file ...]
With no arguments, hashes everything in static/js and static/css.
"""
import base64
import glob
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sri(path):
    with open(path, "rb") as f:
        digest = hashlib.sha384(f.read()).digest()
    return "sha384-" + base64.b64encode(digest).decode("ascii")


if __name__ == "__main__":
    paths = sys.argv[1:] or sorted(
        glob.glob(os.path.join(ROOT, "static", "js", "*.js"))
        + glob.glob(os.path.join(ROOT, "static", "css", "*.css"))
    )
    for path in paths:
        print(f"{os.path.relpath(path, ROOT)}: {sri(path)}")
