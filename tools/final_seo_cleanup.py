from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def set_title(text: str, title: str) -> str:
    return re.sub(r"(<title[^>]*>).*?(</title>)", lambda m: m.group(1) + html.escape(title) + m.group(2), text, count=1, flags=re.I | re.S)


def set_description(text: str, description: str) -> str:
    return re.sub(r'(<meta\s+name=["\']description["\']\s+content=["\'])(.*?)(["\'])', lambda m: m.group(1) + html.escape(description, quote=True) + m.group(3), text, count=1, flags=re.I | re.S)


def main() -> None:
    changed = 0
    # Keep city landing titles short, unique, and distinct from their H1.
    for path in sorted(ROOT.glob("cleaning-*/index.html")):
        text = path.read_text(encoding="utf-8")
        m = re.search(r"<title[^>]*>شركة تنظيف في (.+?) \|", text, re.I | re.S)
        if m:
            new = set_title(text, f"شركة تنظيف في {m.group(1).strip()} | الخيال للخدمات المنزلية")
            if new != text:
                path.write_text(new, encoding="utf-8")
                changed += 1

    # Shorter descriptions are more likely to fit Arabic result snippets.
    for path in ROOT.rglob("*.html"):
        if path.name.startswith("google"):
            continue
        text = path.read_text(encoding="utf-8")
        m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', text, re.I | re.S)
        if m and len(re.sub(r"\s+", " ", m.group(1)).strip()) > 120:
            value = re.sub(r"\s+", " ", m.group(1)).strip()
            value = value[:112].rstrip("،؛,. ") + "."
            new = set_description(text, value)
            if new != text:
                path.write_text(new, encoding="utf-8")
                changed += 1

    # The four long drain-unblocking H1s are shortened without losing search intent.
    h1s = {
        "articles/drain-unblocking-makkah.html": "تسليك مجاري في مكة: تجهيز الصرف وحلول الانسداد",
        "articles/drain-unblocking-taif.html": "تسليك مجاري في الطائف: تجهيز الصرف وحلول الانسداد",
        "articles/drain-unblocking-abha.html": "تسليك مجاري في أبها: تجهيز الصرف وحلول الانسداد",
        "articles/drain-unblocking-buraydah.html": "تسليك مجاري في بريدة: تجهيز الصرف وحلول الانسداد",
    }
    for rel, heading in h1s.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        new = re.sub(r"(<h1[^>]*>).*?(</h1>)", lambda m: m.group(1) + html.escape(heading) + m.group(2), text, count=1, flags=re.I | re.S)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1

    # Put the video SEO copy inside main so it is part of the primary document content.
    path = ROOT / "video.html"
    text = path.read_text(encoding="utf-8")
    marker = '<section class="section video-seo-copy"'
    start = text.find(marker)
    end = text.find('</section>', start) if start >= 0 else -1
    # Find the complete section by balancing section tags.
    if start >= 0:
        pos = start
        depth = 0
        close = None
        for m in re.finditer(r"<section\b|</section>", text[start:], re.I):
            token = m.group(0).lower()
            if token.startswith("<section"):
                depth += 1
            else:
                depth -= 1
                if depth == 0:
                    close = start + m.end()
                    break
        if close:
            block = text[start:close]
            text = text[:start] + text[close:]
            text = text.replace("</main>", block + "\n</main>", 1)
    text = set_description(text, "شاهد خطوات تنظيف وصيانة المنزل مع الخيال كلين، وتعرّف على الخدمات المتاحة وطرق التواصل قبل تحديد الموعد في مدينتك.")
    if text != path.read_text(encoding="utf-8"):
        path.write_text(text, encoding="utf-8")
        changed += 1

    # Use a proper heading sequence on the contact page.
    path = ROOT / "contact.html"
    text = path.read_text(encoding="utf-8")
    new = text.replace("<h3>كيف تساعدنا على خدمتك؟</h3>", "<h2>كيف تساعدنا على خدمتك؟</h2>")
    if new != text:
        path.write_text(new, encoding="utf-8")
        changed += 1

    print(f"changed={changed}")


if __name__ == "__main__":
    main()
