"""Blog publishing contracts; disposable content stays outside the repository."""

import gzip
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import unquote, urlsplit

import pytest
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "website/docs"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hook = load_module("blog_agents", ROOT / "hooks/blog_agents.py")
guard = load_module("dummy_guard", ROOT / "scripts/check_no_dummy_posts.py")


def front_matter(path):
    text = path.read_text(encoding="utf-8-sig")
    assert text.startswith("---\n"), path
    _, header, body = re.split(r"^---\s*$", text, maxsplit=2, flags=re.M)
    return yaml.safe_load(header), body


POSTS = sorted((DOCS / "blog/posts").glob("*.md"))


@pytest.mark.parametrize("path", POSTS or [None], ids=lambda path: path.name if path else "empty")
def test_post_front_matter(path):
    if path is None:
        pytest.skip("Builder B has not supplied posts yet")
    meta, body = front_matter(path)
    required = {
        "date", "categories", "tags", "slug", "description", "keywords",
        "summary", "key_points", "prerequisites", "image", "dummy", "authors",
    }
    assert required <= meta.keys(), path
    assert 120 <= len(meta["description"]) <= 170, path
    assert len(meta["keywords"]) >= 2
    assert all(isinstance(keyword, str) and keyword.strip() for keyword in meta["keywords"])
    assert meta["summary"].strip()
    assert 3 <= len(meta["key_points"]) <= 5
    assert 0 <= len(meta["prerequisites"]) <= 3
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", meta["slug"])
    assert {"created", "updated"} <= meta["date"].keys()
    for value in meta["date"].values():
        datetime.fromisoformat(str(value))
    allowed = {"Data Engineering", "Analytics", "APIs", "Actuarial", "AI Agents"}
    assert len(meta["categories"]) == 1 and set(meta["categories"]) <= allowed
    assert (DOCS / meta["image"]).is_file(), meta["image"]
    body_without_code = re.sub(r"^(`{3,}|~{3,}).*?^\1\s*$", "", body, flags=re.M | re.S)
    assert len(re.findall(r"^#\s+\S", body_without_code, re.M)) == 1
    authors = yaml.safe_load((DOCS / "blog/.authors.yml").read_text())["authors"]
    assert meta["authors"] and set(meta["authors"]) <= authors.keys()
    if meta["dummy"]:
        assert '!!! note "Sample post"' in body or re.search(
            r'!!! \w+ ["\']Sample post["\']', body
        )
    # Inline Markdown and reference links, including images. Code is not a link.
    links = re.findall(r"!?\[[^\]]*\]\(\s*<?([^\s)>]+)>?", body_without_code)
    links += re.findall(r"^\s*\[[^\]]+\]:\s*<?([^\s>]+)", body_without_code, re.M)
    for link in links:
        target = urlsplit(link)
        if target.scheme or target.netloc or not target.path:
            continue
        relative = unquote(target.path)
        resolved = DOCS / relative.lstrip("/") if relative.startswith("/") else path.parent / relative
        candidates = [resolved, resolved / "index.md", resolved.with_suffix(".md")]
        assert any(candidate.exists() for candidate in candidates), f"{path.name}: {link}"


def post(tmp_path, slug="example", year=2025, dummy=True):
    source = tmp_path / f"{slug}.md"
    source.write_text("---\ndummy: true\n---\n# Original Markdown\n", encoding="utf-8")
    created = datetime(year, 1, 2, tzinfo=timezone.utc)
    return SimpleNamespace(
        title='A "quoted" </script> & useful title',
        url=f"blog/{year}/01/02/{slug}/",
        canonical_url=f"https://example.test/blog/{year}/01/02/{slug}/",
        meta={
            "template": "blog-post.html", "slug": slug, "categories": ["Analytics"],
            "tags": ["charts"], "keywords": ["primary", "secondary"],
            "summary": "Two factual sentences. A concrete summary.",
            "description": 'A "description" < & >', "dummy": dummy,
            "image": "assets/images/blog/example.webp", "series": "Charts",
            "series_part": 1, "series_total": 2, "start_here": True,
        },
        file=SimpleNamespace(
            src_uri=f"blog/posts/{slug}.md", abs_src_path=str(source),
            dest_uri=f"blog/{year}/01/02/{slug}/index.html",
        ),
        config=SimpleNamespace(date=SimpleNamespace(created=created, updated=None)),
        authors=[SimpleNamespace(name='Sample "Author"')],
    )


@pytest.fixture
def config(tmp_path):
    root = tmp_path / "site"
    root.mkdir()
    return {
        "site_dir": str(root), "site_url": "https://example.test/",
        "site_name": "Example", "site_description": "Practical notes.",
    }


def test_resources_include_samples_all_pages_and_original_markdown(tmp_path, config):
    hook.on_pre_build()
    older = post(tmp_path, "older", 2024, dummy=False)
    newer = post(tmp_path, "newer", 2026)
    public = SimpleNamespace(
        title="Showcase", url="showcase/", canonical_url="https://example.test/showcase/",
        meta={}, file=SimpleNamespace(src_uri="showcase.md"),
    )
    for page in (older, public, newer):
        context = hook.on_page_context({}, page, config)
        if page is public:
            assert context["abm_noindex"]
        else:
            assert context["abm_markdown_url"].endswith("index.md")
    hook.on_post_build(config)
    root = Path(config["site_dir"])
    entries = json.loads((root / "blog/index.json").read_text())
    assert [entry["slug"] for entry in entries] == ["newer", "older"]
    assert entries[0]["dummy"] is True and entries[1]["dummy"] is False
    assert entries[0]["related_slugs"] == ["older"]
    assert entries[0]["date"]["updated"] == entries[0]["date"]["created"]
    assert entries[0]["series"] == "Charts" and entries[0]["series_part"] == 1
    assert entries[0]["category"] == ["Analytics"] and entries[0]["keywords"][0] == "primary"
    llms = (root / "llms.txt").read_text()
    assert "[Sample content]" in llms and "omits no public pages" in llms
    assert public.canonical_url in llms and newer.meta["summary"] in llms
    assert llms.index(newer.canonical_url) < llms.index(older.canonical_url)
    assert (root / hook.markdown_url(newer)).read_bytes() == Path(newer.file.abs_src_path).read_bytes()


def test_empty_resources(config):
    hook.on_pre_build()
    hook.on_post_build(config)
    assert json.loads((Path(config["site_dir"]) / "blog/index.json").read_text()) == []
    assert (Path(config["site_dir"]) / "llms.txt").is_file()


def test_json_ld_escapes_and_parses(tmp_path, config):
    page = post(tmp_path)
    context = hook.on_page_context({}, page, config)
    env = Environment(
        loader=FileSystemLoader(ROOT / "website/overrides"),
        autoescape=select_autoescape(["html"]),
    )
    rendered = env.get_template("partials/abm-seo.html").render(page=page, **context)
    scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', rendered, re.S)
    assert len(scripts) == 2
    article, breadcrumb = [json.loads(script) for script in scripts]
    assert article["@type"] == "BlogPosting" and article["headline"] == page.title
    assert article["abstract"] == page.meta["summary"]
    assert article["author"][0]["name"] == page.authors[0].name
    assert article["image"] == "https://example.test/assets/images/blog/example.webp"
    assert breadcrumb["itemListElement"][2]["item"] == page.canonical_url
    assert "\\u003c/script\\u003e" in rendered
    assert 'content="A &#34;description&#34; &lt; &amp; &gt;"' in rendered
    nonpost = env.get_template("partials/abm-seo.html").render(abm_noindex=False)
    assert "BlogPosting" not in nonpost


def test_summary_is_optional_collapsed_and_escaped():
    env = Environment(loader=FileSystemLoader(ROOT / "website/overrides"), autoescape=True)
    template = env.get_template("partials/abm-agent-summary.html")
    assert "<details" not in template.render(page=SimpleNamespace(meta={}))
    rendered = template.render(page=SimpleNamespace(meta={
        "summary": "<unsafe>", "key_points": ["First"], "prerequisites": ["Python"],
    }))
    assert "<details" in rendered and " open" not in rendered
    assert "&lt;unsafe&gt;" in rendered and "Prerequisites" in rendered


def test_sitemap_and_gzip_exclusions(config):
    root = Path(config["site_dir"])
    xml = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(
        f"<url><loc>https://example.test/{path}/</loc></url>"
        for path in ("start-here", "showcase", "blog-authoring-guide", "blog")
    ) + "</urlset>"
    (root / "sitemap.xml").write_text(xml)
    (root / "sitemap.xml.gz").write_bytes(gzip.compress(xml.encode()))
    hook.on_pre_build()
    hook.on_post_build(config)
    result = (root / "sitemap.xml").read_bytes()
    assert b"start-here" not in result and b"showcase" not in result
    assert b"blog-authoring-guide" not in result and b"/blog/" in result
    assert gzip.decompress((root / "sitemap.xml.gz").read_bytes()) == result


def test_guard_rejects_flag_only_and_handles_crlf(tmp_path):
    assert guard.main([str(tmp_path)]) == 0
    (tmp_path / "real.md").write_text("---\ndummy: false\n---\ndummy: true\n")
    assert guard.main([str(tmp_path)]) == 0
    (tmp_path / "sample.md").write_bytes(b"---\r\ndummy: true\r\n---\r\n# Sample\r\n")
    assert guard.main([str(tmp_path)]) == 1


def test_guard_is_production_only():
    workflow = (ROOT / ".github/workflows/build.yml").read_text()
    step = workflow.split("- name: Reject dummy posts on production", 1)[1].split("- name:", 1)[0]
    assert "github.ref_name == 'master'" in step
    assert "github.event_name != 'pull_request'" in step
    assert "scripts/check_no_dummy_posts.py" in step
