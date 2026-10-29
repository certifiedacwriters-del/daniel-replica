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

# Replace the original header wordmark with the project-owned PrepWthDian artwork.
brand_assets = {
    'prepwthdian-logo.png': (1024, 150),
    'prepwthdian-logo-768.png': (768, 112),
    'prepwthdian-logo-300.png': (300, 44),
}
for filename in brand_assets:
    source = ROOT / 'source-assets' / filename
    destination = DIST / 'assets' / filename
    destination.write_bytes(source.read_bytes())
rendered = rendered.replace('/assets/e19cd3c77f580a20.png', '/assets/prepwthdian-logo.png')
rendered = rendered.replace('/assets/0254f1f57243d1ed.png', '/assets/prepwthdian-logo-768.png')
rendered = rendered.replace('/assets/cf2f6f9aff1184e1.png', '/assets/prepwthdian-logo-300.png')
rendered = rendered.replace('<img alt="" class="attachment-full size-full wp-image-8063"', '<img alt="PrepWthDian" class="attachment-full size-full wp-image-8063"', 1)
extra='''
<style>
.replica-chat-launcher{position:fixed;right:24px;bottom:26px;width:66px;height:66px;border-radius:50%!important;background:linear-gradient(145deg,#2ee878 0%,#1bc760 48%,#0da54a 100%);color:#fff;border:2px solid #ffffffd6;z-index:99999;box-shadow:0 16px 38px #07944752,0 4px 12px #11142624,inset 0 2px 2px #ffffff73;padding:0;cursor:pointer;transition:transform .25s ease,box-shadow .25s ease;display:flex;align-items:center;justify-content:center;overflow:hidden}
.replica-chat-launcher:hover{transform:translateY(-4px) scale(1.045);box-shadow:0 22px 50px #0794476b,0 6px 16px #1114262b,inset 0 2px 2px #ffffff80}.replica-chat-launcher:active{transform:translateY(-1px) scale(.97)}.replica-chat-launcher svg{width:34px!important;height:34px!important;min-width:34px;display:block;fill:currentColor;filter:drop-shadow(0 1px 1px #087c3880)}
.replica-chat{display:block;position:fixed;right:24px;bottom:104px;width:min(390px,calc(100vw - 32px));background:#ffffffd9;border:1px solid #fff;backdrop-filter:blur(24px) saturate(160%);-webkit-backdrop-filter:blur(24px) saturate(160%);border-radius:26px;box-shadow:0 28px 80px #1d24402e;z-index:99999;overflow:hidden;font-family:Outfit,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#171a2c;opacity:0;transform:translateY(16px) scale(.97);pointer-events:none;transition:opacity .25s ease,transform .25s ease}
.replica-chat.open{opacity:1;transform:none;pointer-events:auto}.replica-chat header{background:linear-gradient(135deg,#171a2c,#292d50);color:white;padding:20px 22px;display:flex;justify-content:space-between;align-items:center}.replica-chat header span{display:flex;align-items:center;gap:10px;font-size:17px;font-weight:600}.replica-chat header span:before{content:"";width:10px;height:10px;border-radius:50%;background:#2ee87c;box-shadow:0 0 0 5px #2ee87c22}.replica-chat header button{background:#ffffff14;color:white;border:1px solid #ffffff21;border-radius:50%;width:34px;height:34px;padding:0;font-size:22px}.replica-chat p{padding:18px 22px 12px;margin:0;color:#5c6075;line-height:1.55}.replica-chat form{padding:0 22px 22px}.replica-chat textarea{width:100%;min-height:118px;resize:vertical;margin:0 0 13px;padding:15px 16px;border:1px solid #dfe2ec;border-radius:16px;background:#fff;color:#171a2c;font:inherit;box-shadow:inset 0 1px 2px #1111;outline:none;transition:border .2s,box-shadow .2s}.replica-chat textarea:focus{border-color:#19b95d;box-shadow:0 0 0 4px #20c86a18}.replica-chat form button{width:100%;border:0;border-radius:15px;padding:14px 18px;background:linear-gradient(135deg,#25d366,#17ad52);color:white;font:600 15px/1 Outfit,sans-serif;box-shadow:0 10px 25px #20b85a35;cursor:pointer}.replica-chat button{cursor:pointer}
html{scroll-behavior:smooth}body{background:#f7f8fb!important;color:#171a2c;-webkit-font-smoothing:antialiased}.elementor-location-header .elementor-element-b38f107{background:#ffffffc7!important;backdrop-filter:blur(20px) saturate(160%);-webkit-backdrop-filter:blur(20px) saturate(160%);border-bottom:1px solid #ffffffc9;box-shadow:0 12px 40px #19213a0d}.elementor-button{border-radius:999px!important;box-shadow:0 9px 24px #242b4818;transition:transform .2s ease,box-shadow .2s ease!important}.elementor-button:hover{transform:translateY(-2px);box-shadow:0 14px 30px #242b4828}.elementor-widget-image img{transition:transform .45s cubic-bezier(.2,.8,.2,1),filter .45s ease}.image-zoom-in:hover img{transform:scale(1.025)!important;filter:saturate(1.04)}.elementor-accordion-item,.e-n-accordion-item{border-radius:18px!important;overflow:hidden;box-shadow:0 12px 35px #1b23420d}.elementor-field,.elementor-field-textual{border-radius:14px!important;background:#fff!important;border-color:#e1e4ed!important;box-shadow:inset 0 1px 2px #10152a0a}.elementor-element-61670ec .e-con-inner,.elementor-element-7c33530 .e-con-inner{border-radius:28px}.elementor-location-footer{background:#111426!important}@media(max-width:767px){.replica-chat-launcher{right:16px;bottom:18px;width:60px;height:60px;border-radius:50%!important}.replica-chat-launcher svg{width:32px!important;height:32px!important;min-width:32px}.replica-chat{right:16px;bottom:92px}.elementor-location-header .elementor-element-b38f107{border-radius:0}}
</style>
<button class="replica-chat-launcher" aria-label="Message us on WhatsApp"><svg aria-hidden="true" viewBox="0 0 448 512"><path d="M380.9 97.1C339 55.1 283.2 32 223.9 32c-122.4 0-222 99.6-222 222 0 39.1 10.2 77.3 29.6 111L0 480l117.7-30.9c32.4 17.7 68.9 27 106.1 27h.1c122.3 0 224.1-99.6 224.1-222 0-59.3-25.2-115-67.1-157zm-157 341.6c-33.2 0-65.7-8.9-94-25.8l-6.7-4-69.8 18.3L72 359.2l-4.4-7c-18.5-29.4-28.2-63.4-28.2-98.2 0-101.7 82.8-184.5 184.6-184.5 49.3 0 95.6 19.2 130.4 54.1 34.8 34.9 56.2 81.2 56.1 130.5 0 101.8-84.9 184.6-186.6 184.6zm101.2-138.2c-5.5-2.8-32.8-16.1-37.9-18-5.1-1.9-8.8-2.8-12.5 2.8s-14.3 18-17.6 21.8c-3.2 3.7-6.5 4.2-12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3 1.8-3.7.9-6.9-.5-9.7-1.4-2.8-12.5-30.1-17.1-41.2-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2s-9.7 1.4-14.8 6.9c-5.1 5.6-19.4 19-19.4 46.3s19.9 53.7 22.6 57.4c2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9 10.7-1.6 32.8-13.4 37.4-26.4 4.6-13 4.6-24.1 3.2-26.4-1.3-2.5-5-3.9-10.5-6.6z"/></svg></button>
<aside class="replica-chat" aria-label="WhatsApp message"><header><span>WhatsApp Concierge</span><button aria-label="Close WhatsApp message">×</button></header><p>How can we help? Write your message below and continue securely in WhatsApp.</p><form><textarea aria-label="Your WhatsApp message" placeholder="Type your message…" required></textarea><button type="submit">Continue to WhatsApp</button></form></aside>
<script>
const panel=document.querySelector('.replica-chat');
function openDemo(e){if(e)e.preventDefault();panel.classList.add('open')}
document.querySelector('.replica-chat-launcher').addEventListener('click',openDemo);
panel.querySelector('header button').onclick=()=>panel.classList.remove('open');
document.querySelectorAll('.ghl-open,[data-demo-contact],a[href="#contact-demo"]').forEach(b=>b.addEventListener('click',openDemo));
document.addEventListener('submit',e=>{e.preventDefault();e.stopImmediatePropagation();if(panel.contains(e.target)){const message=panel.querySelector('textarea').value.trim();if(message){window.open('https://wa.me/14075753790?text='+encodeURIComponent(message),'_blank','noopener,noreferrer')}}else{openDemo()}},true);
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
