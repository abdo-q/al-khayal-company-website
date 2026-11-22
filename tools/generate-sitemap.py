#!/usr/bin/env python3
"""Generate canonical page, image, and sitemap-index XML for the static site."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE_ORIGIN = "https://al-khayal.space/"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
IMAGE_NS = "http://www.google.com/schemas/sitemap-image/1.1"
ET.register_namespace("", SITEMAP_NS)
ET.register_namespace("image", IMAGE_NS)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sources: list[str] = []
        self.canonical: str | None = None
        self.noindex = False
        self.container_stack: list[tuple[str, bool]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        tag = tag.lower()
        classes = set((values.get("class") or "").lower().split())
        if tag in {"div", "figure", "section"}:
            hidden = values.get("aria-hidden", "").lower() == "true" or "article-decoration" in classes
            self.container_stack.append((tag, hidden))

        if tag == "img" and not any(hidden for _, hidden in self.container_stack):
            src = (values.get("src") or "").strip()
            alt = (values.get("alt") or "").strip()
            filename = Path(urlsplit(src).path).name.lower()
            if (
                src
                and alt
                and not filename.endswith(".svg")
                and not any(token in filename for token in ("logo", "phone", "whatsapp", "icon"))
                and not classes.intersection({"phone-contact-icon", "logo", "brand-logo"})
            ):
                self.sources.append(src)
        elif tag == "link" and "canonical" in (values.get("rel") or "").lower().split():
            self.canonical = (values.get("href") or "").strip()
        elif tag == "meta" and (values.get("name") or "").lower() in {"robots", "googlebot"}:
            self.noindex = "noindex" in (values.get("content") or "").lower()

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag not in {"div", "figure", "section"}:
            return
        for index in range(len(self.container_stack) - 1, -1, -1):
            if self.container_stack[index][0] == tag:
                del self.container_stack[index:]
                return


def page_url(page: Path) -> str:
    relative = page.relative_to(ROOT).as_posix()
    if relative == "index.html":
        return SITE_ORIGIN
    if relative.endswith("/index.html"):
        relative = relative[: -len("index.html")]
    return urljoin(SITE_ORIGIN, quote(relative, safe="/"))


def canonical_matches(canonical: str | None, expected: str) -> bool:
    if not canonical:
        return False
    actual_parts = urlsplit(canonical)
    expected_parts = urlsplit(expected)
    return (
        actual_parts.scheme == "https"
        and actual_parts.netloc.lower() == urlsplit(SITE_ORIGIN).netloc.lower()
        and actual_parts.path.rstrip("/") == expected_parts.path.rstrip("/")
        and not actual_parts.query
        and not actual_parts.fragment
    )


def content_images(page: Path, parser: PageParser) -> list[str]:
    result: set[str] = set()
    for src in parser.sources:
        parsed = urlsplit(src)
        if parsed.scheme or parsed.netloc or src.startswith("//"):
            continue
        local_path = (page.parent / parsed.path).resolve()
        if not local_path.is_file() or not local_path.is_relative_to(ROOT):
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
        if ".git" not in page.relative_to(ROOT).parts and not page.name.startswith("google")
    )
    page_root = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    image_root = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    image_associations = 0
    eligible_pages = 0

    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        if text.lstrip().startswith("google-site-verification:"):
            continue
        parser = PageParser()
        parser.feed(text)
        if parser.noindex:
            continue
        loc = page_url(page)
        if not canonical_matches(parser.canonical, loc):
            continue

        eligible_pages += 1
        page_entry = ET.SubElement(page_root, f"{{{SITEMAP_NS}}}url")
        ET.SubElement(page_entry, f"{{{SITEMAP_NS}}}loc").text = loc

        images = content_images(page, parser)
        if images:
            image_entry = ET.SubElement(image_root, f"{{{SITEMAP_NS}}}url")
            ET.SubElement(image_entry, f"{{{SITEMAP_NS}}}loc").text = loc
            for image_url in images:
                image = ET.SubElement(image_entry, f"{{{IMAGE_NS}}}image")
                ET.SubElement(image, f"{{{IMAGE_NS}}}loc").text = image_url
                image_associations += 1

    save_xml(page_root, ROOT / "pages-sitemap.xml")
    save_xml(image_root, ROOT / "image-sitemap.xml")

    index_root = ET.Element(f"{{{SITEMAP_NS}}}sitemapindex")
    for name in ("pages-sitemap.xml", "image-sitemap.xml"):
        item = ET.SubElement(index_root, f"{{{SITEMAP_NS}}}sitemap")
        ET.SubElement(item, f"{{{SITEMAP_NS}}}loc").text = urljoin(SITE_ORIGIN, name)
    save_xml(index_root, ROOT / "sitemap.xml")

    print("Wrote sitemap.xml index with 2 child sitemaps")
    print(f"Wrote pages-sitemap.xml: {eligible_pages} canonical indexable pages")
    print(f"Wrote image-sitemap.xml: {image_associations} page-image associations")


if __name__ == "__main__":
    main()
