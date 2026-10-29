from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import re, hashlib, json

ROOT=Path(__file__).parent
DIST=ROOT/'dist'
BASE='https://thinkwithdaniel.com/'
html=(ROOT/'reference-homepage.html').read_text(encoding='utf-8')
soup=BeautifulSoup(html,'html.parser')
removed=[]
for node in list(soup.find_all('script')):
    src=node.get('src','')
    body=node.string or node.get_text()
    if (src and urlparse(urljoin(BASE,src)).hostname != 'thinkwithdaniel.com') or (not src and any(t in body for t in ['gtag(', 'fbq(', 'gtm.start', 'dataLayer_content', 'smsUrl', 'submittedData', 'leadConnector', 'Tawk_API', 'window.location.search'])):
        removed.append(src or 'inline integration')
        node.decompose()
for node in list(soup.find_all(['noscript'])):
    node.decompose()
for frame in list(soup.find_all('iframe')):
    if 'reputation' in frame.get('src',''):
        frame['src']='reviews.html'
    else:
        frame.decompose()
for form in soup.find_all('form'):
    form['action']='#'
    form['method']='get'
    for field in form.select('input[type="hidden"]'):
        field.decompose()
for a in soup.find_all('a',href=True):
    href=a['href']
    if href.startswith(('tel:','mailto:','sms:')):
        a['href']='#contact-demo';a['data-demo-contact']='true'
    elif 'thinkwithdaniel.com' in href and urlparse(href).path not in ('','/'):
        if not href.startswith(BASE+'wp-content/'):
            a['data-original-href']=href;a['href']='#contact-demo'
for node in soup.select('meta[name="robots"]'):
    node['content']='noindex,nofollow'
meta=soup.new_tag('meta',attrs={'name':'robots','content':'noindex,nofollow'})
soup.head.append(meta)
title=soup.title
if title:title.string='ThinkWithDaniel — Private Homepage Replica'

mapping={}
errors=[]
def local(url):
    u=urlparse(url)
    ext=Path(u.path).suffix or '.bin'
    return 'assets/'+hashlib.sha256(url.encode()).hexdigest()[:16]+ext
def fetch(url):
    name=local(url)
    try:
        p=DIST/name;p.parent.mkdir(exist_ok=True)
        if p.exists():data=p.read_bytes()
        else:
            encoded=url.replace('\u2014','%E2%80%94').replace(' ','%20')
            data=urlopen(Request(encoded,headers={'User-Agent':'Mozilla/5.0'}),timeout=35).read();p.write_bytes(data)
        return url,name,data
    except Exception as e:
        return url,None,str(e)
def find_urls(text):
    text=text.replace('\\/','/')
    return set(re.findall(r'https?://[^\s\"\'<>\\)]+',text))
def allowed(url):
    u=urlparse(url)
    return (u.hostname=='thinkwithdaniel.com' and u.path.startswith(('/wp-content/','/wp-includes/'))) or u.hostname in ('fonts.googleapis.com','fonts.gstatic.com')
rendered=str(soup)
pending={u.replace('&amp;','&') for u in find_urls(rendered) if allowed(u)}
for link in soup.select('link[rel="stylesheet"]'):
    pending.add(urljoin(BASE,link['href']))
seen=set()
text_assets={}
while pending:
    batch=pending-seen;pending=set();seen.update(batch)
    with ThreadPoolExecutor(max_workers=12) as pool:
        for f in as_completed([pool.submit(fetch,u) for u in batch]):
            url,name,data=f.result()
            if not name:
                errors.append({'url':url,'error':data});continue
            mapping[url]=name
            if Path(name).suffix in ('.css','.js') or urlparse(url).hostname=='fonts.googleapis.com':
                content=data.decode('utf-8',errors='replace');text_assets[url]=content
                for candidate in find_urls(content):
                    if allowed(candidate):pending.add(candidate)
                if Path(name).suffix=='.css':
                    for candidate in re.findall(r'url\([\"\']?([^\)\"\']+)',content):
                        if not candidate.startswith('data:'):
                            full=urljoin(url,candidate)
                            if allowed(full):pending.add(full)
    print('Downloaded',len(mapping),'assets; queued',len(pending-seen),flush=True)
for url,content in text_assets.items():
    if Path(mapping[url]).suffix=='.css' or urlparse(url).hostname=='fonts.googleapis.com':
        content=re.sub(r'url\(([\"\']?)([^\)\"\']+)\1\)',lambda m:'url("'+('../'+mapping[urljoin(url,m.group(2))] if urljoin(url,m.group(2)) in mapping else m.group(2))+'")',content)
    for original,replacement in sorted(mapping.items(),key=lambda x:-len(x[0])):
        content=content.replace(original,'/'+replacement)
    (DIST/mapping[url]).write_text(content,encoding='utf-8')
for original,replacement in sorted(mapping.items(),key=lambda x:-len(x[0])):
    rendered=rendered.replace(original.replace('&','&amp;'),'/'+replacement).replace(original,'/'+replacement)
extra='''
<style>
.replica-chat-launcher{position:fixed;right:22px;bottom:24px;width:58px;height:58px;border-radius:50%;background:#ffcf00;color:#fff;border:0;font-size:28px;z-index:99999;box-shadow:0 4px 20px #0002;padding:0;cursor:pointer}
.replica-chat{display:none;position:fixed;right:22px;bottom:94px;width:min(350px,calc(100vw - 32px));background:white;border-radius:16px;box-shadow:0 10px 45px #0003;z-index:99999;overflow:hidden;font-family:Outfit,sans-serif;color:#2a2550}
.replica-chat.open{display:block}.replica-chat header{background:#2a2550;color:white;padding:18px;display:flex;justify-content:space-between}.replica-chat header button{background:none;color:white;border:0;padding:0;font-size:22px}.replica-chat p{padding:16px;margin:0}.replica-chat form{padding:0 16px 16px}.replica-chat input{width:100%;margin-bottom:10px}.replica-chat button{cursor:pointer}
</style>
<button class="replica-chat-launcher" aria-label="Open demo chat">♧</button>
<aside class="replica-chat" aria-label="Demo chat"><header>ThinkWithDaniel <button aria-label="Close demo chat">×</button></header><p>Homepage replica preview. Messages and form entries are not sent to the original business.</p><form><input aria-label="Your message" placeholder="Type your message…" required><button type="submit">Send</button></form><p class="demo-response" hidden>Demo only — your message was not sent.</p></aside>
<script>
const panel=document.querySelector('.replica-chat');
function openDemo(e){if(e)e.preventDefault();panel.classList.add('open')}
document.querySelector('.replica-chat-launcher').addEventListener('click',openDemo);
panel.querySelector('header button').onclick=()=>panel.classList.remove('open');
document.querySelectorAll('.ghl-open,[data-demo-contact],a[href="#contact-demo"]').forEach(b=>b.addEventListener('click',openDemo));
document.addEventListener('submit',e=>{e.preventDefault();e.stopImmediatePropagation();if(panel.contains(e.target)){panel.querySelector('.demo-response').hidden=false;e.target.reset()}else{openDemo();panel.querySelector('.demo-response').hidden=false}},true);
</script>
'''
rendered=rendered.replace('</body>',extra+'</body>')
(DIST/'index.html').write_text(rendered,encoding='utf-8')
(DIST/'reviews.html').write_text('''<!doctype html><html><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font:14px Arial;color:#555;margin:16px;text-align:center}button{background:#00cbaa;border:0;color:white;padding:18px;border-radius:6px;font-size:16px;font-weight:bold}.review{margin:30px 0;background:#f1edff;padding:24px;text-align:left;border-radius:14px;box-shadow:0 4px 12px #0001;line-height:1.7}.stars{color:#ffb900;font-size:22px}small{color:#888}</style><p>95 reviews</p><button onclick="document.querySelector('.notice').hidden=false">Write a review</button><p class="notice" hidden>Replica preview — reviews are not submitted.</p><div class="review"><div class="stars">5 ★★★★★</div><p>Review preview</p><small>This local preview preserves the review card layout. Live customer reviews are not connected.</small></div><p>‹　1　…　2　3　4　…　95　›</p></html>''',encoding='utf-8')
(ROOT/'asset-report.json').write_text(json.dumps({'downloaded':len(mapping),'errors':errors,'removed_integrations':removed},indent=2))
(ROOT/'README.md').write_text('''# ThinkWithDaniel homepage replica

Private visual reconstruction using the reference homepage markup and downloaded public assets. Open through an HTTP server with dist as its document root. Chat, contact links and form submissions are local demo interactions; original advertising trackers and CRM integrations are removed. Review widget uses an explicitly labeled local placeholder. Service links open the contact demo; separate service pages have not been replicated.
''')
print(json.dumps({'assets':len(mapping),'failed':len(errors),'html_bytes':len(rendered)}))
