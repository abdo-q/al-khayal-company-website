from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://al-khayal.space"
CONTACT = ROOT / "contact.html"


def rel_href(path: Path, target: Path) -> str:
    return Path(__import__("os").path.relpath(target, path.parent)).as_posix()


def page_url(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return BASE + "/"
    if rel.endswith("/index.html"):
        return BASE + "/" + rel[:-10]
    return BASE + "/" + rel


def plain(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()


def get_title(text: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    return plain(m.group(1)) if m else "الخيال للخدمات المنزلية"


def get_h1(text: str) -> str | None:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.I | re.S)
    return plain(m.group(1)) if m else None


def shorten_description(value: str, limit: int = 155) -> str:
    value = plain(value)
    if len(value) <= limit:
        return value
    cut = value[:limit]
    for mark in (". ", "، ", "؛ ", " "):
        pos = cut.rfind(mark)
        if pos >= 90:
            return cut[:pos].rstrip("،؛,. ") + "."
    return cut.rstrip("،؛,. ") + "…"


def image_alt(src: str, context: str) -> str:
    name = Path(src.split("?")[0]).stem.lower()
    mapping = {
        "logo-mark-128": "شعار الخيال للخدمات المنزلية",
        "logo-mark-512": "شعار الخيال للخدمات المنزلية",
        "whatsapp-icon": "أيقونة واتساب",
        "home-services-hero-wide": "فني صيانة منزلية يعمل داخل منزل",
        "about-hero": "مشهد توضيحي لخدمات الخيال المنزلية",
        "about-ac-filter": "تنظيف فلتر مكيف منزلي",
        "ac-service": "فني صيانة تكييف منزلي",
        "article-ac-filter": "تنظيف فلتر المكيف",
        "article-electrical-safety": "فحص لوحة كهرباء منزلية بأمان",
        "article-city": "خدمة منزلية في المدينة",
    }
    if name in mapping:
        return mapping[name]
    if name.startswith("phone-contact"):
        return "أيقونة الاتصال"
    if name.startswith("article-"):
        label = name.removeprefix("article-").replace("-", " ")
        return f"صورة توضيحية لخدمة {label}"
    if name.startswith("service-"):
        label = name.removeprefix("service-").replace("-", " ")
        return f"صورة توضيحية لخدمة {label}"
    return f"صورة توضيحية لخدمات الخيال المنزلية — {context[:70]}"


def add_alt_attributes(text: str, path: Path) -> tuple[str, int]:
    h1 = get_h1(text) or "الخدمات المنزلية"
    changed = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal changed
        tag = m.group(0)
        if re.search(r"aria-hidden=[\"']true[\"']", tag, re.I):
            return tag
        src_m = re.search(r"\bsrc=[\"']([^\"']+)[\"']", tag, re.I)
        src = src_m.group(1) if src_m else ""
        alt_m = re.search(r"\balt=[\"']([^\"']*)[\"']", tag, re.I)
        if alt_m and alt_m.group(1).strip():
            return tag
        alt = html.escape(image_alt(src, h1), quote=True)
        if alt_m:
            tag = tag[:alt_m.start(1)] + alt + tag[alt_m.end(1):]
        else:
            tag = tag[:-1] + f' alt="{alt}">'
        changed += 1
        return tag

    return re.sub(r"<img\b[^>]*>", repl, text, flags=re.I), changed


def add_schema(text: str, path: Path) -> tuple[str, bool]:
    if re.search(r'application/ld\+json', text, re.I):
        return text, False
    url = page_url(path)
    title = get_title(text)
    if path.name == "contact.html":
        schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "@id": BASE + "/#business",
            "name": "الخيال للخدمات المنزلية",
            "url": BASE + "/",
            "telephone": "+966552610151",
            "image": BASE + "/images/logo-mark-512.png",
            "priceRange": "$$",
            "areaServed": "المملكة العربية السعودية",
            "contactPoint": {"@type": "ContactPoint", "telephone": "+966552610151", "contactType": "customer service", "availableLanguage": ["ar"]},
        }
    elif path.name == "about.html" or path.name == "services.html":
        schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "@id": BASE + "/#business",
            "name": "الخيال للخدمات المنزلية",
            "url": BASE + "/",
            "telephone": "+966552610151",
            "image": BASE + "/images/logo-mark-512.png",
            "description": "خدمات تنظيف وصيانة منزلية ومكافحة آفات بحسب المدينة ونطاق الخدمة.",
            "areaServed": "المملكة العربية السعودية",
        }
    elif path.name == "video.html" or path.name == "articles.html":
        schema = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": title,
            "url": url,
            "isPartOf": {"@type": "WebSite", "name": "الخيال للخدمات المنزلية", "url": BASE + "/"},
        }
    else:
        return text, False
    block = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + "</script>\n"
    return text.replace("</head>", block + "</head>", 1), True


def update_meta_and_titles(text: str) -> tuple[str, int, int]:
    title_changes = 0
    desc_changes = 0
    h1 = get_h1(text)
    title = get_title(text)
    if h1 and plain(title).casefold() == plain(h1).casefold():
        new_title = title + " | الخيال للخدمات المنزلية"
        text = re.sub(r"(<title[^>]*>).*?(</title>)", lambda m: m.group(1) + html.escape(new_title) + m.group(2), text, count=1, flags=re.I | re.S)
        title_changes += 1
    def desc_repl(m: re.Match[str]) -> str:
        nonlocal desc_changes
        old = m.group(2)
        new = shorten_description(old)
        if new != plain(old):
            desc_changes += 1
        return m.group(1) + html.escape(new, quote=True) + m.group(3)
    text = re.sub(r'(<meta\s+name=["\']description["\']\s+content=["\'])(.*?)(["\'])', desc_repl, text, count=1, flags=re.I | re.S)
    return text, title_changes, desc_changes


def contact_target(path: Path) -> str:
    return rel_href(path, CONTACT)


def update_contact_links(text: str, path: Path) -> str:
    target = html.escape(contact_target(path), quote=True)
    # The prominent CTA and the first fixed contact button always open the contact page.
    text = re.sub(r'(<a\s+class=["\']nav-cta["\'][^>]*\bhref=["\'])([^"\']+)(["\'])', r'\g<1>' + target + r'\3', text, count=1, flags=re.I)
    text = re.sub(r'(<aside\s+class=["\']floating-contact["\'][\s\S]*?<a\s+)([^>]*?\bhref=["\'])(?:tel:[^"\']+)(["\'])', r'\g<1>\g<2>' + target + r'\3', text, count=1, flags=re.I)
    text = text.replace('aria-label="اتصال هاتفي على 055 261 0151"', 'aria-label="فتح صفحة الاتصال"', 1) if 'floating-contact' in text else text
    return text


def remove_contact_form(text: str, path: Path) -> tuple[str, bool]:
    if path.name != "contact.html":
        return text, False
    pattern = r'<form\s+class=["\']contact-form[\s\S]*?</form>'
    replacement = '''<section class="contact-direct reveal" aria-labelledby="contact-direct-title"><h2 id="contact-direct-title">تواصل مباشرة مع الخيال كلين</h2><p>للاستفسار عن التنظيف أو الصيانة أو مكافحة الآفات، اتصل بنا أو افتح واتساب. اذكر المدينة ونوع الخدمة وتفاصيل الطلب، وسنراجع نطاق التغطية معك قبل تحديد الموعد.</p><div class="contact-direct-actions"><a class="button" href="tel:+966552610151">اتصال هاتفي</a><a class="button button-secondary" href="https://wa.me/966552610151" target="_blank" rel="noopener noreferrer">واتساب</a></div><p class="form-note">لا يتم إرسال أي بيانات عبر الموقع؛ التواصل يتم مباشرة عبر الهاتف أو واتساب.</p></section>'''
    new, count = re.subn(pattern, replacement, text, count=1, flags=re.I)
    return new, bool(count)


def enrich_thin_pages(text: str, path: Path) -> str:
    if path.name == "video.html" and "video-seo-copy" not in text:
        block = '''<section class="section video-seo-copy" aria-labelledby="video-seo-title"><div class="container"><div class="section-heading"><span class="eyebrow"><span class="eyebrow-dot"></span> معرفة قبل الطلب</span><h2 id="video-seo-title">شاهد طريقة العناية بالخدمة المنزلية</h2><p>توضح المقاطع خطوات التنظيف والصيانة والعناية بالمكان قبل بدء العمل. اذكر المدينة ونوع الخدمة عند التواصل حتى نتحقق من التوفر ونقترح الخطوة المناسبة.</p></div><div class="content-grid"><article class="info-card"><h3>تنظيف أدق</h3><p>ابدأ بوصف نوع السطح أو الأثاث والمساحة، واذكر أي خامة حساسة تحتاج اختبارًا موضعيًا.</p></article><article class="info-card"><h3>صيانة أوضح</h3><p>في أعمال التكييف والسباكة والكهرباء، اذكر العلامات التي ظهرت وما جُرّب سابقًا لتسهيل التقييم الأولي.</p></article><article class="info-card"><h3>تواصل مباشر</h3><p>بعد مشاهدة المقطع، اتصل بالخيال أو راسلنا عبر واتساب لتأكيد نطاق الخدمة والموعد.</p></article></div></div></section>\n'''
        text = text.replace("<footer", block + "<footer", 1)
    return text


def main() -> None:
    files = sorted(ROOT.rglob("*.html"))
    stats = {"pages": 0, "alt": 0, "schema": 0, "title": 0, "description": 0, "contact_form": 0}
    for path in files:
        if path.name.startswith("google"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        original = text
        text, n_alt = add_alt_attributes(text, path)
        text, n_schema = add_schema(text, path)
        text, n_title, n_desc = update_meta_and_titles(text)
        text = update_contact_links(text, path)
        text, n_form = remove_contact_form(text, path)
        text = enrich_thin_pages(text, path)
        if text != original:
            path.write_text(text, encoding="utf-8")
        stats["pages"] += 1
        stats["alt"] += n_alt
        stats["schema"] += int(n_schema)
        stats["title"] += n_title
        stats["description"] += n_desc
        stats["contact_form"] += int(n_form)
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
