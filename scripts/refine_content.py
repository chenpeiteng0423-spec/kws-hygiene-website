"""Complete gallery migration, correct category provenance, and bind archived videos."""
from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor,as_completed
import re,json
from import_content import ROOT,url,save_asset,sanitize,ERRORS
content=ROOT/'content';products=json.loads((content/'products.json').read_text());media=json.loads((content/'media.json').read_text());extra=set();galleries={}
if (content/'recovered-media.json').exists():media.update(json.loads((content/'recovered-media.json').read_text()))
for p in products:
    b=BeautifulSoup((ROOT/'research/details'/f'{p["id"]}.html').read_text(),'html.parser')
    crumb=b.select_one('[itemprop="itemListElement"] a[href*="supplier-"]')
    if crumb:p['category']=crumb.get_text(' ',strip=True)
    gallery=[]
    for img in b.select('#slidePic img'):
        source=url(img.get('src'));large=re.sub(r'/photo/pc(\d+)',r'/photo/pl\1',source)
        gallery.append(large)
        if large not in media:extra.add(large)
    galleries[p['id']]=list(dict.fromkeys(gallery))
    # Re-sanitize from archive so both the raw description and display are retained.
    desc=b.select_one('#product_description');p['description_html']=sanitize(str(desc.select_one('section') or desc),media) if desc else ''
    for a in BeautifulSoup(p['description_html'],'html.parser').select('a[href]'):
        if a['href'] in media:pass
resources=json.loads((content/'resources.json').read_text());streams={v.get('id'):v for v in json.loads((content/'video-streams.json').read_text())} if (content/'video-streams.json').exists() else {}
for v in resources['videos']:
    b=BeautifulSoup((ROOT/'research/details'/Path(v['source']).name).read_text(),'html.parser');raw=str(b)
    stream=streams.get(v['id'],{})
    v.update({k:val for k,val in stream.items() if k in ['hls','segments','title']})
    poster=re.search(r'window\.(?:detailposter|detailvideoposter|poster)\s*=\s*[\'"]([^\'"]+)',raw)
    if not poster:
        # Player poster is adjacent to the detail stream assignment.
        poster=re.search(r'window\.[A-Za-z]*poster[A-Za-z]*\s*=\s*[\'"]([^\'"]+)',raw,re.I)
    if poster:
        v['poster_url']=url(poster[1]);extra.add(v['poster_url'])
    description=b.select_one('.vc-btxt-description') or b.select_one('.vc-btxt-desc')
    if description:v['text']=description.get_text(' ',strip=True)
print('Additional full gallery / video poster images:',len(extra),flush=True)
with ThreadPoolExecutor(max_workers=4) as pool:
    futures={pool.submit(save_asset,u):u for u in extra}
    for i,f in enumerate(as_completed(futures),1):
        result=f.result()
        if result:media[futures[f]]=result
        if i%100==0 or i==len(futures):print(f'Gallery media {i}/{len(futures)}',flush=True)
for p in products:
    p['gallery']=[media[u] for u in galleries[p['id']] if u in media] or p.get('gallery',[])[:1]
    if not p.get('image') and p['gallery']:p['image']=p['gallery'][0]
    # Map image and known product links locally; no unnecessary legacy-site dependency.
    b=BeautifulSoup(p['description_html'],'html.parser')
    for a in b.select('a[href]'):
        if a['href'] in media:a['href']=media[a['href']]['src'];a.attrs.pop('target',None)
        else:
            match=re.search(r'/(?:sale|quality)-(\d+)',a['href'])
            if match and any(x['id']==match[1] for x in products):a['href']=f'/products/p-{match[1]}/';a.attrs.pop('target',None)
    p['description_html']=str(b)
for v in resources['videos']:
    if v.get('poster_url') in media:v['poster']=media[v['poster_url']]
for n in resources['news']:
    b=BeautifulSoup((ROOT/'research/details'/Path(n['source']).name).read_text(),'html.parser');node=b.select_one('.four_news_detail_132 .contents')
    if node:n['html']=sanitize(str(node),media)
(content/'products.json').write_text(json.dumps(products,ensure_ascii=False,indent=2));(content/'media.json').write_text(json.dumps(media,ensure_ascii=False,indent=2));(content/'resources.json').write_text(json.dumps(resources,ensure_ascii=False,indent=2));(content/'gallery-audit.json').write_text(json.dumps({'additional_media':len(extra),'media_errors':ERRORS,'products_with_gallery':sum(bool(p['gallery']) for p in products),'local_video_streams':sum(bool(v.get('hls')) for v in resources['videos'])},indent=2));print('Gallery and video content refinement complete.',flush=True)
