"""Exercise the real Material templates with an isolated, disposable post."""

import gzip
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit

from mkdocs.commands.build import build
from mkdocs.config import load_config
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def test_real_post_build(tmp_path):
    docs = tmp_path / "docs"
    posts = docs / "blog/posts"
    posts.mkdir(parents=True)
    (docs / "assets").mkdir()
    for name in ("logo.png", "logo.svg", "favicon.svg"):
        shutil.copyfile(ROOT / "website/docs/assets" / name, docs / "assets" / name)
    (docs / "index.md").write_text("# Home\n")
    (docs / "blog/index.md").write_text("# Blog\n")
    for page in ("start-here", "showcase", "blog-authoring-guide"):
        (docs / f"{page}.md").write_text(f"# {page}\n")
    title = 'Insurance data validation "quoted" policies & claims workflows for repeatable monthly jobs'
    assert len(title) == 90
    source = (
        '---\ntitle: >-\n  ' + title + '\n'
        'date: {created: 2026-01-02, updated: 2026-02-03}\n'
        'categories: [Analytics]\ntags: [validation]\nslug: long-title\n'
        'description: A practical description of validation rules for insurance policy and claims feeds.\n'
        'keywords: [insurance validation, claims]\n'
        'summary: A factual summary. A second factual sentence.\n'
        'key_points: [First point, Second point, Third point]\nprerequisites: [Python]\n'
        'image: assets/logo.png\ndummy: true\n---\n\n# ' + title + '\n\n'
        '!!! note "Sample post"\n    Demonstration content.\n\n<!-- more -->\n\n## Checks\n\nBody.\n'
    )
    (posts / "example.md").write_text(source, encoding="utf-8")
    site = tmp_path / "site"
    config = load_config(
        config_file=str(ROOT / "website/mkdocs.yml"), strict=True,
        docs_dir=str(docs), site_dir=str(site),
        nav=[{"Home": "index.md"}, {"Blog": "blog/index.md"}],
        extra_css=[], extra_javascript=[],
    )
    config.plugins.on_startup(command="build", dirty=False)
    try:
        build(config)
    finally:
        config.plugins.on_shutdown()
    entries = json.loads((site / "blog/index.json").read_text())
    assert len(entries) == 1 and entries[0]["dummy"] is True
    url_path = urlsplit(entries[0]["url"]).path.lstrip("/")
    html = (site / url_path / "index.html").read_text()
    scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    article, breadcrumb = [json.loads(script) for script in scripts]
    assert article["headline"] == title and article["dateModified"].startswith("2026-02-03")
    assert breadcrumb["@type"] == "BreadcrumbList"
    assert html.count('name="description"') == 1 and html.count('rel="canonical"') == 1
    assert 'property="article:published_time"' in html and 'property="article:tag"' in html
    assert "Summary for agents" in html and "View as Markdown" in html
    assert (site / url_path / "index.md").read_text() == source
    assert '&quot;quoted&quot;' in html or '&#34;quoted&#34;' in html
    for property_name in ("og:image", "twitter:image"):
        image_url = re.search(rf'property="{property_name}" content="([^"]+)"', html)[1]
        image_path = site / urlsplit(image_url).path.lstrip("/")
        assert image_path.is_file()
        with Image.open(image_path) as image:
            assert image.size == (1200, 630)
    sitemap = (site / "sitemap.xml").read_bytes()
    assert gzip.decompress((site / "sitemap.xml.gz").read_bytes()) == sitemap
    for excluded in ("start-here", "showcase", "blog-authoring-guide"):
        assert excluded.encode() not in sitemap
        assert 'name="robots" content="noindex"' in (site / excluded / "index.html").read_text()
        assert f"/{excluded}/" in (site / "llms.txt").read_text()
