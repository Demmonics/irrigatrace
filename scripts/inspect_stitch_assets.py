import re
import os
import urllib.request

os.makedirs('design/stitch-source/assets', exist_ok=True)

all_urls = set()
for mode in ['light', 'dark']:
    with open(f'design/stitch-source/{mode}/code.html', 'r', encoding='utf-8') as f:
        content = f.read()
    # find urls
    found = re.findall(r'https?://[^\s"\'\)]+', content)
    for u in found:
        # filter images / fonts
        if any(ext in u.lower() for ext in ['.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif', 'images.unsplash.com', 'assets.']):
            all_urls.add(u)

print(f"Discovered {len(all_urls)} asset URLs:")
for i, url in enumerate(sorted(all_urls)):
    print(f" {i+1}. {url}")
    # try downloading
    try:
        clean_name = f"asset_{i+1}" + (os.path.splitext(url.split('?')[0])[1] or '.png')
        target_path = os.path.join('design/stitch-source/assets', clean_name)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp, open(target_path, 'wb') as out:
            data = resp.read()
            out.write(data)
        print(f"    -> Saved {target_path} ({len(data)} bytes)")
    except Exception as e:
        print(f"    -> Download skipped/failed: {e}")
