"""Public blog metadata and build-time agent resources."""

import gzip
import json
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urljoin
from xml.etree import ElementTree as ET

from mkdocs.plugins import event_priority

_pages = {}
EXCLUDED = {"start-here.md", "showcase.md", "blog-authoring-guide.md"}


def on_pre_build(**kwargs):
    _pages.clear()


@event_priority(-75)
def on_page_markdown(markdown, *, page, **kwargs):
    path = page.file.src_uri
    if path == "blog/index.md" or path.startswith("blog/page/"):
        title = "Blog"
        description = "Practical notes on insurance data models, analytics, and AI agents."
    elif path.startswith("blog/archive/"):
        year = path.split("/")[2].removesuffix(".md")
        title = f"Archive {year}"
        description = f"Browse {year} posts on insurance data, analytics, and AI agents."
    elif path.startswith("blog/category/"):
        category = page.title
        title = f"Category: {category}"
        description = f"Notes and tutorials about {category}, with practical insurance data examples."
    else:
        return
    page.meta["abm_card_title"] = title
    page.meta["abm_card_description"] = description


def iso(value):
    return value.isoformat() if isinstance(value, (date, datetime)) else str(value or "")


def absolute(config, path):
    return urljoin(config["site_url"].rstrip("/") + "/", path)


def is_post(page):
    return page.meta.get("template") == "blog-post.html"


def markdown_url(page):
    destination = Path(page.file.dest_uri)
    return destination.with_suffix(".md").as_posix()


def entry(page, config):
    meta = page.meta
    dates = page.config.date
    return {
        "title": page.title,
        "url": page.canonical_url or absolute(config, page.url),
        "slug": meta.get("slug", page.url.rstrip("/").split("/")[-1]),
        "date": {"created": iso(dates.created), "updated": iso(dates.updated or dates.created)},
        "category": list(meta.get("categories", [])),
        "tags": list(meta.get("tags", [])),
        "keywords": list(meta.get("keywords", [])),
        "summary": meta.get("summary", ""),
        **{key: meta.get(key) for key in ("series", "series_part", "series_total", "start_here")},
        "dummy": meta.get("dummy", False),
        "related_slugs": [],
    }


def structured_data(page, config):
    post = entry(page, config)
    article = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post["title"],
        "description": page.meta.get("description", ""),
        "datePublished": post["date"]["created"],
        "dateModified": post["date"]["updated"],
        "author": [{"@type": "Person", "name": author.name} for author in page.authors],
        "keywords": post["keywords"],
        "abstract": post["summary"],
        "url": post["url"],
        "mainEntityOfPage": post["url"],
    }
    if page.meta.get("image"):
        article["image"] = absolute(config, page.meta["image"])
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": number, "name": title, "item": url}
            for number, (title, url) in enumerate([
                (config["site_name"], config["site_url"].rstrip("/") + "/"),
                ("Blog", absolute(config, "blog/")),
                (post["title"], post["url"]),
            ], 1)
        ],
    }
    return [article, breadcrumb]


def on_page_context(context, page, config, **kwargs):
    _pages[page.url] = page
    context["abm_noindex"] = page.file.src_uri in EXCLUDED
    if is_post(page):
        context["abm_structured_data"] = structured_data(page, config)
        context["abm_markdown_url"] = markdown_url(page)
    return context


@event_priority(-100)
def on_post_build(config, **kwargs):
    root = Path(config["site_dir"])
    pages = list(_pages.values())
    posts = [entry(page, config) for page in pages if is_post(page)]
    posts.sort(key=lambda post: (post["date"]["created"], post["url"]), reverse=True)
    for post in posts:
        post["related_slugs"] = [
            other["slug"] for other in posts
            if other["url"] != post["url"]
            and set(post["category"]) & set(other["category"])
        ][:3]
    (root / "blog").mkdir(parents=True, exist_ok=True)
    (root / "blog/index.json").write_text(
        json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        f"# {config['site_name']}", "", f"> {config.get('site_description', '')}", "",
        "This index omits no public pages rendered by this build. Sample posts are included",
        "and labelled below; their JSON entries carry dummy: true.", "",
        "## Key sections", "",
        *[f"- [{title}]({absolute(config, path)})" for title, path in [
            ("Blog", "blog/"), ("Learn", "learn/"), ("About", "about/"),
            ("Newsletter", "newsletter/"), ("Machine-readable blog index", "blog/index.json"),
        ]], "", "## Posts (newest first)", "",
    ]
    for post in posts:
        label = " [Sample content]" if post["dummy"] else ""
        lines.append(f"- [{post['title']}]({post['url']}){label}: {' '.join(post['summary'].split())}")
    lines.extend(["", "## All other public pages", ""])
    for page in sorted(pages, key=lambda page: page.url):
        if not is_post(page):
            lines.append(f"- [{page.title}]({page.canonical_url or absolute(config, page.url)})")
    (root / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for page in pages:
        if is_post(page):
            destination = root / markdown_url(page)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(Path(page.file.abs_src_path).read_bytes())

    sitemap = root / "sitemap.xml"
    if sitemap.exists():
        tree = ET.parse(sitemap)
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        excluded = {absolute(config, path) for path in (
            "start-here/", "showcase/", "blog-authoring-guide/",
            "start-here.html", "showcase.html", "blog-authoring-guide.html",
        )}
        for node in list(tree.getroot()):
            if node.findtext("s:loc", namespaces=ns) in excluded:
                tree.getroot().remove(node)
        ET.register_namespace("", ns["s"])
        tree.write(sitemap, encoding="utf-8", xml_declaration=True)
        compressed = root / "sitemap.xml.gz"
        if compressed.exists():
            compressed.write_bytes(gzip.compress(sitemap.read_bytes(), mtime=0))
