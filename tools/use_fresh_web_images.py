from pathlib import Path
from PIL import Image
import re

ROOT = Path(__file__).resolve().parents[1]
SEARCH = Path('/home/ubuntu/upload/search_images')
IMG = ROOT / 'images'

sources = {
    # Fresh cleaning photos from the latest web-image search.
    'web-cleaning-01.webp': 'zquAUS02u5q3.jpg',
    'web-cleaning-02.webp': 'gmTWcBFosSOX.jpg',
    'web-cleaning-03.webp': 'sKmq13bNshoW.jpg',
    'web-cleaning-04.webp': 's8A4ekkqTvO4.jpg',
    'web-cleaning-05.webp': 'zZndRmtjVb1q.jpg',
    'web-cleaning-06.webp': '1HzpotfOp0Kn.jpeg',
    'web-cleaning-07.webp': 'rvQiwikjjMVM.jpeg',
    # Fresh repair, plumbing and HVAC photos.
    'web-repair-01.webp': '1pTcFBd2UdlR.jpg',
    'web-repair-02.webp': 'jmk5XliKBO0z.jpg',
    'web-repair-03.webp': 'jCLLbRqs5gQe.jpg',
    'web-repair-04.webp': '5rQWxzdmRCok.jpeg',
    'web-repair-05.webp': 'hmClujMxgalI.jpeg',
    'web-repair-06.webp': 'Vuxy4qqCa2pl.jpeg',
    'web-repair-07.webp': 'gewLitaQcxDy.jpg',
    'web-repair-08.webp': 'bNUO5azzdD3h.jpg',
    # Fresh moving and oven photos.
    'web-moving-01.webp': 'BHcCG1d6eLMH.jpg',
    'web-moving-02.webp': 'BJUXRlSW62aQ.jpg',
    'web-moving-03.webp': 'IN8HdaN4uuTi.jpg',
    'web-moving-04.webp': 'dYQ7iaE8eIom.jpeg',
    'web-moving-05.webp': 'WTwxjVHYBuKy.jpg',
    'web-moving-06.webp': 'VKUKPbshB8xE.jpg',
    'web-moving-07.webp': '1KWHmiFlvryn.jpeg',
    'web-moving-08.webp': 'Hhpvk19ssSgn.jpeg',
    # Inspection/termite-oriented photos; avoid spray-can imagery.
    'web-inspection-01.webp': 'mQ33loAQdE1B.jpg',
    'web-inspection-02.webp': 'iO3dwEC05P0u.jpeg',
    'web-inspection-03.webp': '5zZeUb4uUCH1.jpg',
    'web-inspection-04.webp': 'lMVnBKJD8L3R.jpg',
}
for out, source in sources.items():
    target = IMG / out
    if not target.exists():
        with Image.open(SEARCH / source) as im:
            im = im.convert('RGB')
            # Use a consistent landscape card crop while preserving the subject.
            ratio = max(1600 / im.width, 900 / im.height)
            im = im.resize((round(im.width * ratio), round(im.height * ratio)), Image.Resampling.LANCZOS)
            left = (im.width - 1600) // 2
            top = (im.height - 900) // 2
            im = im.crop((left, top, left + 1600, top + 900))
            im.save(target, 'WEBP', quality=82, method=6)

pools = {
    'category-drain_unblocking': [f'images/web-repair-{n:02d}.webp' for n in (1, 4, 5, 7, 8)],
    'category-air_conditioner_maintenance': [f'images/web-repair-{n:02d}.webp' for n in (2, 3, 4, 5, 6, 7, 8)],
    'category-furniture_moving': [f'images/web-moving-{n:02d}.webp' for n in range(1, 9)],
    'category-gas_oven_maintenance': [f'images/web-moving-{n:02d}.webp' for n in (5, 6, 2, 3, 4)],
    'category-pest_control': [f'images/web-inspection-{n:02d}.webp' for n in range(1, 5)],
}

path = ROOT / 'articles.html'
html = path.read_text(encoding='utf-8')
lines = html.splitlines()
current = None
counters = {key: 0 for key in pools}
out = []
for line in lines:
    heading = re.search(r'aria-labelledby="([^"]+)"', line)
    if heading and heading.group(1) in pools:
        current = heading.group(1)
    if '<article class="article-card article-card-text reveal"><img class="article-card-image"' in line and current in pools:
        pool = pools[current]
        src = pool[counters[current] % len(pool)]
        counters[current] += 1
        line = re.sub(r'(<img class="article-card-image" src=")[^"]+', rf'\g<1>{src}', line, count=1)
    out.append(line)
path.write_text('\n'.join(out) + '\n', encoding='utf-8')
print(f'created {len(sources)} fresh web image assets')
print('assigned', sum(counters.values()), 'category cards')
