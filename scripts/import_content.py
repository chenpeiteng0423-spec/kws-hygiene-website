"""Import owner-supplied public website content; never execute source HTML/scripts."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from PIL import Image, ImageOps
import json, re, subprocess, hashlib, threading, sys
ROOT=Path(__file__).resolve().parents[1]; RESEARCH=ROOT/'research'; CONTENT=ROOT/'content'; ASSETS=ROOT/'website/assets/media'
ORIGIN='https://www.scentairmachines.com'; LOCK=threading.Lock(); ERRORS=[]; AUDIT=[]
for d in [RESEARCH/'details',RESEARCH/'media',CONTENT,ASSETS]:d.mkdir(parents=True,exist_ok=True)
def url(v):
    return urljoin(ORIGIN+'/',v or '')
def fetch(u,p):
    if p.exists() and p.stat().st_size:return True
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.part')
    result=subprocess.run(['curl','--silent','--show-error','--fail','--location','--connect-timeout','7','--max-time','18','--retry','1','--retry-delay','1','--user-agent','KWS-Content-Migration/1.0',u,'-o',str(tmp)],capture_output=True)
    if result.returncode:
        with LOCK:ERRORS.append({'url':u,'error':result.stderr.decode(errors='replace')[:300]})
        tmp.unlink(missing_ok=True);return False
    tmp.replace(p);return True

def save_asset(u):
    name=hashlib.sha256(u.encode()).hexdigest()[:20];ext=Path(urlparse(u).path).suffix.lower();ext=ext if ext in ['.jpg','.jpeg','.png','.gif','.webp','.mp4'] else '.jpg'
    raw=RESEARCH/'media'/f'{name}{ext}';target=ASSETS/f'{name}{".mp4" if ext==".mp4" else ".webp"}'
    if not fetch(u,raw):return None
    try:
        if ext=='.mp4':
            if not target.exists():target.write_bytes(raw.read_bytes())
            return {'src':'/assets/media/'+target.name}
        with Image.open(raw) as original:
            image=ImageOps.exif_transpose(original).convert('RGBA' if 'A' in original.getbands() else 'RGB');w,h=image.size
            if not target.exists():
                # Keep fine print/diagrams readable; source originals remain in research/media.
                image.thumbnail((2000,12000));image.save(target,'WEBP',quality=88,method=4)
            thumb=ASSETS/f'{name}-thumb.webp'
            if not thumb.exists():
                image.thumbnail((640,640));image.save(thumb,'WEBP',quality=83,method=4)
            return {'src':'/assets/media/'+target.name,'thumb':'/assets/media/'+thumb.name,'width':w,'height':h}
    except Exception as ex:
        with LOCK:ERRORS.append({'url':u,'error':str(ex)})
        return None

def text(x):return ' '.join(x.get_text(' ',strip=True).split()) if x else ''
def pairs(t):
    result=[]
    for row in t.select('tr'):
        cells=row.find_all(['th','td'],recursive=False)
        if len(cells) not in [2,4]:continue
        for i in range(0,len(cells),2):
            k=text(cells[i]).rstrip(':').strip();v=text(cells[i+1])
            if not k or not v or k.lower()=='highlight':continue
            if len(v)>=12 and len(v)%2==0 and v[:len(v)//2]==v[len(v)//2:] and re.search(r'\d',v) and re.search(r'mm|cm|kg|ml',v,re.I):
                AUDIT.append({'field':k,'before':v,'after':v[:len(v)//2],'fix':'exact duplicated value'});v=v[:len(v)//2]
            result.append([k,v])
    return result

def parse_product(p):
    dst=RESEARCH/'details'/f'{p["id"]}.html'
    if not dst.exists():
        existing=RESEARCH/Path(urlparse(p['url']).path).name
        if existing.exists():dst.write_bytes(existing.read_bytes())
    if not fetch(p['url'],dst):return {**p,'error':True}
    b=BeautifulSoup(dst.read_text(errors='replace'),'html.parser')
    title=text(b.select_one('h1')) or p['title'];tables=b.select('table.tables.data')
    basic=pairs(tables[0]) if tables else [];shipping=pairs(tables[1]) if len(tables)>1 else []
    specs=pairs(b.select_one('table.tab1')) if b.select_one('table.tab1') else []
    main=b.select_one('#productImg');mainurl=url(main.get('src')) if main else p['image']
    description=b.select_one('#product_description');image_urls=[]
    # Gallery is identified from source photo paths, excluding recommendations and icons.
    if mainurl:image_urls.append(mainurl)
    for a in b.select('a[href]'):
        href=a.get('href','')
        if re.search(r'/photo/pl\d+',href) and href not in image_urls:image_urls.append(url(href))
    desc=str(description.select_one('section') or description) if description else ''
    for i in BeautifulSoup(desc,'html.parser').find_all('img'):
        image_urls.append(url(i.get('data-original') or i.get('src')))
    crumbs=[text(a) for a in b.select('.breadcrumb a, .crumbs a, .breadcrumbs a')]
    # A product's source category appears before h1 in the page breadcrumb.
    category=p['categories'][0]
    for a in b.select('a[href]'):
        if a.find_parent('h2'):continue
        if 'supplier-' in a.get('href','') and text(a) in p['categories']:
            category=text(a);break
    actual_category=None
    if main:
        for a in b.select('a[href]'):
            if 'supplier-' in a.get('href','') and a.find_parent(class_=re.compile('breadcrumb|crumb')):
                actual_category=text(a)
    return {**p,'title':title,'category':actual_category or category,'basic':basic,'shipping':shipping,'specs':specs,'main_url':mainurl,'image_urls':list(dict.fromkeys(image_urls)),'description_html':desc,'model':dict(basic).get('Model Number',dict(specs).get('Model No.','')),'record_type':'catalog' if '/sale-' in p['url'] else 'recommended'}

def sanitize(raw,assets):
    b=BeautifulSoup(raw,'html.parser')
    for x in b.select('script,style,iframe,form,object,embed,link,meta,input,button'):
        x.decompose()
    allowed={'p','div','span','section','strong','b','em','i','u','ul','ol','li','h2','h3','h4','table','thead','tbody','tr','th','td','br','img','a','blockquote','sup','sub'}
    for x in list(b.find_all(True)):
        if x.name not in allowed:x.unwrap();continue
        attrs=dict(x.attrs);x.attrs={}
        if x.name in ['th','td']:
            for key in ['colspan','rowspan']:
                if str(attrs.get(key,'')).isdigit():x[key]=attrs[key]
        if x.name=='img':
            u=url(attrs.get('data-original') or attrs.get('src'));a=assets.get(u)
            if not a:x.decompose();continue
            x['src']=a['src'];x['alt']=attrs.get('alt') or 'KWS product information';x['loading']='lazy';x['decoding']='async';x['width']=a.get('width',800);x['height']=a.get('height',800)
        if x.name=='a':
            href=url(attrs.get('href'))
            if urlparse(href).scheme in ['http','https']:
                x['href']=href;x['target']='_blank';x['rel']='noopener'
            else:x.unwrap()
    # Drop empty source layout blocks; leave meaningful text and images intact.
    for x in reversed(list(b.find_all(['p','div','span']))):
        if not x.get_text(strip=True) and not x.find(['img','table']):x.decompose()
    return str(b)

def main():
    records=json.loads((RESEARCH/'products.json').read_text());parsed=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(parse_product,p) for p in records]
        for i,f in enumerate(as_completed(futures),1):
            parsed.append(f.result())
            if i%40==0 or i==len(records):print(f'Product details {i}/{len(records)}',flush=True)
    parsed.sort(key=lambda p:(p.get('record_type')!='catalog',p['id']))
    (CONTENT/'products-raw.json').write_text(json.dumps(parsed,ensure_ascii=False,indent=2))
    pages={};asset_urls=set([url('/logo.gif')]);extra_links=set()
    for name in ['aboutus.html','factory.html','quality.html','contactus.html','news.html','cases__our-business-partners-1898.html','video-all.html','video-playlist.html']:
        b=BeautifulSoup((RESEARCH/name).read_text(),'html.parser');pages[name]=b
        for i in b.select('img'):
            u=url(i.get('data-original') or i.get('src'))
            if '/photo/' in u:asset_urls.add(u)
        if name=='news.html':extra_links.update(url(a['href']) for a in b.select('a[href]') if '/news/' in a['href'])
        if name=='video-all.html':extra_links.update(url(a['href']) for a in b.select('a[href]') if re.search(r'/video-\d+',a['href']))
    # Preserve all video list pagination and unique video pages.
    b=pages['video-all.html'];pagination={url(a['href']) for a in b.select('a[href]') if re.search(r'video-all-p\d+',a['href'])}
    for u in sorted(pagination):
        dst=RESEARCH/Path(urlparse(u).path).name
        if fetch(u,dst):
            bb=BeautifulSoup(dst.read_text(),'html.parser');extra_links.update(url(a['href']) for a in bb.select('a[href]') if re.search(r'/video-\d+',a['href']))
    extras=[]
    for u in sorted(extra_links):
        dst=RESEARCH/'details'/Path(urlparse(u).path).name
        if not fetch(u,dst):continue
        bb=BeautifulSoup(dst.read_text(),'html.parser');extras.append((u,bb))
        for i in bb.select('img'):
            v=url(i.get('data-original') or i.get('src'))
            if '/photo/' in v:asset_urls.add(v)
        for v in re.findall(r'''(?:src|url|video_url|videoUrl)[\s:=]+["']([^"']+\.mp4(?:\?[^"']*)?)["']''',str(bb)):
            asset_urls.add(url(v))
    for p in parsed:asset_urls.update(p.get('image_urls',[]))
    print(f'Downloading {len(asset_urls)} unique media files',flush=True);assets={}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(save_asset,u):u for u in sorted(asset_urls)}
        for i,f in enumerate(as_completed(futures),1):
            value=f.result()
            if value:assets[futures[f]]=value
            if i%100==0 or i==len(futures):print(f'Media {i}/{len(futures)}',flush=True)
    (CONTENT/'media.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
    for p in parsed:
        p['image']=assets.get(p.get('main_url'),{});p['gallery']=[assets[u] for u in p.get('image_urls',[]) if u in assets]
        p['description_html']=sanitize(p.get('description_html',''),assets)
    page_data={}
    for name,b in pages.items():
        node=b.select_one('.about-us-content') if name=='aboutus.html' else b.select_one('.left-content')
        if node:
            for x in node.select('.contacts,.tab-wrap,.page-title,.tab-title'):x.decompose()
            # Public company description stays archived; promotional metrics aren't automatically published.
            page_data[name]={'html':sanitize(str(node),assets),'images':[assets[url(i.get('data-original') or i.get('src'))] for i in node.select('img') if url(i.get('data-original') or i.get('src')) in assets]}
    videos=[];news=[]
    for u,b in extras:
        if '/video-' in u:
            match=re.search(r'/video-(\d+)',u);mp4=[]
            for a in assets:
                if '.mp4' in a and a.split('?',1)[0] in str(b):mp4.append(assets[a]['src'])
            title=text(b.select_one('h1')) or text(b.select_one('title')).split(' - ')[0]
            poster=next((assets[url(i.get('data-original') or i.get('src'))] for i in b.select('img') if '.mp4_d' in str(i) and url(i.get('data-original') or i.get('src')) in assets),None)
            videos.append({'id':match[1],'title':title,'source':u,'video':mp4[0] if mp4 else None,'poster':poster,'text':text(b.select_one('.v-details') or b.select_one('.v-description'))})
        else:
            node=b.select_one('.news-content') or b.select_one('.news-details') or b.select_one('.item-content');news.append({'title':text(b.select_one('h1')) or 'KWS team building','source':u,'html':sanitize(str(node),assets) if node else ''})
    (CONTENT/'products.json').write_text(json.dumps(parsed,ensure_ascii=False,indent=2))
    (CONTENT/'pages.json').write_text(json.dumps(page_data,ensure_ascii=False,indent=2))
    (CONTENT/'resources.json').write_text(json.dumps({'videos':videos,'news':news},ensure_ascii=False,indent=2))
    (CONTENT/'migration-audit.json').write_text(json.dumps({'products':len(parsed),'errors':ERRORS,'normalizations':AUDIT,'media':len(assets),'videos':len(videos)},ensure_ascii=False,indent=2))
    print(f'Import complete: {len(parsed)} products, {len(assets)} media, {len(videos)} videos, {len(ERRORS)} errors',flush=True)
if __name__=='__main__':main()
