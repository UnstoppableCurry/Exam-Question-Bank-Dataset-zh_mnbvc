#!/usr/bin/env python3
"""Check internal links, assets, and expected pages in the built docs/ site."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

REQUIRED = [
    "index.html",
    "pipeline.html",
    "usage.html",
    "notebooks.html",
    "results.html",
    "404.html",
    "robots.txt",
    "sitemap.xml",
    ".nojekyll",
    "assets/styles.css",
    "assets/site.js",
    "assets/favicon.svg",
    "notebooks/create-datasets.html",
    "notebooks/train.html",
    "notebooks/type-classifier.html",
    "notebooks/validation.html",
    "notebooks/random-test.html",
]


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if tag == "a" and attr.get("href"):
            self.refs.append(("href", attr["href"]))
        if tag == "link" and attr.get("href"):
            self.refs.append(("href", attr["href"]))
        if tag in {"script", "img"} and attr.get("src"):
            self.refs.append(("src", attr["src"]))


def local_target(page: Path, raw_url: str) -> Path | None:
    url, _frag = urldefrag(raw_url)
    if not url or url.startswith(("#", "mailto:", "javascript:")):
        return None
    parsed = urlparse(url)
    if parsed.scheme in {"http", "https"}:
        return None
    joined = urljoin(page.as_uri(), url)
    parsed_local = urlparse(joined)
    return Path(parsed_local.path)


def main() -> int:
    errors: list[str] = []
    if not DOCS.is_dir():
        print("docs/ does not exist. Run site/build.py first.", file=sys.stderr)
        return 1

    for rel in REQUIRED:
        if not (DOCS / rel).exists():
            errors.append(f"missing required file: {rel}")

    html_files = sorted(DOCS.rglob("*.html"))
    if len(html_files) < 10:
        errors.append(f"expected at least 10 HTML files, found {len(html_files)}")

    for page in html_files:
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for kind, ref in parser.refs:
            target = local_target(page, ref)
            if target is None:
                continue
            try:
                resolved = target.resolve()
            except OSError:
                errors.append(f"{page.relative_to(DOCS)} {kind}={ref} is not resolvable")
                continue
            if DOCS.resolve() not in resolved.parents and resolved != DOCS.resolve():
                errors.append(f"{page.relative_to(DOCS)} {kind}={ref} escapes docs/")
                continue
            if not resolved.exists():
                errors.append(f"{page.relative_to(DOCS)} {kind}={ref} -> missing {resolved}")

    sitemap = (DOCS / "sitemap.xml").read_text(encoding="utf-8")
    if "unstoppablecurry.github.io/Exam-Question-Bank-Dataset-zh_mnbvc" not in sitemap:
        errors.append("sitemap.xml does not contain the intended Pages URL")

    robots = (DOCS / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap:" not in robots:
        errors.append("robots.txt missing Sitemap")

    index_html = (DOCS / "index.html").read_text(encoding="utf-8")
    for needle in (
        'lang="zh-CN"',
        "skip-link",
        "canonical",
        "og:title",
        "选择 · 填空 · 简答",
        "静态文档与结果展示",
    ):
        if needle not in index_html:
            errors.append(f"index.html missing {needle}")

    results_html = (DOCS / "results.html").read_text(encoding="utf-8")
    for needle in ("0.9794419970631424", "10297", "13621", "不选取"):
        if needle not in results_html:
            errors.append(f"results.html missing recorded output {needle}")

    if errors:
        print("Site check failed:")
        for item in errors:
            print(f" - {item}")
        return 1

    print(f"OK: checked {len(html_files)} HTML pages and {len(REQUIRED)} required files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
