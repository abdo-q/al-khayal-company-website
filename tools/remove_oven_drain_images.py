from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'articles.html'
lines = path.read_text(encoding='utf-8').splitlines()
current = None
counters = {'category-drain_unblocking': 0, 'category-gas_oven_maintenance': 0}

drain_icon = '<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M14 12v18c0 7 5 12 12 12h12c7 0 12-5 12-12V12M14 23h36M26 42v10M38 42v10M22 52h20"/><path d="M45 12h9v8h-9"/></svg>'
oven_icon = '<svg viewBox="0 0 64 64" aria-hidden="true"><rect x="14" y="8" width="36" height="48" rx="4"/><path d="M22 18h5M37 18h5M20 26h24v22H20zM25 31h14v12H25z"/><circle cx="24" cy="18" r="1"/><circle cx="32" cy="18" r="1"/><circle cx="40" cy="18" r="1"/></svg>'

out = []
for line in lines:
    heading = re.search(r'aria-labelledby="([^"]+)"', line)
    if heading and heading.group(1) in counters:
        current = heading.group(1)
    if current in counters and '<article class="article-card article-card-text reveal"><img class="article-card-image"' in line:
        n = counters[current]
        kind = 'drain' if current == 'category-drain_unblocking' else 'oven'
        icon = drain_icon if kind == 'drain' else oven_icon
        visual = f'<div class="article-card-service-visual article-card-service-visual--{kind} service-tone-{kind}-{n % 6 + 1}" aria-hidden="true">{icon}</div>'
        line = re.sub(r'<img class="article-card-image"[^>]*>', visual, line, count=1)
        counters[current] += 1
    out.append(line)
path.write_text('\n'.join(out) + '\n', encoding='utf-8')
print('replaced drain cards:', counters['category-drain_unblocking'])
print('replaced oven cards:', counters['category-gas_oven_maintenance'])
