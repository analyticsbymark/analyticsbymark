from textwrap import dedent
import urllib.parse
import re
from urllib.parse import urljoin

x_intent = "https://twitter.com/intent/tweet"
fb_sharer = "https://www.facebook.com/sharer/sharer.php"
li_sharer = "https://www.linkedin.com/sharing/share-offsite/"
include = re.compile(r"blog/[1-9].*")


def on_page_markdown(markdown, **kwargs):
    page = kwargs["page"]
    config = kwargs["config"]

    if not include.match(page.url):
        return markdown

    # Prefer canonical absolute URL if available; otherwise build with site_url
    page_url = getattr(page, "canonical_url", None) or urljoin(config.site_url or "", page.url)

    # If you're serving locally and site_url isn't set, fall back to localhost so the param is present
    if not page_url or page_url.startswith("/"):
        page_url = urljoin("http://localhost:8000/", page.url)

    # Encode pieces
    encoded_url = urllib.parse.quote(page_url, safe="")
    encoded_title = urllib.parse.quote((page.title or "").strip())

    # (Optional) log to verify at build/serve time
    return markdown + dedent(f"""

    ---

    [Enjoyed this post? Get more like it in your inbox.](https://YOUR-NEWSLETTER-SIGNUP-URL-HERE){{ #post-footer-cta .md-button .md-button--primary target=_blank }}

    [Share on :simple-x:]({x_intent}?text={encoded_title}&url={encoded_url}){{ .md-button target=_blank rel=noopener }}
    [Share on :simple-facebook:]({fb_sharer}?u={encoded_url}){{ .md-button target=_blank rel=noopener }}
    [Share on :fontawesome-brands-square-linkedin:]({li_sharer}?url={encoded_url}){{ .md-button target=_blank rel=noopener }}
    """)