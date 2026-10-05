"""Archive the source HLS playlists and segments locally, preserving native playback."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re,json
from import_content import fetch,url,ROOT
errors=[];videos=[]
def migrate(path):
    raw=path.read_text();match=re.search(r'window\.detailvideosrc\s*=\s*[\'"]([^\'"]+)',raw)
    if not match:return {'file':path.name,'error':'No source stream found'}
    pid=re.search(r'video-(\d+)',path.name)[1];source=url(match[1]);folder=ROOT/'website/assets/video'/pid;archive=ROOT/'research/video'/pid;folder.mkdir(parents=True,exist_ok=True)
    master=archive/'master.m3u8'
    if not fetch(source,master):return {'id':pid,'error':'Could not retrieve master playlist'}
    stream_lines=[s for s in master.read_text().splitlines() if s and not s.startswith('#')]
    selected=stream_lines[-1];selected_url=urljoin(source,selected);manifest=archive/'index.m3u8'
    if not fetch(selected_url,manifest):return {'id':pid,'error':'Could not retrieve stream playlist'}
    lines=manifest.read_text().splitlines();output=[];count=0
    for line in lines:
        if line and not line.startswith('#'):
            name=f'{count:04d}.ts';count+=1
            if not fetch(urljoin(selected_url,line),folder/name):return {'id':pid,'error':'Could not retrieve a video segment'}
            output.append(name)
        elif 'URI=' in line:return {'id':pid,'error':'Source uses a separate key or media initialization file; retain external player'}
        else:output.append(line)
    (folder/'index.m3u8').write_text('\n'.join(output)+'\n')
    poster=re.search(r'window\.detailvideoposter\s*=\s*[\'"]([^\'"]+)',raw) or re.search(r'window\.detailposter\s*=\s*[\'"]([^\'"]+)',raw)
    b=BeautifulSoup(raw,'html.parser');heading=b.select_one('.vc-btxt-title')
    return {'id':pid,'hls':'/assets/video/'+pid+'/index.m3u8','segments':count,'source_stream':source,'title':heading.get_text(' ',strip=True) if heading else b.title.get_text(strip=True),'poster_url':url(poster[1]) if poster else None}
paths=list((ROOT/'research/details').glob('video-*.html'))
with ThreadPoolExecutor(max_workers=2) as pool:
    futures=[pool.submit(migrate,p) for p in paths]
    for i,f in enumerate(as_completed(futures),1):
        result=f.result();videos.append(result);print(f'Video archives {i}/{len(paths)}: '+result.get('id',result.get('file',''))+(' OK' if result.get('hls') else ' unavailable'),flush=True)
(ROOT/'content/video-streams.json').write_text(json.dumps(videos,ensure_ascii=False,indent=2))
print('Locally archived videos:',sum(bool(v.get('hls')) for v in videos),flush=True)
