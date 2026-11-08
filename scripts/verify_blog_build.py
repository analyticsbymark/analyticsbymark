"""Check generated blog metadata and resources in a built MkDocs site."""

import argparse
import gzip
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.links = {}
        self.scripts = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            self.meta[attrs.get("property", attrs.get("name"))] = attrs.get("content")
        elif tag == "link":
            self.links[attrs.get("rel")] = attrs.get("href")
        elif tag == "script" and attrs.get("type") == "application/ld+json":
            self.current = ""

    def handle_data(self, data):
        if self.current is not None:
            self.current += data

    def handle_endtag(self, tag):
        if tag == "script" and self.current is not None:
            self.scripts.append(json.loads(self.current))
            self.current = None


def verify(site):
    site = Path(site)
    posts = json.loads((site / "blog/index.json").read_text())
    for post in posts:
        relative = urlsplit(post["url"]).path.lstrip("/")
        page = site / relative / "index.html"
        if not page.exists():
            page = site / relative
        html = page.read_text()
        head = Head()
        head.feed(html)
        assert {item["@type"] for item in head.scripts} == {"BlogPosting", "BreadcrumbList"}
        article = next(item for item in head.scripts if item["@type"] == "BlogPosting")
        assert article["abstract"] == post["summary"]
        assert head.links["canonical"] == post["url"]
        assert head.meta["description"] == article["description"]
        assert head.meta["og:description"] == article["description"]
        assert head.meta["article:published_time"] == article["datePublished"]
        assert page.with_suffix(".md").is_file()
        assert "View as Markdown" in html and "Summary for agents" in html
        for key in ("og:image", "twitter:image"):
            assert (site / urlsplit(head.meta[key]).path.lstrip("/")).is_file()
    sitemap = (site / "sitemap.xml").read_bytes()
    for path in ("start-here/", "showcase/", "blog-authoring-guide/"):
        assert path.encode() not in sitemap
    assert gzip.decompress((site / "sitemap.xml.gz").read_bytes()) == sitemap
    assert (site / "llms.txt").is_file() and (site / "robots.txt").is_file()
    print(f"Verified {len(posts)} posts: JSON-LD, metadata, Markdown, cards, and sitemap.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site_dir", type=Path)
    verify(parser.parse_args().site_dir)
