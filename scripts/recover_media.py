"""Retry unavailable original media without replacing valid migrated assets."""
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
from import_content import ROOT,save_asset,ERRORS
c=ROOT/'content';audit=json.loads((c/'migration-audit.json').read_text());urls=[x['url'] for x in audit['errors'] if '/editor/' in x['url'] or '/test/' in x['url']];recovered={}
def run(u):
    value=save_asset(u)
    if not value and '/test/scentairmachines.com/photo/' in u:value=save_asset(u.replace('/test/scentairmachines.com/photo/','/photo/'))
    return u,value
with ThreadPoolExecutor(max_workers=3) as pool:
    for f in as_completed([pool.submit(run,u) for u in urls]):
        u,value=f.result()
        if value:recovered[u]=value
        print(('Recovered ' if value else 'Unavailable ')+u,flush=True)
(c/'recovered-media.json').write_text(json.dumps(recovered,indent=2));(c/'recovery-audit.json').write_text(json.dumps({'recovered':len(recovered),'requested':len(urls),'errors':ERRORS},indent=2))
