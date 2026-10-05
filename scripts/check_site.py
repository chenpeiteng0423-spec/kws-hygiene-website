"""Proportional checks for migrated content integrity, safe markup and local routes."""
from pathlib import Path
from urllib.parse import urlparse,unquote
from bs4 import BeautifulSoup
import json,re
root=Path(__file__).resolve().parents[1];site=root/'website';products=json.loads((root/'content/products.json').read_text());report=json.loads((root/'content/build-report.json').read_text());failures=[];checked=0
assert len(products)==321 and len({p['id'] for p in products})==321
assert report['product_pages']==321 and report['categories']==14
assert report['certificates']==10 and report['certificate_scans']==11
for p in products:
    assert p.get('basic'),f'Missing actual source specifications: {p["id"]}'
    assert p.get('image'),f'Missing product image: {p["id"]}'
    assert (site/f'products/p-{p["id"]}/index.html').exists()
    assert p['category'],f'Missing category: {p["id"]}'

def target(path):
    dst=site/unquote(path).lstrip('/')
    return dst/'index.html' if dst.is_dir() or path.endswith('/') else dst
for path in report['routes']:
    f=target(path);b=BeautifulSoup(f.read_text(),'html.parser');checked+=1
    if len(b.select('h1'))!=1:failures.append((path,'Expected exactly one h1'))
    if not b.select_one('main') or not b.select_one('nav[aria-label="Main navigation"]'):failures.append((path,'Missing landmark'))
    for tag in b.find_all(True):
        if any(k.lower().startswith('on') for k in tag.attrs):failures.append((path,'Unsafe inline handler'))
        for attr in ['href','src','poster']:
            value=tag.get(attr)
            if value is None:continue
            parsed=urlparse(value)
            if parsed.scheme in ['http','https','mailto','tel','data']:continue
            if value.startswith('javascript:'):failures.append((path,'Unsafe javascript URL'));continue
            if not parsed.path:continue
            dst=target(parsed.path) if parsed.path.startswith('/') else f.parent/unquote(parsed.path)
            if not dst.exists():failures.append((path,'Missing link or asset: '+value))
        if tag.name=='img' and 'alt' not in tag.attrs:failures.append((path,'Image missing alt'))
    if b.select('iframe,object,embed'):failures.append((path,'Source embed unexpectedly present'))
    for tag in b.select('script[src], img[src], source[src]'):
        if urlparse(tag['src']).scheme in ['http','https']:failures.append((path,'Remote render dependency: '+tag['src']))
    for field in b.select('input,select,textarea'):
        if field.get('type') in ['hidden','submit']:continue
        if not field.get('id') or not b.find('label',attrs={'for':field.get('id')}):failures.append((path,'Input missing visible/programmatic label'))
for p in site.glob('assets/video/*/index.m3u8'):
    for line in p.read_text().splitlines():
        if line and not line.startswith('#') and not (p.parent/line).exists():failures.append((str(p),'Missing video segment '+line))
contact=(site/'contact/index.html').read_text();assert 'Preparing a draft does not send a message' in contact
js=(site/'assets/site.js').read_text();assert 'mailto:mandyxu@scentairmachines.com' in js and 'https://wa.me/8613590491364' in js
sample=next(p for p in products if p['id']=='31772096');assert dict(sample['specs'])['Product Size']=='245*167*44mm'
summary={'checked_pages':checked,'product_records':len(products),'source_specs_present':True,'certificate_records':10,'failures':failures}
(root/'evidence/static-checks.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps(summary,ensure_ascii=False,indent=2));assert not failures,'Site verification failed'
