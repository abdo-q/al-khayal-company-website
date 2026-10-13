from pathlib import Path
from PIL import Image
import re

ROOT = Path(__file__).resolve().parents[1]
SEARCH = Path('/home/ubuntu/upload/search_images')
IMG = ROOT / 'images'

assets = {
    'stock-moving-unsplash.webp': ('71SXgCNFPVSK.jpg', 'moving boxes'),
    'stock-oven-unsplash.webp': ('P4ZchWCXOSNP.jpg', 'oven repair'),
    'stock-pest-unsplash.webp': ('1wVfKp6MP8rs.jpg', 'pest control'),
    'stock-electrical-unsplash.webp': ('Qk2vzD9bwUox.jpg', 'electrical safety'),
}
for out, (source, _) in assets.items():
    target = IMG / out
    if not target.exists():
        with Image.open(SEARCH / source) as im:
            im = im.convert('RGB')
            width = 1600
            ratio = width / im.width
            im = im.resize((width, round(im.height * ratio)), Image.Resampling.LANCZOS)
            im.save(target, 'WEBP', quality=82, method=6)

# Replace the three highlighted cleaning-card placeholders with one real cleaning photo.
articles = ROOT / 'articles.html'
html = articles.read_text(encoding='utf-8')
for city in ('القريات', 'رفحاء', 'طريف'):
    html = re.sub(
        rf'(<a class="article-cover-link" href="cleaning-[^"]+/"[^>]*><img class="article-cover" src=")[^"]+(" alt=")صورة تحريرية لمقال تنظيف المنازل في {city}(")',
        rf'\g<1>images/stock-cleaning-unsplash.webp\g<2>فريق ينظف منزلًا بطريقة منظمة في {city}\g<3>',
        html,
        count=1,
    )

# Top evergreen maintenance cards use external-free assets too.
for href, src, alt in [
    ('articles/ac-filter-cleaning.html', 'images/stock-hvac-unsplash.webp', 'فني يفحص وحدة تكييف منزلية'),
    ('articles/electrical-safety.html', 'images/stock-electrical-unsplash.webp', 'فني يفحص لوحة كهرباء منزلية'),
    ('articles/water-leak.html', 'images/stock-pipe-unsplash.webp', 'فني يفحص أنابيب المياه أسفل المغسلة'),
]:
    html = re.sub(rf'(<a class="article-cover-link" href="{re.escape(href)}"[^>]*><img class="article-cover" src=")[^"]+(" alt=")[^"]+("[^>]*>)', rf'\g<1>{src}\g<2>{alt}\g<3>', html, count=1)

# Turn text-only maintenance/category cards into the same image + body card pattern.
category_images = {
    'category-drain_unblocking': ('images/stock-pipe-unsplash.webp', 'فحص أنابيب الصرف وتسليك المجاري'),
    'category-air_conditioner_maintenance': ('images/stock-hvac-unsplash.webp', 'فني صيانة مكيفات منزلية'),
    'category-furniture_moving': ('images/stock-moving-unsplash.webp', 'ترتيب صناديق الأثاث قبل النقل'),
    'category-gas_oven_maintenance': ('images/stock-oven-unsplash.webp', 'فحص فرن منزلي وصيانته'),
    'category-pest_control': ('images/stock-pest-unsplash.webp', 'فحص وقائي لمكافحة الآفات المنزلية'),
}
lines = html.splitlines()
current = None
out = []
for line in lines:
    heading = re.search(r'aria-labelledby="([^"]+)"', line)
    if heading and heading.group(1) in category_images:
        current = heading.group(1)
    if '<article class="article-card article-card-text reveal">' in line and current in category_images:
        src, alt = category_images[current]
        line = line.replace(
            '<article class="article-card article-card-text reveal">',
            f'<article class="article-card article-card-text reveal"><img class="article-card-image" src="{src}" alt="{alt}" width="1200" height="675" loading="lazy" decoding="async"><div class="article-card-text-body">',
            1,
        )
        line = line.replace('</article>', '</div></article>', 1)
    out.append(line)
html = '\n'.join(out) + ('\n' if html.endswith('\n') else '')
articles.write_text(html, encoding='utf-8')

# Make every phone number a blue WhatsApp link site-wide.
html_files = list(ROOT.glob('*.html')) + list(ROOT.glob('articles/*.html')) + list(ROOT.glob('cleaning-*/index.html')) + list(ROOT.glob('services/*.html'))
for path in html_files:
    value = path.read_text(encoding='utf-8')
    value = value.replace('href="tel:+966552610151"', 'href="https://wa.me/966552610151" target="_blank" rel="noopener noreferrer" class="phone-link"')
    value = value.replace('aria-label="الاتصال الهاتفي"', 'aria-label="التواصل عبر واتساب"')
    value = value.replace('اتصل على <a class="phone-link"', 'تواصل عبر واتساب على <a class="phone-link"')
    path.write_text(value, encoding='utf-8')

# Append source records without claiming public-domain status.
sources = ROOT / 'image-sources.md'
with sources.open('a', encoding='utf-8') as f:
    f.write('\n## الصور المضافة لبطاقات الأدلة\n\n')
    f.write('- `images/stock-moving-unsplash.webp` — [صور صناديق النقل على Unsplash](https://unsplash.com/s/photos/moving-boxes).\n')
    f.write('- `images/stock-oven-unsplash.webp` — [صور إصلاح الأفران على Unsplash](https://unsplash.com/s/photos/oven-repair).\n')
    f.write('- `images/stock-pest-unsplash.webp` — [صور مكافحة الآفات على Unsplash](https://unsplash.com/s/photos/pest-control).\n')
    f.write('- `images/stock-electrical-unsplash.webp` — [صور قواطع الكهرباء على Unsplash](https://unsplash.com/s/photos/circuit-breaker).\n')

print('updated cards, WhatsApp links, and', len(assets), 'new stock assets')
