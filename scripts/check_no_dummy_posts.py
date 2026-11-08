"""Reject sample blog posts before a production build."""

import argparse
from pathlib import Path

import yaml


def dummy_posts(posts_dir):
    found = []
    for path in sorted(Path(posts_dir).rglob("*.md")):
        text = path.read_text(encoding="utf-8-sig")
        if text.startswith("---\n"):
            parts = text.split("---", 2)
            meta = yaml.safe_load(parts[1]) or {}
            if meta.get("dummy") is True:
                found.append(path)
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("posts_dir", nargs="?", default="website/docs/blog/posts")
    args = parser.parse_args(argv)
    found = dummy_posts(args.posts_dir)
    if found:
        print("Production blocked: remove sample posts before publishing:")
        for path in found:
            print(f"  {path}")
        return 1
    print("No dummy posts found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
