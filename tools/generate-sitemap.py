#!/usr/bin/env python3
"""Generate separate XML sitemaps for public pages and their content images."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE_ORIGIN = "https://abdo-q.github.io/al-khayal-home-services/"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
IMAGE_NS = "http://www.google.com/schemas/sitemap-image/1.1"
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
        name = local_path.name.lower()
        if any(token in name for token in ("logo", "favicon", "whatsapp", "icon")):
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
    image_count = 0
    for page in pages:
        loc = page_url(page)
        ET.SubElement(ET.SubElement(page_root, f"{{{SITEMAP_NS}}}url"), f"{{{SITEMAP_NS}}}loc").text = loc
        images = content_images(page)
        if images:
            image_entry = ET.SubElement(image_root, f"{{{SITEMAP_NS}}}url")
            ET.SubElement(image_entry, f"{{{SITEMAP_NS}}}loc").text = loc
            for image_url in images:
                image = ET.SubElement(image_entry, f"{{{IMAGE_NS}}}image")
                ET.SubElement(image, f"{{{IMAGE_NS}}}loc").text = image_url
                image_count += 1

    page_path = ROOT / "sitemap.xml"
    image_path = ROOT / "image-sitemap.xml"
    save_xml(page_root, page_path)
    save_xml(image_root, image_path)
    print(f"Wrote {page_path.name}: {len(pages)} page URLs")
    print(f"Wrote {image_path.name}: {image_count} content-image entries")


if __name__ == "__main__":
    main()
