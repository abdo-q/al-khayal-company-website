#!/usr/bin/env python3
"""Generate a page sitemap and a focused sitemap for eight content images."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE_ORIGIN = "https://al-khayal.space/"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
IMAGE_NS = "http://www.google.com/schemas/sitemap-image/1.1"
INDEXED_IMAGE_FILENAMES = {
    "home-services-hero.jpg",
    "stock-cleaning-unsplash.webp",
    "stock-hvac-unsplash.webp",
    "stock-pipe-unsplash.webp",
    "stock-electrical-unsplash.webp",
    "article-new-01.webp",
    "article-new-05.webp",
    "article-web-01.webp",
}
ET.register_namespace("", SITEMAP_NS)
ET.register_namespace("image", IMAGE_NS)


class ImageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sources: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "img":
            src = (dict(attrs).get("src") or "").strip()
            if src:
                self.sources.append(src)


def page_url(page: Path) -> str:
    relative = page.relative_to(ROOT).as_posix()
    if relative == "index.html":
        return SITE_ORIGIN
    if relative.endswith("/index.html"):
        relative = relative[: -len("index.html")]
    return urljoin(SITE_ORIGIN, quote(relative, safe="/"))


def content_images(page: Path) -> list[str]:
    parser = ImageParser()
    parser.feed(page.read_text(encoding="utf-8", errors="replace"))
    result: set[str] = set()
    for src in parser.sources:
        parsed = urlsplit(src)
        if parsed.scheme or parsed.netloc or src.startswith("//"):
            continue
        local_path = (page.parent / parsed.path).resolve()
        if not local_path.is_file() or not local_path.is_relative_to(ROOT):
            continue
        if local_path.name not in INDEXED_IMAGE_FILENAMES:
            continue
        relative = local_path.relative_to(ROOT).as_posix()
        result.add(urljoin(SITE_ORIGIN, quote(relative, safe="/")))
    return sorted(result)


def save_xml(root: ET.Element, path: Path) -> None:
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(path, encoding="UTF-8", xml_declaration=True)


def main() -> None:
    pages = sorted(
        page for page in ROOT.rglob("*.html")
        if ".git" not in page.relative_to(ROOT).parts
        and not page.read_text(encoding="utf-8", errors="replace").lstrip().startswith("google-site-verification:")
    )

    page_root = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    image_root = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    indexed_images: set[str] = set()
    for page in pages:
        loc = page_url(page)
        ET.SubElement(ET.SubElement(page_root, f"{{{SITEMAP_NS}}}url"), f"{{{SITEMAP_NS}}}loc").text = loc
        new_images = [image for image in content_images(page) if image not in indexed_images]
        if new_images:
            image_entry = ET.SubElement(image_root, f"{{{SITEMAP_NS}}}url")
            ET.SubElement(image_entry, f"{{{SITEMAP_NS}}}loc").text = loc
            for image_url in new_images:
                image = ET.SubElement(image_entry, f"{{{IMAGE_NS}}}image")
                ET.SubElement(image, f"{{{IMAGE_NS}}}loc").text = image_url
                indexed_images.add(image_url)

    save_xml(page_root, ROOT / "sitemap.xml")
    save_xml(page_root, ROOT / "pages-sitemap.xml")
    save_xml(image_root, ROOT / "image-sitemap.xml")
    print(f"Wrote sitemap.xml: {len(pages)} page URLs")
    print(f"Wrote pages-sitemap.xml: {len(pages)} page URLs")
    print(f"Wrote image-sitemap.xml: {len(indexed_images)} selected image URLs")


if __name__ == "__main__":
    main()
