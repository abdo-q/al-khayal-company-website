from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://al-khayal.space"

CITY_NAMES = {
    "abha": "أبها", "abu-arish": "أبو عريش", "aljouf": "الجوف", "bisha": "بيشة",
    "buraydah": "بريدة", "dammam": "الدمام", "dawadmi": "الدوادمي", "hail": "حائل",
    "jazan": "جازان", "jeddah": "جدة", "khamis-mushait": "خميس مشيط", "khobar": "الخبر",
    "madinah": "المدينة المنورة", "majmaah": "المجمعة", "makkah": "مكة المكرمة",
    "najran": "نجران", "qassim": "القصيم", "qurayyat": "القريات", "rafha": "رفحاء",
    "rass": "الرس", "riyadh": "الرياض", "sabya": "صبيا", "sakaka": "سكاكا",
    "shaqra": "شقراء", "tabuk": "تبوك", "taif": "الطائف", "turaif": "طريف",
    "unayzah": "عنيزة", "wadi-al-dawasir": "وادي الدواسر",
}

SERVICE_INFO = {
    "cleaning": ("تنظيف المنازل", "شركة تنظيف", "articles/cleaning-homes-guide.html"),
    "drain-unblocking": ("تسليك المصارف", "تسليك مجاري", "articles/drain-unblocking-guide.html"),
    "pest-control": ("مكافحة الآفات", "رش مبيدات", "articles/pest-control-guide.html"),
    "furniture-moving": ("نقل الأثاث", "نقل عفش", "articles/furniture-moving-guide.html"),
    "gas-oven-maintenance": ("صيانة أفران الغاز", "صيانة أفران الغاز", "articles/home-maintenance-guide.html"),
    "air-conditioner-maintenance": ("صيانة المكيفات", "صيانة مكيفات", "articles/ac-maintenance-guide.html"),
    "ac-filter": ("تنظيف فلاتر المكيف", "تنظيف فلاتر المكيف", "articles/ac-filter-cleaning.html"),
    "electrical": ("السلامة الكهربائية", "كهربائي منازل", "articles/electrical-safety.html"),
    "water-leak": ("معالجة تسرب المياه", "كشف تسرب المياه", "articles/water-leak.html"),
    "plumbing": ("السباكة المنزلية", "سباك منازل", "articles/plumbing-guide.html"),
    "roof-insulation": ("عزل الأسطح", "عزل أسطح", "articles/roof-insulation-guide.html"),
    "tank-cleaning": ("تنظيف خزانات المياه", "تنظيف خزانات", "articles/tank-cleaning-guide.html"),
    "home-maintenance": ("الصيانة المنزلية", "صيانة منزلية", "articles/home-maintenance-guide.html"),
}

VARIANTS = [
    "ابدأ بتصوير موضع المشكلة وكتابة ما تغيّر في الأيام الأخيرة؛ هذه المعلومة تختصر وقت المعاينة وتساعد على اختيار الأدوات المناسبة.",
    "قبل الحجز، افصل بين العمل العاجل والعمل التحسيني، وحدد ما يجب إنجازه في الزيارة الأولى حتى تكون النتيجة قابلة للمراجعة.",
    "أفضل تجهيز لهذه الخدمة هو وصف المكان بدقة: عدد الغرف أو الأجهزة، وجود أطفال أو حيوانات، وأي خامة حساسة تحتاج اختبارًا موضعيًا.",
    "لا تعتمد على اسم الخدمة وحده؛ اطلب بيانًا مختصرًا لما سيدخل في النطاق وما يحتاج زيارة فنية أو مادة خاصة قبل بدء العمل.",
    "للمقارنة بين الخيارات، سجّل الحالة قبل التنفيذ وبعده، واسأل عن وقت التجفيف أو إعادة التشغيل أو المتابعة المطلوبة بعد الزيارة.",
    "إذا تكرر العطل أو الاتساخ في الموضع نفسه، فاطلب معالجة السبب المحتمل لا تكرار الحل المؤقت، مع توثيق النتيجة بعد الانتهاء.",
    "يفيد سكان {city} أن يذكروا موقع العقار وسهولة الوصول ووقت الزيارة المناسب؛ هذه التفاصيل تغير ترتيب الأولويات في الخدمة.",
    "في {city}، اجعل الاتفاق مكتوبًا في رسالة قصيرة: الخدمة، المناطق المشمولة، المواد المستخدمة، وما الذي سيحدث إذا ظهرت ملاحظة إضافية.",
    "قبل استقبال الفني أو فريق الخدمة في {city}، أخلِ مساحة العمل من الأغراض القابلة للكسر وأبقِ تعليمات الأجهزة أو موادها الأصلية قريبة.",
    "النتيجة الجيدة في {city} لا تقاس بالسرعة فقط؛ راجع الحواف والزوايا ومكان تجمع المشكلة، ثم اطلب توضيح أي بند لم يُنفذ.",
    "عند طلب {service} في {city}، اذكر هل المكان منزل أو شقة أو مكتب، لأن طبيعة الاستخدام تؤثر في وقت التنفيذ وطريقة الحماية.",
    "هذا الدليل لا يغني عن الفحص عند وجود خطر أو تلف مخفي؛ أوقف التجربة المنزلية وسجّل العلامات التي ظهرت قبل طلب المختص في {city}.",
]


def route_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[:-10]
    return "/" + rel


def rel_href(path: Path, target: str) -> str:
    source_dir = (ROOT / path.relative_to(ROOT)).parent
    return Path(os.path.relpath(ROOT / target, source_dir)).as_posix()


def title_of(text: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else "الخيال للخدمات المنزلية"


def city_for(path: Path) -> str | None:
    stem = path.parent.name if path.name == "index.html" else path.stem
    for slug, city in CITY_NAMES.items():
        if stem.endswith("-" + slug) or stem == slug:
            return city
    return None


def service_for(path: Path) -> tuple[str, str, str]:
    stem = path.parent.name if path.name == "index.html" else path.stem
    for key, value in SERVICE_INFO.items():
        if key in stem:
            return value
    if "cleaning" in path.as_posix():
        return SERVICE_INFO["cleaning"]
    return SERVICE_INFO["home-maintenance"]


def add_head_assets(text: str) -> str:
    marker = '<link rel="icon" type="image/svg+xml" href="https://al-khayal.space/assets/favicon.svg">'
    if marker not in text:
        png = '<link rel="icon" type="image/png" sizes="96x96" href="https://al-khayal.space/assets/favicon-96.png">'
        replacement = marker + png + '<link rel="apple-touch-icon" sizes="512x512" href="https://al-khayal.space/images/logo-mark-512.png"><link rel="manifest" href="/site.webmanifest">'
        text = re.sub(r'<link rel="icon"[^>]*>', replacement, text, count=1, flags=re.I)
        if marker not in text:
            text = text.replace("</head>", replacement + "</head>", 1)
    elif 'apple-touch-icon' not in text:
        text = text.replace(marker, marker + '<link rel="icon" type="image/png" sizes="96x96" href="https://al-khayal.space/assets/favicon-96.png"><link rel="apple-touch-icon" sizes="512x512" href="https://al-khayal.space/images/logo-mark-512.png"><link rel="manifest" href="/site.webmanifest">', 1)
    return text


def keyword_links(path: Path, city: str | None, service: tuple[str, str, str], index: int) -> str:
    service_name, keyword, guide = service
    candidates = []
    if city:
        candidates.extend([
            (f"شركة تنظيف في {city}", "articles/cleaning-homes-guide.html"),
            (f"{keyword} في {city}", guide),
            (f"خدمات منزلية في {city}", "articles/home-maintenance-guide.html"),
        ])
    else:
        candidates.extend([
            (f"شركة الخيال للتنظيف", "articles/cleaning-homes-guide.html"),
            (f"شركة الخيال للصيانة المنزلية", "articles/home-maintenance-guide.html"),
            (f"{keyword} في السعودية", guide),
            (f"خدمات منزلية في السعودية", "articles/home-maintenance-guide.html"),
            (f"{service_name} للمنازل", guide),
        ])
    # Add a service keyword that does not depend on the brand name.
    candidates.append((f"{keyword} بالسعودية", guide))
    out = []
    seen = set()
    for label, target in candidates:
        href = rel_href(path, target)
        if href == path.name or href in seen:
            continue
        seen.add(href)
        out.append((label, href))
        if len(out) == 3:
            break
    links = "".join(f'<li><a class="article-keyword-link" href="{html.escape(href)}">{html.escape(label)}</a></li>' for label, href in out)
    heading = ["أدلة مرتبطة بالخدمة", "معلومات تساعدك قبل الطلب", "روابط بحثية مفيدة", "أدلة حسب الخدمة والمدينة"][index % 4]
    return f'<section class="keyword-links-section" aria-labelledby="keyword-links-title"><div class="container"><h2 id="keyword-links-title">{heading}</h2><p>اقرأ الدليل الأقرب لاحتياجك قبل تحديد الموعد والنطاق:</p><ul>{links}</ul></div></section>'


def unique_note(path: Path, city: str | None, service: tuple[str, str, str], index: int) -> str:
    service_name, keyword, _ = service
    local = city or "السعودية"
    sentence = VARIANTS[index % len(VARIANTS)].format(city=local, service=service_name)
    return f'<section class="article-unique-note" aria-labelledby="local-note-title"><h2 id="local-note-title">ملاحظة عملية لـ{html.escape(local)}</h2><p>{html.escape(sentence)}</p><p>ولطلب {html.escape(keyword)} بصورة أوضح، اذكر مساحة المكان ودرجة الاستعجال وما جُرّب سابقًا، ثم راجع بنود الخدمة قبل اعتماد الموعد.</p></section>'


def main() -> None:
    files = []
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT).as_posix()
        if "/" not in rel and re.fullmatch(r"google[a-f0-9]+\.html", rel):
            continue
        files.append(p)
    updated = 0
    article_updated = 0
    for index, path in enumerate(sorted(files, key=lambda p: p.as_posix())):
        text = path.read_text(encoding="utf-8", errors="ignore")
        original = text
        text = add_head_assets(text)
        city = city_for(path)
        service = service_for(path)
        if "keyword-links-section" not in text:
            section = keyword_links(path, city, service, index)
            text = text.replace("<footer", section + "\n<footer", 1)
        if ("/articles/" in path.as_posix() or path.parent.name.startswith("cleaning-")) and "article-unique-note" not in text:
            note = unique_note(path, city, service, index)
            if "</article>" in text:
                text = text.replace("</article>", note + "</article>", 1)
            else:
                text = text.replace("<footer", note + "\n<footer", 1)
            article_updated += 1
        if text != original:
            path.write_text(text, encoding="utf-8")
            updated += 1
    manifest = {
        "name": "الخيال للخدمات المنزلية",
        "short_name": "الخيال",
        "lang": "ar",
        "dir": "rtl",
        "start_url": "/",
        "display": "standalone",
        "theme_color": "#377d69",
        "background_color": "#fffefb",
        "icons": [
            {"src": "/images/logo-mark-128.webp", "sizes": "128x128", "type": "image/webp", "purpose": "any maskable"},
            {"src": "/images/logo-mark-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    }
    (ROOT / "site.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"updated pages: {updated}; unique article notes: {article_updated}; total pages: {len(files)}")


if __name__ == "__main__":
    main()
