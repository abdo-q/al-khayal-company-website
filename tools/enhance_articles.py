from pathlib import Path
import re, shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / 'images'
SEARCH = Path('/home/ubuntu/upload/search_images')

# Photos found through Unsplash free-image collections; resized and stored locally.
STOCK = {
    'stock-cleaning-unsplash.webp': ('zChRcuHwpRQ5.jpg', 1600),
    'stock-hvac-unsplash.webp': ('hoN03mxECcHM.jpg', 1600),
    'stock-pipe-unsplash.webp': ('gTgkbLtnLPR6.jpg', 1600),
}
for out, (source, width) in STOCK.items():
    target = IMG / out
    if not target.exists():
        with Image.open(SEARCH / source) as im:
            im = im.convert('RGB')
            ratio = width / im.width
            im = im.resize((width, round(im.height * ratio)), Image.Resampling.LANCZOS)
            im.save(target, 'WEBP', quality=82, method=6)

category_cover = {
    'cleaning-': ('images/stock-cleaning-unsplash.webp', 'تنظيف منزل بطريقة منظمة'),
    'air-conditioner-maintenance': ('images/stock-hvac-unsplash.webp', 'فني يفحص وحدة تكييف منزلية'),
    'drain-unblocking': ('images/stock-pipe-unsplash.webp', 'فني يفحص أنابيب المياه أسفل المغسلة'),
    'furniture-moving': ('images/article-new-01.webp', 'تجهيز الأثاث للنقل بطريقة منظمة'),
    'gas-oven-maintenance': ('images/article-web-01.webp', 'فحص جهاز منزلي وصيانته'),
    'pest-control': ('images/article-new-05.webp', 'إرشادات عامة للعناية المنزلية'),
}

def abs_url(src: str, depth: int) -> str:
    src = src.replace('../', '')
    return 'https://abdo-q.github.io/al-khayal-home-services/' + src

def add_meta(html: str, image_url: str, alt: str) -> str:
    html = re.sub(r'(<meta name="twitter:card" content=")[^"]+', r'\g<1>summary_large_image', html, count=1)
    if 'property="og:image"' not in html:
        html = html.replace('<meta property="og:site_name"', f'<meta property="og:image" content="{image_url}"><meta property="og:image:alt" content="{alt}"><meta property="og:site_name"', 1)
    elif 'property="og:image:alt"' not in html:
        html = html.replace('<meta property="og:site_name"', f'<meta property="og:image:alt" content="{alt}"><meta property="og:site_name"', 1)
    if 'name="twitter:image"' not in html:
        html = html.replace('</head>', f'<meta name="twitter:image" content="{image_url}"><meta name="twitter:image:alt" content="{alt}">\n</head>', 1)
    elif 'name="twitter:image:alt"' not in html:
        html = html.replace('</head>', f'<meta name="twitter:image:alt" content="{alt}">\n</head>', 1)
    # Add an image to Article JSON-LD when the existing schema omitted it.
    if '"@type":"Article"' in html or '"@type": "Article"' in html:
        first = html.find('<script type="application/ld+json">')
        end = html.find('</script>', first)
        if first >= 0 and end > first:
            block = html[first:end]
            if '"image"' not in block:
                block = block.replace('"datePublished"', f'"image":"{image_url}","datePublished"', 1)
                html = html[:first] + block + html[end:]
    return html

def add_cover(html: str, src: str, alt: str, depth: int) -> str:
    if 'class="article-cover' in html:
        return html
    rel = ('../' * depth) + src
    img = f'<img class="article-cover article-cover-detail" src="{rel}" alt="{alt}" width="1200" height="675" fetchpriority="high" decoding="async">\n'
    marker = '<article class="article-detail reveal">'
    return html.replace(marker, marker + img, 1)

# All article routes: improve social previews and guarantee a useful image for crawlers.
files = sorted(ROOT.glob('articles/*.html')) + sorted(ROOT.glob('cleaning-*/index.html'))
changed = 0
for path in files:
    html = path.read_text(encoding='utf-8')
    depth = len(path.relative_to(ROOT).parts) - 1
    rel_name = path.stem if path.parent.name == 'articles' else path.parent.name
    mapping = None
    for prefix, value in category_cover.items():
        if rel_name.startswith(prefix):
            mapping = value
            break
    if mapping:
        src, alt = mapping
        html = add_cover(html, src, alt, depth)
    # Locate the first cover after insertion, otherwise use a stable category fallback.
    match = re.search(r'<img[^>]+class="article-cover[^>]+src="([^"]+)"[^>]*alt="([^"]*)"', html)
    if not match and mapping:
        src, alt = mapping
        image_url = abs_url(src, depth)
    elif match:
        image_url = abs_url(match.group(1), depth)
        alt = match.group(2) or 'صورة توضيحية من مقال الخيال للخدمات المنزلية'
    else:
        image_url = 'https://abdo-q.github.io/al-khayal-home-services/images/article-city-riyadh.webp'
        alt = 'صورة توضيحية لمقال خدمات منزلية'
    html = add_meta(html, image_url, alt)
    # Mark non-hero images as async where the attribute is absent.
    html = re.sub(r'(<img(?![^>]*class="article-cover)[^>]*)(?<!/)>', lambda m: m.group(1) + ' loading="lazy" decoding="async">' if 'loading=' not in m.group(1) else m.group(0), html)
    if html != path.read_text(encoding='utf-8'):
        path.write_text(html, encoding='utf-8')
        changed += 1

# Use the new stock photos on the three evergreen guides as visible, relevant covers.
replacements = {
    ROOT / 'articles/ac-filter-cleaning.html': ('../images/stock-hvac-unsplash.webp', 'فني يفحص وحدة تكييف منزلية قبل الصيانة'),
    ROOT / 'articles/water-leak.html': ('../images/stock-pipe-unsplash.webp', 'فني يفحص أنابيب المياه أسفل المغسلة'),
    ROOT / 'cleaning-riyadh/index.html': ('../images/stock-cleaning-unsplash.webp', 'تنظيف منزل بطريقة منظمة'),
}
for path, (src, alt) in replacements.items():
    html = path.read_text(encoding='utf-8')
    html = re.sub(r'(<img[^>]+class="article-cover article-cover-detail"[^>]+src=")[^"]+("[^>]+alt=")[^"]+("[^>]*>)', rf'\g<1>{src}\g<2>{alt}\g<3>', html, count=1)
    image_url = 'https://abdo-q.github.io/al-khayal-home-services/' + src.replace('../', '')
    html = re.sub(r'(<meta property="og:image" content=")[^"]+', rf'\g<1>{image_url}', html, count=1)
    html = re.sub(r'(<meta name="twitter:image" content=")[^"]+', rf'\g<1>{image_url}', html, count=1)
    first = html.find('<script type="application/ld+json">')
    end = html.find('</script>', first)
    if first >= 0 and end > first:
        block = html[first:end]
        block = re.sub(r'("image"\s*:\s*")[^"]+', rf'\g<1>{image_url}', block, count=1)
        html = html[:first] + block + html[end:]
    path.write_text(html, encoding='utf-8')

sources = ROOT / 'image-sources.md'
sources.write_text('''# مصادر الصور\n\nتم تنزيل الصور التالية من صفحات البحث المجانية في Unsplash، ثم ضغطها محليًا بصيغة WebP لاستخدامها داخل الموقع. وفق [ترخيص Unsplash](https://unsplash.com/license) يمكن استخدام الصور المنشورة على Unsplash مجانًا للأغراض التجارية وغير التجارية. أُبقيت روابط المصدر هنا للتوثيق، مع تجنب الصور التي تحمل علامات مائية.\n\n- `images/stock-cleaning-unsplash.webp` — [صور تنظيف المنازل على Unsplash](https://unsplash.com/s/photos/house-cleaning) — تستخدم في دليل التنظيف.\n- `images/stock-hvac-unsplash.webp` — [صور فنيي التكييف على Unsplash](https://unsplash.com/s/photos/hvac-technician) — تستخدم في دليل فلتر المكيف وصفحات صيانة التكييف.\n- `images/stock-pipe-unsplash.webp` — [صور تسرب وإصلاح الأنابيب على Unsplash](https://unsplash.com/s/photos/pipe-leak) — تستخدم في دليل تسرب المياه وصفحات تسليك المجاري.\n\n> الصور مجانية الاستخدام وفق الترخيص المذكور، لكن لا يعني ذلك أنها ملكية عامة؛ لذلك يجب الاحتفاظ بهذا السجل عند نقل الموقع أو إعادة استخدام الأصول.\n''', encoding='utf-8')
print(f'updated {changed} article pages; added {len(STOCK)} local stock assets')
