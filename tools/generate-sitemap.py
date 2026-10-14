#!/usr/bin/env python3
"""Generate the site's XML sitemap, including discoverable content images."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE_ORIGIN = "https://abdo-q.github.io/al-khayal-home-services/"
SITEMAP_PATH = ROOT / "sitemap.xml"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
IMAGE_NS = "http://www.google.com/schemas/sitemap-image/1.1"
ET.register_namespace("", SITEMAP_NS)
ET.register_namespace("image", IMAGE_NS)


class ImageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.images: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "img":
            return
        values = dict(attrs)
        src = (values.get("src") or "").strip()
        alt = (values.get("alt") or "").strip()
        if src:
            self.images.append((src, alt))


def page_url(page: Path) -> str:
    relative = page.relative_to(ROOT).as_posix()
    if relative == "index.html":
        return SITE_ORIGIN
    if relative.endswith("/index.html"):
        return urljoin(SITE_ORIGIN, quote(relative[: -len("index.html")], safe="/"))
    return urljoin(SITE_ORIGIN, quote(relative, safe="/"))


def content_images(page: Path) -> list[tuple[str, str]]:
    parser = ImageParser()
    parser.feed(page.read_text(encoding="utf-8", errors="replace"))
    result: dict[str, str] = {}
    for src, caption in parser.images:
        parsed = urlsplit(src)
        if parsed.scheme or parsed.netloc or src.startswith("//"):
            continue
        local_path = (page.parent / parsed.path).resolve()
        if not local_path.is_file() or not local_path.is_relative_to(ROOT):
            continue
        name = local_path.name.lower()
        # These are interface/brand controls rather than page content imagery.
        if any(token in name for token in ("logo", "favicon", "whatsapp", "icon")):
            continue
        relative = local_path.relative_to(ROOT).as_posix()
        image_url = urljoin(SITE_ORIGIN, quote(relative, safe="/"))
        result.setdefault(image_url, caption)
    return sorted(result.items())


def main() -> None:
    pages = sorted(
        page for page in ROOT.rglob("*.html")
        if ".git" not in page.relative_to(ROOT).parts
        and not page.read_text(encoding="utf-8", errors="replace").lstrip().startswith("google-site-verification:")
    )
    root = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    image_count = 0
    for page in pages:
        entry = ET.SubElement(root, f"{{{SITEMAP_NS}}}url")
        ET.SubElement(entry, f"{{{SITEMAP_NS}}}loc").text = page_url(page)
        for image_url, _caption in content_images(page):
            image = ET.SubElement(entry, f"{{{IMAGE_NS}}}image")
            ET.SubElement(image, f"{{{IMAGE_NS}}}loc").text = image_url
            image_count += 1

    ET.indent(root, space="  ")
    tree = ET.ElementTree(root)
    tree.write(SITEMAP_PATH, encoding="UTF-8", xml_declaration=True)
    print(f"Wrote {SITEMAP_PATH.relative_to(ROOT)}: {len(pages)} pages, {image_count} page-image entries")


if __name__ == "__main__":
    main()
