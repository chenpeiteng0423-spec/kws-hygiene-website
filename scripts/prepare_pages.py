"""Prepare a verified static snapshot for GitHub Pages, including project paths."""
from pathlib import Path
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
import argparse, json, shutil

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
parser.add_argument('--output', default='_site')
args = parser.parse_args()
url = args.url.rstrip('/')
parsed = urlparse(url)
if parsed.scheme != 'https' or not parsed.netloc or parsed.query or parsed.fragment:
    raise ValueError('Expected a complete HTTPS website URL without query or fragment')
base = parsed.path.rstrip('/')
output = ROOT / args.output
if output == ROOT or ROOT not in output.resolve().parents or output == ROOT / 'website':
    raise ValueError('Output must be a separate directory inside this project')
if output.exists():
    shutil.rmtree(output)
shutil.copytree(ROOT / 'website', output)
attrs = ['href', 'src', 'poster', 'data-gallery-src', 'data-zoom-src', 'data-hls']
pages = 0
for file in list(output.rglob('*')):
    if not file.is_file() or file.suffix or file.name.startswith('.'):
        continue
    if file.read_bytes()[:100].lower().startswith(b'<!doctype html'):
        text = file.read_text()
        file.unlink()
        file.mkdir()
        (file / 'index.html').write_text(text)
for file in output.rglob('*.html'):
    soup = BeautifulSoup(file.read_text(), 'html.parser')
    for tag in soup.find_all(True):
        for attr in attrs:
            value = tag.get(attr)
            if isinstance(value, str) and value.startswith('/') and not value.startswith('//'):
                tag[attr] = base + value
        if tag.name == 'meta' and tag.get('http-equiv', '').lower() == 'refresh':
            value = tag.get('content', '')
            tag['content'] = value.replace('url=/', 'url=' + base + '/', 1)
    # Customer review URL is deliberately not indexed alongside the existing domain.
    robots = soup.find('meta', attrs={'name': 'robots'})
    if robots:
        robots['content'] = 'noindex,nofollow'
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    if canonical:
        canonical.decompose()
    for script in soup.select('script[type="application/ld+json"]'):
        data = json.loads(script.string or '{}')
        if isinstance(data, dict) and isinstance(data.get('image'), str) and data['image'].startswith('/'):
            data['image'] = url + data['image']
        script.string = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    file.write_text(str(soup))
    pages += 1
(output / '.nojekyll').touch()
(output / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')
for name in ['_headers', '_redirects', 'sitemap.xml']:
    (output / name).unlink(missing_ok=True)
failures = []
for file in output.rglob('*.html'):
    soup = BeautifulSoup(file.read_text(), 'html.parser')
    for tag in soup.find_all(True):
        for attr in attrs:
            value = tag.get(attr)
            if not isinstance(value, str):
                continue
            path = urlparse(value).path
            if not value.startswith('/') or value.startswith('//'):
                continue
            if base and not path.startswith(base + '/'):
                failures.append(f'{file.relative_to(output)}: missing project prefix {value}')
                continue
            target = output / unquote(path[len(base):]).lstrip('/')
            if target.is_dir():
                target = target / 'index.html'
            if not target.exists():
                failures.append(f'{file.relative_to(output)}: missing target {value}')
if failures:
    raise AssertionError('\n'.join(failures[:30]))
print(json.dumps({'url': url, 'base_path': base, 'html_documents': pages, 'broken_local_targets': len(failures), 'output': args.output}))
