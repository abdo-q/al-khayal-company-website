from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'articles.html'
html = path.read_text(encoding='utf-8')

# Use the existing local copies of web imagery, with the new Unsplash assets first.
# The pool is intentionally long so consecutive cards do not repeat the same photo.
pool = [
    'images/stock-pipe-unsplash.webp', 'images/stock-hvac-unsplash.webp',
    'images/stock-moving-unsplash.webp', 'images/stock-oven-unsplash.webp',
    'images/stock-pest-unsplash.webp', 'images/stock-electrical-unsplash.webp',
    'images/stock-cleaning-unsplash.webp',
]
# Replace only category/text cards, not the three evergreen cards at the top.
pattern = re.compile(r'(<article class="article-card article-card-text reveal"><img class="article-card-image" src=")[^"]+(" alt=")[^"]+("[^>]*>)')
index = 0
def replace(match):
    global index
    src = pool[index % len(pool)]
    index += 1
    return match.group(1) + src + match.group(2) + 'صورة مناسبة لدليل خدمات منزلية' + match.group(3)
html, count = pattern.subn(replace, html)
path.write_text(html, encoding='utf-8')
print(f'updated {count} horizontal cards with {len(pool)} rotating images')
