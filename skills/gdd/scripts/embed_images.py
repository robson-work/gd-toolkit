#!/usr/bin/env python3
"""Embed local <img src="..."> files in an HTML page as data URIs.

Usage:
  embed_images.py page.html          rewrite page.html in place
  embed_images.py page.html --check  exit 1 if any non-data image src remains

Paths are resolved relative to the page. Remote (http/https) images are left
alone by the rewrite and reported by --check.
"""
import base64
import mimetypes
import re
import sys
from pathlib import Path

IMG_SRC = re.compile(r'(<img\b[^>]*?\bsrc=)(["\'])(.*?)\2', re.IGNORECASE | re.DOTALL)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv
    if len(args) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    page = Path(args[0]).resolve()
    html = page.read_text(encoding="utf-8")

    if check:
        left = [m.group(3) for m in IMG_SRC.finditer(html) if not m.group(3).startswith("data:")]
        for src in left:
            print(f"not embedded: {src}")
        print(f"{len(left)} image(s) not embedded")
        return 1 if left else 0

    missing, embedded = [], 0

    def repl(m: re.Match) -> str:
        nonlocal embedded
        src = m.group(3)
        if src.startswith(("data:", "http://", "https://")):
            return m.group(0)
        path = (page.parent / src).resolve()
        if not path.is_file():
            missing.append(src)
            return m.group(0)
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        embedded += 1
        return f'{m.group(1)}{m.group(2)}data:{mime};base64,{data}{m.group(2)}'

    html = IMG_SRC.sub(repl, html)
    page.write_text(html, encoding="utf-8")
    print(f"embedded {embedded} image(s) into {page}")
    for src in missing:
        print(f"missing file: {src}", file=sys.stderr)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
