from pathlib import Path
from html import escape
from urllib.parse import quote
import json
import re
from polish import refine

ROOT=Path(__file__).parent
DOMAIN='https://decada.store'
INTRO_VARIANT='name'  # 'tag' (etiqueta que gira) or 'name' (logo cargando con puntada)
PRODUCTS=[
 dict(slug='vaquero-tommy-hilfiger-azul-talla-31',name='Vaquero Tommy Hilfiger azul',size='31/30',price='16,95 €',amount=16.95,front='tommy.jpg',back='tommy-back.jpg',kind='Vaqueros',feature=True),
 dict(slug='camiseta-manga-larga-superdry-azul-y-gris',name='Camiseta manga larga Superdry azul y gris',size='S',price='9,95 €',amount=9.95,front='superdry.jpg',back='superdry-back.jpg',kind='Camisetas'),
 dict(slug='vaquero-vintage-dressing-onyx-jeans-azul-talla-27',name='Vaquero Vintage Dressing Onyx Jeans azul',size='27',price='19,95 €',amount=19.95,front='onyx.jpg',back='onyx-back.jpg',kind='Vaqueros'),
 dict(slug='vaquero-levi-s-560-hombre-corte-recto-lavado-medio',name="Vaquero Levi's 560 hombre lavado medio",size='W38 L30',price='19,95 €',amount=19.95,front='levis.jpg',back='levis-back.jpg',kind='Vaqueros'),
 dict(slug='vaquero-hamilton-azul-talla-27',name='Vaquero Hamilton azul',size='27',price='19,95 €',amount=19.95,front='hamilton.jpg',back='hamilton-back.jpg',kind='Vaqueros')]
CATALOG=json.loads((ROOT/'catalog-data.json').read_text(encoding='utf-8'))
PHOTO_EXT=('.webp','.jpg','.jpeg','.png','.avif')
def garment_photos(slug,listed=()):
 """Todas las fotos de una prenda. Para añadir fotos basta con guardarlas en assets/catalog/
 como <slug>-1.webp, <slug>-2.webp, <slug>-3.webp… (también .jpg/.png). El número marca el orden:
 1 modelo delante, 2 modelo detrás, 3 prenda delante, 4 prenda detrás, 5+ etiquetas y detalles."""
 found={}
 for img in listed:
  if img.startswith('https://'):found[img]=None;continue
  f=ROOT/'assets'/img
  if f.exists() and f.stat().st_size>0:found[img]=None
 folder=ROOT/'assets'/'catalog'
 extra=[]
 for f in folder.glob(slug+'-*'):
  tail=f.stem[len(slug)+1:]
  if f.suffix.lower() in PHOTO_EXT and tail.isdigit() and f.stat().st_size>0:extra.append((int(tail),'catalog/'+f.name))
 for _,img in sorted(extra):found[img]=None
 return list(found)
MEASURES=json.loads((ROOT/'product-measures.json').read_text(encoding='utf-8'))
for gender,items in CATALOG.items():
 for item in items:
  item['gender']=gender
  slug=item['slug']
  raw_name=item['name']
  item['name']=re.sub(r',?\s+talla\s+[^,]+$','',raw_name,flags=re.I).strip()
  item['name']=re.sub(r'\b(hombre|mujer)\b','',item['name'],flags=re.I)
  item['name']=re.sub(r'\s{2,}',' ',item['name']).strip(' ,-')
  item['size']=item['meta'].split(' · ')[0].removeprefix('TALLA ').strip() or 'Consultar talla'
  meta_condition=item['meta'].split(' · ')[1].strip() if ' · ' in item['meta'] else ''
  item['condition']=item.get('condition') or {'MUY BUENO':'Muy buen estado','EXCELLENT':'Excelente estado'}.get(meta_condition,meta_condition.title())
  item['amount']=float(item['price'].replace(' €','').replace(',','.')) if item['price'] else 0
  n=item['name'].lower()
  item['kind']='Pantalones' if any(w in n for w in ('vaquero','pantalón','pantalon','jeans','track pant','falda')) else 'Camisetas y polos' if any(w in n for w in ('camiseta','camisa','polo')) else 'Chaquetas' if any(w in n for w in ('chaqueta','trench','chaleco')) else 'Jerséis' if 'jersey' in n else 'Sudaderas' if 'sudadera' in n else 'Otras prendas'
  allowed={'Pantalones':{'CINTURA','ENTREPIERNA','LARGO'},'Camisetas y polos':{'PECHO','HOMBROS','LARGO'},'Chaquetas':{'PECHO','HOMBROS','LARGO'},'Jerséis':{'PECHO','HOMBROS','LARGO'},'Sudaderas':{'PECHO','HOMBROS','LARGO'}}.get(item['kind'],set())
  measurements={k:v for k,v in MEASURES.get(slug,{}).items() if k in allowed}
  if 'falda' in n:measurements.pop('ENTREPIERNA',None)
  if slug=='camiseta-adidas-originals-blanca-talla-s':measurements.pop('LARGO',None)
  if slug=='vaquero-levi-s-560-hombre-corte-recto-lavado-medio':measurements.pop('CINTURA',None)
  item['measurements']=measurements
  valid=garment_photos(slug,item.get('imgs',[]))
  if slug=='vaquero-tommy-hilfiger-azul-talla-31':valid=['tommy.jpg','tommy-back.jpg']+[v for v in valid if 'tommy-hilfiger' in v]
  item['photos']=valid or ['logo.webp']
  item['front']=item['photos'][0]
  item['back']=item['photos'][1] if len(item['photos'])>1 else item['front']
PRODUCTS=list({p['slug']:p for p in [*PRODUCTS,*sum(CATALOG.values(),[])]}.values())
for product in PRODUCTS:product.setdefault('measurements',MEASURES.get(product['slug'],{}))
for i,product in enumerate(PRODUCTS,start=1):product['archno']=f'{i:03d}'
PRICE_BANDS=[('low','HASTA 12 €'),('mid','12–18 €'),('high','+18 €')]
def price_key(amount):
 return 'low' if amount<12 else 'mid' if amount<18 else 'high'
# Pieza destacada de la home: marca "destacado": true en catalog-data.json en la prenda que quieras
# resaltar de cada drop. Si no marcas ninguna, se usa la primera del catálogo como respaldo.
FEATURED=next((p for p in PRODUCTS if p.get('destacado')),PRODUCTS[0])

def _brand_counts():
 import collections
 c=collections.Counter(b for b in (brand_for(q['name']) for q in PRODUCTS) if b)
 return sorted(c.items(),key=lambda x:(-x[1],x[0]))
GROUP_LABELS={'Chaquetas':'CHAQUETAS','Jerséis':'JERSÉIS','Camisetas':'CAMISETAS Y POLOS','Pantalones':'PANTALONES','Sudaderas':'SUDADERAS','Otras prendas':'OTRAS PIEZAS'}
GROUP_SLUGS={'Chaquetas':'chaquetas','Jerséis':'jerseis','Camisetas':'camisetas','Pantalones':'pantalones','Sudaderas':'sudaderas','Otras prendas':'otras'}
GENDER_LABELS={'hombre':'HOMBRE','mujer':'MUJER','ninos':'NIÑOS'}
def group_of(p):
 # PROVISIONAL: en producción el tipo sale del inventario, no del nombre.
 name=p['name'].lower()
 if any(t in name for t in ('pantalón','pantalon','vaquero','jeans','track pant','falda')):return 'Pantalones'
 if 'jersey' in name:return 'Jerséis'
 if any(t in name for t in ('camiseta','camisa','polo')):return 'Camisetas'
 if any(t in name for t in ('chaqueta','trench','chaleco')):return 'Chaquetas'
 if 'sudadera' in name:return 'Sudaderas'
 return 'Otras prendas'

def size_key(size):
 s=(size or '').upper().replace('DE MUJER','').replace('NIÑO','').strip()
 m=re.match(r'W?(\d{2})\b',s)
 if m:return m.group(1)
 m=re.match(r'(\d+-\d+)Y',s)
 if m:return m.group(1)+' AÑOS'
 m=re.match(r'(XXS|XS|XXL|XL|S|M|L)\b',s)
 return m.group(1) if m else s or 'ÚNICA'
SIZE_ORDER=['XXS','XS','S','M','L','XL','XXL']
def size_sort(k):
 return (0,SIZE_ORDER.index(k)) if k in SIZE_ORDER else (1,int(k)) if k.isdigit() else (2,k)

CLOUDINARY_MARK='res.cloudinary.com'
UPLOAD_MARK='/upload/'
def _cloudinary_parts(value):
 if CLOUDINARY_MARK in value and UPLOAD_MARK in value:
  head,tail=value.split(UPLOAD_MARK,1)
  return head,tail
 return None
def photo_url(value,prefix):
 if value.startswith('https://'):
  parts=_cloudinary_parts(value)
  if parts and 'f_auto' not in value:  # ya transformada (viene de variants()): no envolver dos veces
   head,tail=parts
   return f'{head}{UPLOAD_MARK}f_auto,q_auto/{tail}'
  return value
 return prefix+'assets/'+value

try:
 from PIL import Image as _PIL
except ImportError:
 _PIL=None
VARIANT_WIDTHS=(480,960,1600)
_variant_cache={}
def variants(value):
 """Genera copias más ligeras (480/960/1600 px) de cada foto.
 Fotos locales: copias .webp en assets/_r/ sin ampliar nunca el original.
 Fotos remotas de Cloudinary (inventario real): usa las transformaciones de
 Cloudinary (f_auto,q_auto,w_XXX) al vuelo, sin descargar ni reprocesar nada."""
 if value in _variant_cache:return _variant_cache[value]
 cloud=_cloudinary_parts(value) if value.startswith('https://') else None
 if cloud:
  head,tail=cloud
  out=[(f'{head}{UPLOAD_MARK}f_auto,q_auto,c_limit,w_{w}/{tail}',w) for w in VARIANT_WIDTHS]
  out.append((f'{head}{UPLOAD_MARK}f_auto,q_auto/{tail}',2000))
  _variant_cache[value]=out
  return out
 src=ROOT/'assets'/value;out=[]
 if _PIL and src.exists() and src.stat().st_size>0 and not value.startswith('https://'):
  try:
   with _PIL.open(src) as im:
    w,h=im.size
    for target in VARIANT_WIDTHS:
     if target>=w:continue
     rel=f'_r/{Path(value).stem}-{target}.webp';dest=ROOT/'assets'/rel
     if not dest.exists() or dest.stat().st_mtime<src.stat().st_mtime:
      dest.parent.mkdir(parents=True,exist_ok=True)
      im.convert('RGB').resize((target,round(h*target/w)),_PIL.LANCZOS).save(dest,'WEBP',quality=86,method=6)
     out.append((rel,target))
    out.append((value,w))
  except OSError:out=[]
 _variant_cache[value]=out
 return out
def img_attrs(value,prefix,sizes):
 v=variants(value)
 if len(v)<2:return f'src="{photo_url(value,prefix)}"'
 return f'src="{photo_url(value,prefix)}" srcset="{", ".join(f"{photo_url(r,prefix)} {w}w" for r,w in v)}" sizes="{sizes}"'
CARD_SIZES='(max-width:700px) 46vw, (max-width:1100px) 31vw, 24vw'

IG='https://instagram.com/decada.store'
CONTACT_EMAIL='storedecada@gmail.com'
# Formulario: FormSubmit reenvía cada consulta a CONTACT_EMAIL. El primer envío llega como
# correo de activación a esa dirección; hay que pulsar "Activate Form" una sola vez.
FORM_ENDPOINT=f'https://formsubmit.co/{CONTACT_EMAIL}'
# Destinos oficiales verificados. Vinted admite varias cuentas: el icono del
# header/footer siempre manda a la sección de Contacto (no puede elegir una
# sola), y ahí se listan todas.
VINTED_ACCOUNTS=[('storedecada','https://www.vinted.es/member/3150995643'),('asiersoto','https://www.vinted.es/member/227811272')]
WHATSAPP_URL='https://wa.me/34611021832'
WHATSAPP_DISPLAY='+34 611 02 18 32'

def svg(kind):
 if kind=='instagram':return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.7" r=".7" fill="currentColor" stroke="none"/></svg>'
 if kind=='whatsapp':return '<svg class="wa-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" stroke="none" d="M12.04 2a9.94 9.94 0 0 0-8.5 15.1L2 22l5.02-1.52A10 10 0 1 0 12.04 2Zm0 18.14a8.2 8.2 0 0 1-4.18-1.14l-.3-.17-2.98.9.97-2.91-.2-.31a8.15 8.15 0 1 1 6.69 3.63Zm4.48-6.1c-.24-.12-1.43-.7-1.65-.78-.22-.08-.38-.12-.54.12-.16.25-.62.78-.76.94-.14.16-.28.18-.52.06a6.66 6.66 0 0 1-1.94-1.2 7.33 7.33 0 0 1-1.35-1.67c-.14-.24-.01-.37.1-.49.11-.11.24-.28.36-.42.12-.14.16-.24.24-.4.08-.16.04-.3-.02-.42-.06-.12-.54-1.29-.74-1.77-.2-.46-.4-.4-.54-.4h-.46c-.16 0-.42.06-.64.3-.22.25-.84.82-.84 2s.86 2.32.98 2.48c.12.16 1.7 2.6 4.13 3.64.58.25 1.03.4 1.38.52.58.18 1.1.16 1.52.1.46-.07 1.43-.59 1.63-1.16.2-.57.2-1.06.14-1.16-.06-.1-.22-.16-.46-.28Z"/></svg>'
 if kind=='bag':return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 8h15l-1 12h-13l-1-12Z"/><path d="M9 9V6a3 3 0 0 1 6 0v3"/></svg>'
 return ''

def socials(prefix='',mobile=False):
 cls='social-row mobile-social' if mobile else 'social-row'
 vinted=prefix+'contacto/index.html#vinted'
 whatsapp=WHATSAPP_URL or prefix+'contacto/index.html#whatsapp'
 return f'<div class="{cls}" aria-label="Redes sociales y contacto"><a href="{IG}" target="_blank" rel="noopener noreferrer" aria-label="Instagram de DÉCADA" title="Instagram">{svg("instagram")}</a><a href="{vinted}" aria-label="Vinted de DÉCADA" title="Vinted"><span class="vinted-logo" aria-hidden="true">vinted</span></a><a href="{whatsapp}" aria-label="WhatsApp de DÉCADA" title="WhatsApp">{svg("whatsapp")}</a></div>'

def header(prefix):
 return f'''<div class="announce" aria-label="Avisos de DÉCADA"><p class="is-on">PIEZAS ÚNICAS <i>✦</i> SIN REPOSICIÓN</p><p>SELECCIONADO A MANO <i>✦</i> SOURCED IN UK</p><p>ZERO TOLERANCE FOR FAKES <i>✦</i> REVISADO PIEZA A PIEZA</p></div><header class="site-header"><a class="logo" href="{prefix}index.html" aria-label="DÉCADA, inicio"><img src="{prefix}assets/logo.webp" alt="DÉCADA" width="156" height="52"></a><nav class="main-nav" id="nav" aria-label="Navegación principal"><a href="{prefix}catalogo/index.html">CATÁLOGO</a><a href="{prefix}catalogo/hombre/index.html">HOMBRE</a><a href="{prefix}catalogo/mujer/index.html">MUJER</a><a href="{prefix}catalogo/ninos/index.html">NIÑOS</a><a href="{prefix}marca/index.html">LA MARCA</a><a href="{prefix}como-comprar/index.html">CÓMO COMPRAR</a>{socials(prefix,mobile=True)}</nav><div class="header-tools">{socials(prefix)}<button class="search-open" type="button" aria-label="Buscar prendas" data-search-open><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg></button><a class="bag-link" href="{prefix}carrito/index.html" aria-label="Abrir bolsa de la compra">{svg('bag')}<span>BOLSA</span><b data-cart-count hidden>0</b></a><button class="menu-button" type="button" aria-expanded="false" aria-controls="nav" aria-label="Abrir menú"><span></span><span></span></button></div></header><dialog class="search-dialog" aria-label="Buscar en DÉCADA" data-search-dialog><div class="search-box"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg><input type="search" id="search-q" placeholder="Busca por marca, prenda o talla" autocomplete="off" aria-label="Buscar prendas" data-search-input><button type="button" class="search-close" aria-label="Cerrar búsqueda" data-search-close>ESC</button></div><div class="search-body"><div class="search-brands" data-search-brands><div class="search-suggest"><p>BÚSQUEDAS RÁPIDAS</p><div>{QUICK_CHIPS}</div></div><div class="search-suggest"><p>MARCAS EN EL ARCHIVO</p><div>{BRAND_CHIPS}</div></div><div class="search-latest"><p>RECIÉN LLEGADAS AL ARCHIVO</p><ul class="search-results" data-search-latest></ul></div></div><p class="search-count" data-search-count aria-live="polite"></p><ul class="search-results" data-search-results></ul></div></dialog>'''

def footer(prefix):
 return f'''<footer class="site-footer"><div class="footer-grid"><div class="footer-brand"><img src="{prefix}assets/logo.webp" alt="DÉCADA" width="235" height="85"><p>Vintage y streetwear seleccionado a mano.<br>Una pieza. Una talla. Una nueva historia.</p><p class="foot-claim">SOURCED IN UK. CURATED IN SPAIN.</p></div><div><h2>EXPLORA</h2><a href="{prefix}catalogo/index.html">Todas las prendas</a><a href="{prefix}catalogo/hombre/index.html">Hombre</a><a href="{prefix}catalogo/mujer/index.html">Mujer</a><a href="{prefix}catalogo/ninos/index.html">Niños</a><a href="{prefix}index.html#novedades">En el archivo</a></div><div><h2>DÉCADA</h2><a href="{prefix}marca/index.html">Nuestra historia</a><a href="{prefix}como-comprar/index.html">Cómo comprar</a><a href="{prefix}guia-tallas/index.html">Guía de tallas</a><a href="{prefix}contacto/index.html">Contacto</a><a href="{prefix}carrito/index.html">Tu bolsa</a><a href="mailto:storedecada@gmail.com">storedecada@gmail.com</a></div><div><h2>AVISO DE DROPS</h2><p>Te escribimos cuando salgan piezas nuevas.</p><form class="footer-drop" action="{FORM_ENDPOINT}" method="POST" data-drop-form novalidate><input type="hidden" name="_subject" value="Alta en el aviso de drops · decada.store"><input type="hidden" name="_template" value="table"><input type="hidden" name="_captcha" value="false"><div class="form-honey" aria-hidden="true"><input type="text" name="_honey" tabindex="-1" autocomplete="off"></div><input type="email" name="email" placeholder="Tu email" aria-label="Tu email" autocomplete="email" required maxlength="120"><button type="submit" aria-label="Apuntarme al aviso de drops">↗</button><label class="footer-drop-check"><input type="checkbox" name="Acepta privacidad" value="Sí" required><span>Acepto la <a href="{DOMAIN}/politica-privacidad" target="_blank" rel="noopener noreferrer">privacidad</a></span></label><p class="drop-form-status" role="status" data-drop-status hidden></p></form>{socials(prefix)}</div></div><div class="footer-legal"><span>© 2026 DÉCADA · EST. 2004</span><div><a href="{DOMAIN}/aviso-legal">Aviso legal</a><a href="{DOMAIN}/politica-privacidad">Privacidad</a><a href="{DOMAIN}/politica-cookies">Cookies</a></div><span>PAST · PRESENT · FUTURE</span></div></footer>'''

def card(product,prefix='',featured=False):
 p=product;name=escape(p['name']);cl='product-card featured' if featured else 'product-card'
 brand=brand_for(p['name']);group=GROUP_SLUGS[group_of(p)]
 label=f"<b>{escape(brand.upper())}</b> · {p['kind']}" if brand else p['kind']
 return f'''<a class="{cl}" href="{prefix}productos/{p['slug']}/index.html" data-name="{name.lower()}" data-category="{p['kind'].lower()}" data-group="{group}" data-size="{size_key(p['size'])}" data-price="{p['amount']}" data-price-band="{price_key(p['amount'])}"><div class="product-photo"><span class="last-badge">ÚLTIMA UNIDAD</span><img {img_attrs(p['front'],prefix,CARD_SIZES)} alt="{name}, vista principal" loading="lazy" width="600" height="600"><img class="photo-back" {img_attrs(p['back'],prefix,CARD_SIZES)} alt="{name}, segunda vista" loading="lazy" width="600" height="600"><span class="size-label">{p['size']}</span></div><div class="product-caption"><div><span class="eyebrow">{label}</span><h3>{name}</h3></div><strong>{p['price']}</strong></div><span class="card-cta">VER LA PRENDA ↗</span></a>'''

def featured_card(p):
 name=escape(p['name']);brand=brand_for(p['name']);group=GROUP_SLUGS[group_of(p)]
 label=f"<b>{escape(brand.upper())}</b> · {p['kind']}" if brand else p['kind']
 return f'''<a class="product-card featured featured-duo" href="productos/{p['slug']}/index.html" data-name="{name.lower()}" data-category="{p['kind'].lower()}" data-group="{group}" data-price="{p['amount']}"><div class="featured-photos"><img src="{photo_url(p['front'],'')}" alt="{name}, delante" loading="lazy" width="600" height="600"><img src="{photo_url(p['back'],'')}" alt="{name}, detrás" loading="lazy" width="600" height="600"><span class="size-label">{p['size']}</span><span class="featured-tag">DESTACADA</span></div><div class="product-caption"><div><span class="eyebrow">{label}</span><h3>{name}</h3></div><strong>{p['price']}</strong></div><span class="card-cta">VER LA PRENDA ↗</span></a>'''

ARROW_L='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>'
ARROW_R='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>'
AUTH_STAMP='<span class="auth-stamp" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M4 12l5 5L20 6"/></svg>OK</span>'
def rail_section(head,link,cards,attrs,label):
 return f'<section class="type-group" data-rail-section {attrs}><header class="type-head">{head}<div class="rail-controls">{link}<div class="rail-buttons"><button type="button" class="rail-btn" data-rail-prev aria-label="Ver prendas anteriores de {label}" disabled>{ARROW_L}{AUTH_STAMP}</button><button type="button" class="rail-btn" data-rail-next aria-label="Ver más prendas de {label}">{ARROW_R}{AUTH_STAMP}</button></div></div></header><div class="type-rail" data-type-grid data-product-rail>{cards}</div><div class="rail-progress" aria-hidden="true"><span></span></div></section>'

def spotlight(p):
 # Destacada con forma de etiqueta de precio vintage.
 name=escape(p['name']);brand=brand_for(p['name'])
 meas=' · '.join(f'{escape(k.title())} {escape(v)}' for k,v in list((p.get('measurements') or {}).items())[:3])
 cond=f'<span>{escape(p["condition"])}</span>' if p.get('condition') else ''
 return f'''<article class="tag-feature"><a class="tag-photo" href="productos/{p['slug']}/index.html" aria-label="Ver {name}"><img {img_attrs(p['front'],'','220px')} alt="{name}" width="220" height="220" loading="lazy"></a><div class="tag-info"><p class="tag-kicker">ARCHIVO Nº{p['archno']} <i>·</i> PIEZA DESTACADA</p><p class="tag-brand">{escape(brand.upper()) if brand else escape(p['kind'].upper())}</p><h3><a href="productos/{p['slug']}/index.html">{name}</a></h3><div class="tag-meta"><span>TALLA {escape(p['size'])}</span>{cond}<span>UNIDAD ÚNICA</span></div>{f'<p class="tag-measures">{meas}</p>' if meas else ''}</div><div class="tag-stub"><span class="tag-hole" aria-hidden="true"></span><p class="tag-price">{p['price']}</p><a class="button pink tag-cta" href="productos/{p['slug']}/index.html">VER LA PRENDA <span>↗</span></a><button class="tag-add add-preview" type="button" data-sku="{p['slug']}" data-name="{name}" data-price="{p['price']}" data-image="{photo_url(p['front'],'')}">AÑADIR A LA BOLSA <span>＋</span></button></div></article>'''

def brand_row():
 items=''.join(f'<li><button type="button" data-search-term="{escape(b)}"><strong>{escape(b.upper())}</strong><span>{n} {"pieza" if n==1 else "piezas"}</span></button></li>' for b,n in BRANDS[:12])
 return f'''<section class="brand-row" aria-labelledby="brands-title"><div class="brand-row-head"><p class="eyebrow">BUSCA POR MARCA</p><h2 id="brands-title">LAS MARCAS DEL ARCHIVO<span>.</span></h2></div><ul>{items}</ul></section>'''

def drop_form(cls=''):
 return f'''<form class="drop-form {cls}" action="{FORM_ENDPOINT}" method="POST" data-drop-form novalidate><input type="hidden" name="_subject" value="Alta en el aviso de drops · decada.store"><input type="hidden" name="_template" value="table"><input type="hidden" name="_captcha" value="false"><input type="hidden" name="Tipo" value="Aviso de drops"><div class="form-honey" aria-hidden="true"><input type="text" name="_honey" tabindex="-1" autocomplete="off"></div><label class="drop-form-field"><span class="visually-hidden">Tu email</span><input type="email" name="email" placeholder="Tu email" autocomplete="email" required maxlength="120"></label><button class="button pink" type="submit">AVÍSAME <span>↗</span></button><label class="drop-form-check"><input type="checkbox" name="Acepta privacidad" value="Sí" required><span>Acepto la <a href="{DOMAIN}/politica-privacidad" target="_blank" rel="noopener noreferrer">política de privacidad</a>. Solo usaremos tu email para avisarte de nuevos drops.</span></label><p class="drop-form-status" role="status" data-drop-status hidden></p></form>'''

def _front(slug):
 q=next((x for x in PRODUCTS if x['slug']==slug),None)
 return q['front'] if q else None

def brand_block():
 # Franja compacta: el proceso DÉCADA en una línea, sin fotos (la home ya tiene suficiente imagen).
 steps=[('BUSCAMOS','En proveedores de vintage de Reino Unido.'),('TRAEMOS','En lotes pequeños. Sin reposición.'),('CURAMOS','Etiquetas, estado y medidas, una a una.')]
 items=''.join(f'<li><span class="process-num">0{i+1}</span><h3>{w}<span>.</span></h3><p>{t}</p></li>' for i,(w,t) in enumerate(steps))
 return f'''<section class="process-band" aria-labelledby="brand-title"><div class="process-band-head"><p class="eyebrow">LA FORMA DÉCADA</p><h2 id="brand-title">SOURCED IN UK.<br><em>CURATED IN SPAIN.</em></h2><a class="under-link" href="marca/index.html">CONOCE DÉCADA ↗</a></div><ol class="process-band-steps">{items}</ol></section>'''

def drop_block():
 # Vista previa de las últimas piezas, con la forma de un perfil de Instagram (solo fotos de calle).
 slugs=['camiseta-adidas-negra-estampado-fragmentado-talla-m','camiseta-levi-s-mujer-rosa-manga-larga','camiseta-nike-gris-logo-camuflaje','sudadera-champion-azul-marino-talla-m','camiseta-nike-just-do-it-negra-talla-m','sudadera-nike-tech-fleece-hombre-negra-premium','chaleco-nike-air-negro-sin-mangas','camiseta-jordan-negra-talla-l','sudadera-puma-negra-talla-m']
 tiles=''.join(f'<a href="productos/{sl}/index.html" tabindex="-1"><img {img_attrs(_front(sl),"","(max-width:800px) 30vw, 12vw")} alt="" loading="lazy" width="300" height="300"></a>' for sl in slugs if _front(sl))
 return f'''<section class="drop-ig" aria-labelledby="drop-title"><div class="drop-ig-copy"><p class="eyebrow">EL PRÓXIMO DROP</p><h2 id="drop-title">QUIEN LLEGA ANTES, <em>ELIGE.</em></h2><p>Cada pieza existe una sola vez y no se repone. Déjanos tu email y te escribimos cuando publiquemos piezas nuevas.</p><ul class="drop-ig-points"><li><strong>1</strong> unidad por prenda</li><li><strong>0</strong> reposiciones</li><li><strong>100 %</strong> revisadas a mano</li></ul><p class="drop-form-label">RECIBE UN AVISO CUANDO SALGA EL PRÓXIMO DROP</p>{drop_form()}<a class="under-link drop-ig-follow-link" href="{IG}" target="_blank" rel="noopener noreferrer">O SÍGUENOS EN INSTAGRAM @DECADA.STORE ↗</a></div><div class="drop-ig-card" aria-hidden="true"><div class="drop-ig-top"><span class="drop-ig-avatar"><img src="assets/logo.webp" alt="" width="80" height="40"></span><div><strong>decada.store</strong><span>Vintage 90s / Y2K · Sourced in UK</span></div><a class="drop-ig-follow" href="{IG}" target="_blank" rel="noopener noreferrer" tabindex="-1">Seguir</a></div><div class="drop-ig-grid">{tiles}</div></div></section>'''

def pieces_label(count):
 return f'{count} PIEZA' if count==1 else f'{count} PIEZAS'

def product_copy(product):
 kind=product.get('kind','prenda')
 copy={
  'Pantalones':'Silueta seleccionada por su corte y su forma de caer. Revisa las medidas de cintura y largo para comparar el ajuste con uno de tus pantalones.',
  'Camisetas y polos':'Pieza seleccionada por su gráfica, acabado y presencia. Comprueba el ancho de pecho y el largo para valorar cómo te quedará.',
  'Chaquetas':'Capa exterior con carácter y una sola unidad disponible. Consulta el pecho, los hombros y el largo antes de elegirla.',
  'Jerséis':'Punto vintage elegido por su textura y silueta. Compara pecho, hombros y largo con una prenda que ya utilices.',
  'Sudaderas':'Sudadera vintage de unidad única, seleccionada por su corte y presencia. Revisa sus medidas reales antes de comprar.'
 }
 return copy.get(kind,'Pieza única seleccionada por DÉCADA. Consulta sus fotografías, estado y medidas antes de elegirla.')

def brand_for(name):
 brands=('Tommy Hilfiger','Levi\'s','Massimo Dutti','Fred Perry','La Martina','Hugo Boss','Nike','Adidas','Puma','Champion','Versace','Jordan','Vans','Fila','Trussardi','Guess','Superdry','Rustler','Hamilton','Ruta66')
 lowered=name.lower()
 return next((brand for brand in brands if brand.lower() in lowered),None)

def categories(prefix=''):
 return f'''<section class="categories" aria-label="Explorar por categoría"><a class="category" href="{prefix}catalogo/hombre/index.html"><img src="{prefix}assets/category-hombre.webp" alt="Editorial DÉCADA de hombre con chaqueta vintage" loading="lazy" width="1698" height="926"><span class="category-index">01 / EXPLORA</span><span class="category-bottom"><strong>HOMBRE</strong><em>VER SELECCIÓN ↗</em></span></a><a class="category" href="{prefix}catalogo/mujer/index.html"><img src="{prefix}assets/category-mujer.webp" alt="Editorial DÉCADA de mujer con chaqueta vintage" loading="lazy" width="1697" height="927"><span class="category-index">02 / EXPLORA</span><span class="category-bottom"><strong>MUJER</strong><em>VER SELECCIÓN ↗</em></span></a><a class="category kids-category" href="{prefix}catalogo/ninos/index.html"><img src="{prefix}assets/category-ninos.webp" alt="Modelo infantil con ropa de deporte vintage en una calle nocturna" loading="lazy"><span class="category-index">03 / EXPLORA</span><span class="category-bottom"><strong>NIÑOS</strong><em>VER SELECCIÓN ↗</em></span></a></section>'''

def shell(path,title,description,body,kind='website',extra_head='',og_image=None):
 body=refine(path,body)
 depth=len(Path(path).parts)-1;prefix='../'*depth
 canonical=DOMAIN+('/' if path=='index.html' else '/'+path.removesuffix('index.html'))
 site_data={'@context':'https://schema.org','@type':'Organization','name':'DÉCADA','url':DOMAIN+'/','logo':DOMAIN+'/assets/logo.webp','sameAs':[IG]}
 if INTRO_VARIANT=='name':
  intro=f'''<div class="intro-name" id="intro-splash" aria-hidden="true"><div class="grain" aria-hidden="true"></div><div class="name-rec" id="intro-rec"><span class="rec-dot"></span><b>REC <span id="intro-tc">00:00</span></b></div><div class="name-stage" id="intro-stage"><span class="corner tl"></span><span class="corner tr"></span><span class="corner bl"></span><span class="corner br"></span><p class="name-kicker" id="intro-kicker">DÉCADA &middot; EST. 2004</p><div class="name-mask" id="intro-mask"><img class="ghost ghost-r" src="{prefix}assets/logo.webp" alt="" aria-hidden="true" width="235" height="85"><img class="ghost ghost-c" src="{prefix}assets/logo.webp" alt="" aria-hidden="true" width="235" height="85"><span class="scan"></span><img src="{prefix}assets/logo.webp" alt="DÉCADA" width="235" height="85"></div><div class="name-track"><div class="name-sprockets" id="intro-sprk-l"><span></span><span></span><span></span></div><div class="name-stitch" id="intro-stitch"></div><div class="name-sprockets" id="intro-sprk-r"><span></span><span></span><span></span></div></div><p class="name-cap">ARCHIVO Nº 001 <i>&middot;</i> CARGANDO <b id="intro-pct">00</b>%</p><div class="name-stamp" id="intro-stamp"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M4 12l5 5L20 6"/></svg>AUTÉNTICO</div></div></div>'''
 else:
  intro=f'''<div class="intro-tag" id="intro-splash" aria-hidden="true"><div class="tag-wrap" id="intro-wrap"><div class="tag-string"></div><div class="tag-card" id="intro-card"><div class="tag-face tag-front"><b>DÉCADA</b><span></span><i>EST. 2004</i></div><div class="tag-face tag-back"><b>ARCHIVO Nº 001</b><i>PIEZA ÚNICA<br>SIN REPOSICIÓN</i></div></div></div></div>'''
 whatsapp_href=WHATSAPP_URL or prefix+'contacto/index.html#whatsapp'
 whatsapp_target=' target="_blank"' if WHATSAPP_URL else ''
 wa_float=f'''<div class="chat-widget" data-chat-widget><div class="chat-panel" role="dialog" aria-modal="false" aria-label="Asistente DÉCADA" data-chat-panel><header class="chat-head"><div class="chat-head-info"><span class="chat-status" aria-hidden="true"></span><div><strong>Asistente DÉCADA</strong><span>Respuestas al momento, sin esperas</span></div></div><button type="button" class="chat-close" data-chat-close aria-label="Cerrar chat">✕</button></header><div class="chat-body" data-chat-body aria-live="polite"></div><div class="chat-chips" data-chat-chips></div><form class="chat-input-row" data-chat-form><input type="text" placeholder="Escribe tu pregunta…" aria-label="Escribe tu pregunta" data-chat-input autocomplete="off" maxlength="200"><button type="submit" aria-label="Enviar pregunta"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button></form><a class="chat-human" href="{whatsapp_href}"{whatsapp_target} rel="noopener noreferrer">{svg('whatsapp')}<span>Hablar con una persona por WhatsApp</span></a></div><button type="button" class="chat-fab" data-chat-toggle aria-expanded="false" aria-controls="chat-panel" aria-label="Abrir chat de ayuda de DÉCADA">{svg('whatsapp')}<svg class="chat-fab-x" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg><span class="chat-fab-label">¿DUDAS? PREGÚNTANOS</span></button></div>'''
 return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#111114"><script>if('scrollRestoration' in history){{history.scrollRestoration='manual'}}window.scrollTo({{top:0,left:0,behavior:'instant'}});try{{if(!sessionStorage.getItem('decadaIntro')){{document.documentElement.classList.add('intro-run')}}}}catch(e){{}}</script><title>{escape(title)}</title><meta name="description" content="{escape(description,quote=True)}"><link rel="canonical" href="{canonical}"><link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="{prefix}assets/logo.webp"><meta property="og:type" content="{kind}"><meta property="og:site_name" content="DÉCADA"><meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{og_image or DOMAIN+'/assets/editorial-hero.webp'}"><meta property="og:image:alt" content="DÉCADA, vintage y streetwear seleccionado"><meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="{prefix}styles.css"><script type="application/ld+json">{json.dumps(site_data,ensure_ascii=False)}</script>{extra_head}</head><body>{intro}{header(prefix)}<main id="contenido">{body}</main>{footer(prefix)}{wa_float}<script src="{prefix}assets/search-index.js" defer></script><script src="{prefix}script.js" defer></script></body></html>'''

def write(path,html):
 file=ROOT/path;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(html,encoding='utf-8')

BRANDS=_brand_counts()
QUICK_CHIPS=''.join(f'<button type="button" class="quick" data-search-term="{t}">{t.upper()}</button>' for t in ('Sudaderas','Vaqueros','Camisetas','Chaquetas','Talla M','Talla L','Niños'))
BRAND_CHIPS=''.join(f'<button type="button" data-search-term="{escape(b)}">{escape(b.upper())} <span>{n}</span></button>' for b,n in BRANDS)
def _index_entry(q):
 v=variants(q['front']);thumb=v[0][0] if v else q['front']
 v2=variants(q['back']);thumb2=v2[0][0] if v2 else q['back']
 return {'slug':q['slug'],'name':q['name'],'brand':brand_for(q['name']) or '','kind':q['kind'],'gender':GENDER_LABELS.get(q.get('gender'),''),'size':q['size'],'sizeKey':size_key(q['size']),'price':q['price'],'img':'assets/'+thumb,'img2':'assets/'+thumb2}
_INDEX=json.dumps([_index_entry(q) for q in PRODUCTS],ensure_ascii=False)
(ROOT/'assets'/'search-index.json').write_text(_INDEX,encoding='utf-8')
(ROOT/'assets'/'search-index.js').write_text('window.DECADA_SEARCH='+_INDEX+';',encoding='utf-8')  # funciona también abriendo los HTML con doble clic
TICKER=''.join(f'<span>{t}</span><i>✦</i>' for t in ('ZERO TOLERANCE FOR FAKES','BUSCAMOS / TRAEMOS / CURAMOS','UNA PIEZA. UNA TALLA.','SOURCED IN UK. CURATED IN SPAIN.','SIN REPOSICIÓN'))
home=f'''<section class="hero entrance" aria-labelledby="hero-title"><div class="hero-image" data-hero-slideshow aria-label="Editorial DÉCADA"><img class="hero-slide is-active" src="assets/editorial-hero.webp" alt="Dos modelos con estilo vintage en una calle nocturna" width="1536" height="1024" fetchpriority="high"><img class="hero-slide" src="assets/editorial-hero-2.webp" alt="Dos modelos con prendas deportivas vintage junto a una calle mojada" width="1536" height="1024"><img class="hero-slide" src="assets/editorial-hero-3.webp" alt="Dos modelos con prendas vintage de deporte y vaqueros de los 90" width="1536" height="1024"><img class="hero-slide" src="assets/editorial-hero-4.webp" alt="Dos amigos caminando de espaldas con chaquetas vintage deportivas" width="1536" height="1024"><div class="hero-slide-controls" aria-label="Fotografías de portada"><button type="button" class="is-active" aria-label="Mostrar fotografía 1" aria-current="true"></button><button type="button" aria-label="Mostrar fotografía 2"></button><button type="button" aria-label="Mostrar fotografía 3"></button><button type="button" aria-label="Mostrar fotografía 4"></button></div><span class="image-id">DÉCADA / ARCHIVO VISUAL</span></div><div class="hero-copy"><p class="eyebrow">ARCHIVO VIVO · 90S / Y2K</p><h1 id="hero-title">EL PASADO<br>NO SE<br><em>REPITE.</em></h1><p>Vintage y streetwear seleccionado a mano. Una talla. Una unidad. Una oportunidad de hacerla tuya.</p><a class="button pink" href="#novedades">DESCUBRIR NOVEDADES <span>↗</span></a><span class="hero-foot">PIEZAS CON HISTORIA. LISTAS PARA OTRA.</span></div></section><div class="ticker" aria-hidden="true"><div class="ticker-track">{TICKER*2}</div></div><section class="section products-section" id="novedades"><div class="section-heading"><div><p class="eyebrow">SELECCIÓN ACTUAL / 001</p><h2>RECIÉN<br>LLEGADAS<span>.</span></h2><p>Descubre algunas de las piezas disponibles en nuestro catálogo. Cada una existe una sola vez.</p></div><a class="under-link" href="catalogo/index.html">VER TODO EL CATÁLOGO ↗</a></div>{spotlight(FEATURED)}<div class="home-rail">{rail_section('<h3 class="rail-title">MÁS EN EL ARCHIVO</h3>','<a class="under-link" href="catalogo/index.html">VER TODO ↗</a>',''.join(card(p) for p in [p for p in PRODUCTS if p is not FEATURED][:10]),'aria-label="Más piezas del archivo"','piezas del archivo')}</div></section>{brand_row()}{categories()}{brand_block()}{drop_block()}'''
write('index.html',shell('index.html','DÉCADA | Ropa vintage y streetwear 90s y Y2K','Descubre ropa vintage y streetwear de los 90 y 2000 seleccionada a mano por DÉCADA. Piezas únicas, sin reposición.',home))

catalog=f'''<section class="catalog-triptych" aria-label="Explorar el catálogo por sección"><h1 class="visually-hidden">Catálogo de ropa vintage DÉCADA: hombre, mujer y niños</h1><a class="catalog-tile catalog-tile-men" href="hombre/index.html"><img src="../assets/category-hombre.webp" alt="Modelo con chaqueta vintage en una calle nocturna" width="1698" height="926"><span class="catalog-tile-content"><strong>HOMBRE</strong><span>EXPLORAR PRENDAS <span aria-hidden="true">↗</span></span></span></a><a class="catalog-tile catalog-tile-women" href="mujer/index.html"><img src="../assets/category-mujer.webp" alt="Modelo con ropa deportiva vintage en una calle nocturna" width="1697" height="927"><span class="catalog-tile-content"><strong>MUJER</strong><span>EXPLORAR PRENDAS <span aria-hidden="true">↗</span></span></span></a><a class="catalog-tile catalog-tile-kids" href="ninos/index.html"><img src="../assets/category-ninos.webp" alt="Modelo infantil con chaqueta deportiva vintage en la ciudad" width="1536" height="1024"><span class="catalog-tile-content"><strong>NIÑOS</strong><span>EXPLORAR PRENDAS <span aria-hidden="true">↗</span></span></span></a></section>'''
write('catalogo/index.html',shell('catalogo/index.html','Catálogo de ropa vintage y streetwear | DÉCADA','Explora la selección de prendas vintage y streetwear de DÉCADA. Vaqueros y camisetas originales, cada pieza con una sola unidad.',catalog))

for gender,photo,copy in [('hombre','category-hombre.webp','Streetwear y vintage con carácter. Prendas escogidas para seguir en la calle.'),('mujer','category-mujer.webp','Una selección con historia, estilo propio y una sola oportunidad por pieza.'),('ninos','category-ninos.webp','Piezas vintage para los más pequeños. Una talla y una unidad por prenda.')]:
 label=GENDER_LABELS[gender]
 group=CATALOG[gender]
 chips=[f'<a href="#prendas" data-filter="all" class="is-active" aria-pressed="true">TODO <span>{len(group)}</span></a>']
 sections=[]
 for kind in GROUP_LABELS:
  members=[p for p in group if group_of(p)==kind]
  if not members:continue
  group_id=GROUP_SLUGS[kind]
  sections.append(rail_section(f'<h2 id="t-{group_id}">{GROUP_LABELS[kind]}<span>.</span></h2><span class="type-count">{pieces_label(len(members))}</span>',f'<a class="under-link" href="{group_id}/index.html">VER SECCIÓN ↗</a>',"".join(card(p,"../../") for p in members),f'data-group-section="{group_id}" aria-labelledby="t-{group_id}"',f'{GROUP_LABELS[kind].lower()}'))
  chips.append(f'<a href="{group_id}/index.html" data-filter="{group_id}" aria-pressed="false">{GROUP_LABELS[kind]} <span>{len(members)}</span></a>')
  collection_path=f'catalogo/{gender}/{group_id}/index.html'
  members_sizes=sorted({size_key(p['size']) for p in members},key=size_sort)
  member_size_chips=''.join(f'<button type="button" data-size-filter="{escape(z)}" aria-pressed="false">{escape(z)}</button>' for z in members_sizes)
  member_price_chips=''.join(f'<button type="button" data-price-filter="{key}" aria-pressed="false">{lbl}</button>' for key,lbl in PRICE_BANDS)
  collection_body=f'''<section class="collection-page-hero"><img src="../../../assets/{photo}" alt="" width="1698" height="926"><div><div class="crumb"><a href="../../../index.html">INICIO</a> / <a href="../../index.html">CATÁLOGO</a> / <a href="../index.html">{label}</a> / {GROUP_LABELS[kind]}</div><p class="eyebrow">DÉCADA / {label}</p><h1>{GROUP_LABELS[kind]}<span>.</span></h1><p>{len(members)} {'pieza única disponible' if len(members)==1 else 'piezas únicas disponibles'}. Consulta fotografías, talla, estado y medidas en cada ficha.</p></div></section><section class="section collection-listing"><div class="collection-toolbar"><label>BUSCAR<input type="search" placeholder="Marca o prenda" autocomplete="off" data-collection-search></label><label>ORDENAR<select data-collection-sort><option value="featured" data-short="Destacadas">Destacadas</option><option value="low" data-short="Precio ↑">Precio: menor a mayor</option><option value="high" data-short="Precio ↓">Precio: mayor a menor</option></select></label><span data-collection-count>{len(members)} {'pieza' if len(members)==1 else 'piezas'}</span></div><div class="collection-filters"><div class="size-chips" role="group" aria-label="Filtrar por talla">{f'<span>TALLA</span>{member_size_chips}' if len(members_sizes)>1 else ''}</div><div class="price-chips" role="group" aria-label="Filtrar por precio"><span>PRECIO</span>{member_price_chips}</div></div><div class="catalog-grid collection-full-grid" data-collection-grid>{''.join(card(p,'../../../') for p in members)}</div><div class="empty-state" data-collection-empty hidden>No hemos encontrado ninguna pieza con ese nombre.</div></section><section class="category-other"><a href="../index.html">← TODO {label}</a><a href="../../index.html">EXPLORAR OTRAS SECCIONES ↗</a></section>'''
  write(collection_path,shell(collection_path,f'{GROUP_LABELS[kind].title()} vintage de {label.lower()} | DÉCADA',f'Explora {len(members)} prendas de {GROUP_LABELS[kind].lower()} vintage de {label.lower()} en DÉCADA. Piezas únicas con fotos, tallas, medidas y precios.',collection_body))
 sizes=sorted({size_key(p['size']) for p in group},key=size_sort)
 size_chips=''.join(f'<button type="button" data-size-filter="{escape(z)}" aria-pressed="false">{escape(z)}</button>' for z in sizes)
 price_chips=''.join(f'<button type="button" data-price-filter="{key}" aria-pressed="false">{lbl}</button>' for key,lbl in PRICE_BANDS)
 filters=f'''<div class="filter-bar" id="prendas"><nav class="filter-chips" aria-label="Filtrar {label.lower()} por tipo de prenda">{''.join(chips)}</nav><div class="size-chips" role="group" aria-label="Filtrar por talla"><span>TALLA</span>{size_chips}</div><div class="price-chips" role="group" aria-label="Filtrar por precio"><span>PRECIO</span>{price_chips}</div><label class="filter-sort">ORDENAR<select data-gender-sort aria-label="Ordenar prendas"><option value="featured" data-short="Destacadas">Destacadas</option><option value="low" data-short="Precio ↑">Precio: menor a mayor</option><option value="high" data-short="Precio ↓">Precio: mayor a menor</option></select></label></div>'''
 body=f'''<section class="category-page-hero {gender}-hero"><img src="../../assets/{photo}" alt="" width="1698" height="926"><div><div class="crumb"><a href="../../index.html">INICIO</a> / <a href="../index.html">CATÁLOGO</a> / {label}</div><p class="eyebrow">DÉCADA / EXPLORA</p><h1>{label}<span>.</span></h1><p>{copy}</p><a class="button pink" href="#prendas">VER {pieces_label(len(group))} <span>↓</span></a></div></section>{filters}<section class="section gender-listing" data-gender-listing><p class="gender-count" data-gender-count aria-live="polite">{pieces_label(len(group))} ÚNICAS</p><div class="empty-state" data-gender-empty hidden>No hay piezas con esa combinación. <button type="button" data-clear-filters>Quitar filtros</button></div>{''.join(sections)}</section><section class="category-other"><span>EL ARCHIVO CONTINÚA</span><a href="../index.html">EXPLORAR OTRAS SECCIONES ↗</a></section>'''
 write(f'catalogo/{gender}/index.html',shell(f'catalogo/{gender}/index.html',f'Ropa vintage de {label.lower()} | DÉCADA',f'Explora {len(group)} prendas vintage y streetwear de {label.lower()} de DÉCADA. Piezas únicas con fotos, tallas y precios.',body))

for p in PRODUCTS:
 name=escape(p['name']);slug=p['slug']
 measurements=p.get('measurements') or {}
 def _cm(value):
  m=re.match(r'([\d.,]+)',value)
  return m.group(1).replace(',','.') if m else ''
 measure_rows=''.join(f'<div class="measure-row" data-measure-row data-cm="{_cm(value)}"><dt>{escape(label.title())}</dt><dd>{escape(value)}</dd><label class="measure-compare"><span>Tu prenda</span><input type="number" inputmode="decimal" step="0.5" min="0" max="200" placeholder="cm" data-measure-input aria-label="Tu medida de {escape(label.title())} en centímetros"></label><span class="measure-diff" data-measure-diff aria-live="polite"></span></div>' for label,value in measurements.items())
 measures=f'''<section class="measure-panel"><div class="measure-title"><p class="eyebrow">TALLA REAL / EN CM</p><h2>MEDIDAS DE LA PRENDA</h2></div><p>Medidas tomadas de esta pieza física. Escribe la medida equivalente de una prenda tuya y compárala al momento. <a class="measure-how" href="../../como-comprar/index.html#como-medimos">Así medimos ↗</a> · <a class="measure-how" href="../../guia-tallas/index.html">Guía de tallas ↗</a></p><dl>{measure_rows}</dl></section>''' if measurements else f'''<section class="measure-panel"><div class="measure-title"><p class="eyebrow">TALLA REAL / EN CM</p><h2>MEDIDAS DE LA PRENDA</h2></div><p>Las medidas de esta pieza figuran en las fotografías de la ficha original. <a href="{DOMAIN}/productos/{slug}" target="_blank" rel="noopener noreferrer">Consultar ficha ↗</a> · <a href="../../guia-tallas/index.html">Guía de tallas ↗</a></p></section>'''
 condition_text=p.get('condition') or 'Estado por confirmar'
 condition_cls='' if p.get('condition') else ' pending'
 condition=f'<span class="detail-condition{condition_cls}">{escape(condition_text)}</span>'
 photo_list=p.get('photos') or [p['front']]
 def srcset_of(v):
  vv=variants(v);return ', '.join(f"{photo_url(r,'../../')} {w}w" for r,w in vv) if len(vv)>1 else ''
 gallery_photos=[(photo_url(v,'../../'),f'{name}, fotografía {i+1} de {len(photo_list)}',f'{i+1:02d}',srcset_of(v)) for i,v in enumerate(photo_list)]
 gallery_thumbs=''.join(f'<button type="button" class="product-thumb{" is-active" if i==0 else ""}" data-gallery-src="{src}" data-gallery-srcset="{ss}" data-gallery-alt="{alt}" aria-label="Mostrar fotografía {i+1}" aria-pressed="{"true" if i==0 else "false"}"><img {img_attrs(photo_list[i],"../../","90px")} alt="" width="90" height="90" loading="lazy"><span>{number}</span></button>' for i,(src,alt,number,ss) in enumerate(gallery_photos))
 first_src,first_alt,_,first_ss=gallery_photos[0]
 images=f'''<div class="product-gallery" data-product-gallery><button type="button" class="product-gallery-stage" aria-label="Ampliar fotografía de la prenda"><img src="{first_src}" {f'srcset="{first_ss}" sizes="(max-width:700px) 100vw, 52vw"' if first_ss else ''} alt="{first_alt}" width="900" height="900" data-gallery-main><span class="gallery-zoom">AMPLIAR ↗</span></button><div class="product-thumbs" aria-label="Fotografías de la prenda">{gallery_thumbs}</div><dialog class="product-lightbox" aria-label="Fotografías de {name}"><div class="lb-top"><div class="lb-title"><span class="eyebrow">DÉCADA / PIEZA ÚNICA</span><strong>{name}</strong></div><span class="gallery-count" aria-live="polite"></span><button type="button" class="lightbox-close" aria-label="Cerrar fotografías"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div><div class="lb-stage"><img src="{first_src}" alt="{first_alt}" data-lightbox-image><p class="lb-hint">Pulsa la foto para ampliar el detalle</p></div><div class="lb-thumbs" data-lb-thumbs></div></dialog></div>'''
 siblings=[q for q in PRODUCTS if q['slug']!=slug and q.get('gender')==p.get('gender')][:4]
 if len(siblings)<4:siblings+= [q for q in PRODUCTS if q['slug']!=slug and q not in siblings][:4-len(siblings)]
 g=p.get('gender');gk=group_of(p)
 crumb_mid=f'<a href="../../catalogo/{g}/index.html">{GENDER_LABELS[g]}</a> / <a href="../../catalogo/{g}/{GROUP_SLUGS[gk]}/index.html">{GROUP_LABELS[gk]}</a>' if g else '<a href="../../catalogo/index.html">CATÁLOGO</a>'
 pager_pool=[q for q in PRODUCTS if q.get('gender')==p.get('gender')] or PRODUCTS
 p_idx=pager_pool.index(p)
 prev_p=pager_pool[p_idx-1] if p_idx>0 else pager_pool[-1]
 next_p=pager_pool[(p_idx+1)%len(pager_pool)]
 pager=f'''<nav class="product-pager" aria-label="Recorrer el archivo"><a href="../{prev_p['slug']}/index.html" class="pager-prev">{ARROW_L}<span><small>ANTERIOR</small><strong>{escape(prev_p['name'])}</strong></span></a><a href="../../catalogo/index.html" class="pager-all">ARCHIVO Nº{p['archno']}<em>TODO EL CATÁLOGO</em></a><a href="../{next_p['slug']}/index.html" class="pager-next"><span><small>SIGUIENTE</small><strong>{escape(next_p['name'])}</strong></span>{ARROW_R}</a></nav>'''
 detail=f'''<div class="crumb product-crumb"><a href="../../index.html">INICIO</a> / {crumb_mid} / <span aria-current="page">{name.upper()}</span></div><section class="detail-layout"><div class="detail-photos">{images}<div class="auth-seal"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M4 12l5 5L20 6"/></svg><span>AUTENTICIDAD<br>VERIFICADA</span></div></div><div class="detail-panel"><p class="eyebrow">DÉCADA / ARCHIVO Nº{p['archno']}</p><h1>{name}</h1><div class="detail-status">{condition}<span>TALLA {escape(p['size'])}</span><span class="last-badge-inline">ÚLTIMA UNIDAD</span></div><p class="detail-price">{p['price']}</p><p class="detail-description">{escape(product_copy(p))}</p>{measures}<div class="detail-actions"><button class="button pink add-preview" type="button" data-sku="{slug}" data-name="{name}" data-price="{p['price']}" data-image="{photo_url(p['front'],'../../')}" data-link="{DOMAIN}/productos/{slug}">AÑADIR A MI BOLSA <span>＋</span></button><a class="button outline detail-buy" href="{DOMAIN}/productos/{slug}" target="_blank" rel="noopener noreferrer">COMPRAR ESTA PIEZA <span>↗</span></a><a class="under-link detail-bag-link" href="../../carrito/index.html" hidden>VER MI BOLSA ↗</a></div><ul class="detail-trust"><li><span>01</span><p><strong>Pieza única.</strong> Una talla, una unidad. Sin reposición.</p></li><li><span>02</span><p><strong>Autenticidad.</strong> ¿Quieres ver etiquetas o detalles? <a href="../../contacto/index.html?motivo=fotos&amp;pieza={quote(p['name'])}#formulario">Pídenos fotos ↗</a></p></li><li><span>03</span><p><strong>Ajuste.</strong> Compara las medidas con una prenda tuya. <a href="../../contacto/index.html?motivo=tallas&amp;pieza={quote(p['name'])}#formulario">¿Dudas? Escríbenos ↗</a></p></li></ul><p class="detail-note"><a href="../../como-comprar/index.html">Consulta cómo comprar, envíos y devoluciones ↗</a></p></div></section><div class="buy-bar" data-buy-bar aria-hidden="true"><div><strong>{name}</strong><span>{p['price']} · TALLA {escape(p['size'])}</span></div><button class="button pink buy-bar-add" type="button" data-proxy-add tabindex="-1">AÑADIR <span>＋</span></button></div>{pager}<section class="section related"><div class="section-heading"><div><p class="eyebrow">SIGUE EXPLORANDO</p><h2>OTRAS PIEZAS<span>.</span></h2></div><a class="under-link" href="../../catalogo/index.html">VER CATÁLOGO ↗</a></div><div class="catalog-grid">{''.join(card(q,'../../') for q in siblings)}</div></section>'''
 product_data={'@context':'https://schema.org','@type':'Product','name':p['name'],'sku':slug,'size':p['size'],'image':list(dict.fromkeys([DOMAIN+'/assets/'+p['front'],DOMAIN+'/assets/'+p['back']])),'description':product_copy(p),'itemCondition':'https://schema.org/UsedCondition','offers':{'@type':'Offer','url':DOMAIN+'/productos/'+slug,'priceCurrency':'EUR','price':p['amount'],'availability':'https://schema.org/InStock','itemCondition':'https://schema.org/UsedCondition'}}
 if brand_for(p['name']):product_data['brand']={'@type':'Brand','name':brand_for(p['name'])}
 product_ld='<script type="application/ld+json">'+json.dumps(product_data,ensure_ascii=False)+'</script>'
 write(f'productos/{slug}/index.html',shell(f'productos/{slug}/index.html',f'{p["name"]} · Talla {p["size"]} | DÉCADA',f'Descubre {p["name"]}, talla {p["size"]}, en la selección de ropa vintage DÉCADA. Consulta medidas y disponibilidad de esta pieza única.',detail,kind='product',extra_head=product_ld,og_image=DOMAIN+'/assets/'+p['front']))

brand=f'''<section class="page-hero brand-page"><img src="../assets/editorial-hero-2.webp" alt="Editorial nocturna de DÉCADA, dos modelos con chándal vintage" width="1536" height="1024"><div class="page-hero-copy"><div class="crumb"><a href="../index.html">INICIO</a> / LA MARCA</div><p class="eyebrow">DÉCADA / EST. 2004</p><h1>ROPA CON<br>OTRA VIDA<span>.</span></h1><p>No buscamos llenar percheros. Buscamos piezas que merecen seguir contando historias.</p></div></section><section class="section story-grid"><img src="../assets/editorial-hero.webp" alt="Editorial nocturna de DÉCADA" width="1536" height="1024"><div><p class="eyebrow">NUESTRA FORMA DE VERLO</p><h2>BUSCAMOS.<br>TRAEMOS.<br><em>CURAMOS.</em></h2><p>Nos atraen las prendas originales de los 90 y los 2000: su corte, los detalles y lo que transmiten al volver a la calle. Cada pieza pasa por una selección individual.</p><p>Una talla, una unidad. Si encuentras la tuya, no habrá otra igual esperando en el almacén.</p><a class="under-link" href="../catalogo/index.html">DESCUBRIR LAS PIEZAS ↗</a></div></section><div class="values"><div><span>01</span><h3>SELECCIÓN</h3><p>Escogemos las prendas una a una.</p></div><div><span>02</span><h3>AUTENTICIDAD</h3><p>Una pieza cuya autenticidad genere dudas no encaja en DÉCADA. Si quieres revisar etiquetas o detalles concretos, pídenos fotos antes de comprar.</p></div><div><span>03</span><h3>OTRA HISTORIA</h3><p>Ropa del pasado hecha para llevar hoy.</p></div></div><section class="brand-quote"><img src="../assets/editorial-hero-3.webp" alt="Modelos con prendas vintage de deporte y vaqueros de los 90" width="1536" height="1024"><blockquote><p>&laquo;Cada prenda que entra al archivo ya tuvo una vida. Nuestro trabajo es encontrarle la siguiente.&raquo;</p><cite>DÉCADA, EST. 2004</cite></blockquote></section><section class="section manifesto"><p class="eyebrow">LA IDEA DETRÁS DE DÉCADA</p><h2>LO BUENO NO CADUCA<span>.</span></h2><div><p>Elegimos ropa que todavía tiene camino por delante: piezas con identidad, detalles que merecen una segunda mirada y estilos que no necesitan seguir una temporada.</p><p>La web reúne el archivo disponible durante todo el año. Las novedades llegan de las últimas piezas publicadas; después siguen en el catálogo hasta encontrar a quien las lleve.</p></div><a class="button pink" href="../catalogo/index.html">EXPLORAR EL ARCHIVO <span>↗</span></a></section>'''
write('marca/index.html',shell('marca/index.html','Sobre DÉCADA | Vintage seleccionado a mano','Conoce DÉCADA: buscamos, traemos y curamos piezas vintage y streetwear de los 90 y 2000 con cero tolerancia a las falsificaciones.',brand))

buy=f'''<section class="page-hero compact photo-hero"><img src="../assets/editorial-detail.webp" alt="Revisando la etiqueta original de una prenda vintage" width="1536" height="1024"><div class="page-hero-copy"><div class="crumb"><a href="../index.html">INICIO</a> / CÓMO COMPRAR</div><p class="eyebrow">PIEZAS ÚNICAS / COMPRA CLARA</p><h1>ASÍ<br>FUNCIONA<span>.</span></h1><p>Consulta la prenda, comprueba su disponibilidad y decide con toda la información antes de pagar.</p></div></section><section class="section buying-steps"><div><span>01 / EXPLORA</span><h2>ENCUENTRA TU PIEZA</h2><p>Filtra el catálogo por tipo de prenda y abre la ficha para ver sus fotografías y la talla indicada.</p></div><div><span>02 / COMPRUEBA</span><h2>RESUELVE LAS DUDAS</h2><p>La talla de etiqueta puede no reflejar el ajuste real de una prenda vintage. Consulta las medidas y el estado en la ficha actual; si falta algún dato, escríbenos antes de comprar.</p></div><div><span>03 / COMPRA</span><h2>REVISA EL TOTAL</h2><p>Añade la pieza a la bolsa y revisa el precio final, el envío y las condiciones antes de completar el pago.</p></div><div><span>04 / DESPUÉS</span><h2>TE AYUDAMOS</h2><p>Para dudas sobre el pedido, envío o devoluciones, contacta con DÉCADA. Revisa las condiciones vigentes en la tienda donde completes la compra.</p></div></section><section class="section faq" id="preguntas" aria-labelledby="faq-title"><div class="faq-head"><p class="eyebrow">PREGUNTAS FRECUENTES</p><h2 id="faq-title">ANTES DE COMPRAR<span>.</span></h2></div><div class="faq-list"><details id="como-medimos" open><summary>¿Cómo medimos las prendas?</summary><div class="faq-body"><p>Con la prenda estirada en plano y sin tensar la tela:</p><ul><li><strong>Pecho:</strong> de axila a axila, por delante.</li><li><strong>Hombros:</strong> de costura a costura por la parte de arriba.</li><li><strong>Largo:</strong> desde el punto más alto del hombro hasta el bajo.</li><li><strong>Cintura (pantalones):</strong> de lado a lado de la cinturilla, abrochada.</li><li><strong>Entrepierna:</strong> desde la costura central hasta el bajo.</li></ul><p>Compara estas medidas con una prenda tuya que te quede bien: es la forma más fiable de acertar con la talla en vintage.</p></div></details><details><summary>¿Qué significa cada estado?</summary><div class="faq-body"><ul><li><strong>Excelente estado:</strong> sin marcas de uso visibles.</li><li><strong>Muy buen estado:</strong> uso ligero, sin defectos que afecten a la prenda.</li><li><strong>Buen estado:</strong> señales de uso o pequeños detalles, siempre indicados y fotografiados en la ficha.</li></ul></div></details><details><summary>¿Cómo sé que es original?</summary><div class="faq-body"><p>Revisamos etiquetas, costuras y detalles de cada pieza antes de publicarla. Si una prenda genera dudas sobre su autenticidad, no entra en DÉCADA. Si quieres ver una etiqueta o un detalle concreto, <a href="../contacto/index.html?motivo=fotos#formulario">pídenos fotos</a> antes de comprar.</p></div></details><details><summary>¿Añadir a la bolsa reserva la pieza?</summary><div class="faq-body"><p>No. Cada prenda existe una sola vez y se la lleva quien completa primero la compra.</p></div></details><details><summary>¿Vendéis también en Vinted?</summary><div class="faq-body"><p>Sí. Parte del archivo también está en nuestro perfil de Vinted. Si tienes dudas sobre una pieza concreta, escríbenos.</p></div></details></div></section><section class="section buying-cta"><p class="eyebrow">¿HAY ALGO QUE QUIERES SABER?</p><h2>HABLEMOS<span>.</span></h2><a class="button pink" href="../contacto/index.html">CONTACTAR <span>↗</span></a></section>'''
write('como-comprar/index.html',shell('como-comprar/index.html','Cómo comprar ropa vintage | DÉCADA','Cómo elegir una prenda vintage de DÉCADA: fotos, tallas, medidas y compra en la tienda actual.',buy))

contact=f'''<section class="page-hero compact photo-hero"><img src="../assets/editorial-contact.webp" alt="Persona sonriendo mientras escribe un mensaje desde el móvil en una calle nocturna" width="1536" height="1024"><div class="page-hero-copy"><div class="crumb"><a href="../index.html">INICIO</a> / CONTACTO</div><p class="eyebrow">HABLEMOS</p><h1>ESTAMOS<br>AQUÍ<span>.</span></h1><p>¿Tienes una duda sobre una prenda, su talla o su estado? Escríbenos y te respondemos por email.</p></div></section><section class="section contact-layout" id="formulario"><form class="contact-form" action="{FORM_ENDPOINT}" method="POST" data-contact-form novalidate><div class="form-head"><p class="eyebrow">FORMULARIO / RESPUESTA POR EMAIL</p><h2>ESCRÍBENOS<span>.</span></h2></div><input type="hidden" name="_subject" value="Nueva consulta desde decada.store"><input type="hidden" name="_template" value="table"><input type="hidden" name="_captcha" value="false"><input type="hidden" name="_next" value="{DOMAIN}/contacto/?enviado=1"><input type="hidden" name="Página de origen" data-origin value=""><div class="form-honey" aria-hidden="true"><label>No rellenar<input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div><div class="form-row"><label class="field"><span>Nombre *</span><input type="text" name="Nombre" autocomplete="name" required maxlength="80"></label><label class="field"><span>Email *</span><input type="email" name="email" autocomplete="email" required maxlength="120"></label></div><div class="form-row"><label class="field"><span>Motivo</span><select name="Motivo" data-field-motivo><option value="Tallas y medidas" data-key="tallas">Tallas y medidas</option><option value="Estado o fotos de una prenda" data-key="fotos">Estado o fotos de una prenda</option><option value="Un pedido o envío" data-key="pedido">Un pedido o envío</option><option value="Colaboraciones" data-key="colab">Colaboraciones</option><option value="Otra consulta" data-key="otra">Otra consulta</option></select></label><label class="field"><span>Prenda (opcional)</span><input type="text" name="Prenda" data-field-prenda placeholder="Ej.: Chaleco Nike Air negro" maxlength="300"></label></div><label class="field"><span>Mensaje *</span><textarea name="Mensaje" rows="6" required minlength="10" maxlength="2000" placeholder="Cuéntanos qué necesitas saber."></textarea></label><label class="check"><input type="checkbox" name="Acepta privacidad" value="Sí" required><span>He leído y acepto la <a href="{DOMAIN}/politica-privacidad" target="_blank" rel="noopener noreferrer">política de privacidad</a>. Usaremos tus datos solo para responder a esta consulta.</span></label><div class="form-foot"><button class="button pink" type="submit">ENVIAR CONSULTA <span>↗</span></button><p class="form-note">Te respondemos desde <strong>{CONTACT_EMAIL}</strong>.</p></div><p class="form-status" data-form-status role="status" hidden></p></form><aside class="contact-grid contact-channels" aria-label="Otros canales"><a href="{IG}" target="_blank" rel="noopener noreferrer"><span>01 / REDES</span><h2>INSTAGRAM ↗</h2><p>@decada.store</p></a><div class="contact-channel" id="vinted"><span>02 / REVENTA</span><h2>VINTED</h2><p class="contact-channel-links">{''.join(f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label} ↗</a>' for label,url in VINTED_ACCOUNTS)}</p></div><a id="whatsapp" href="{WHATSAPP_URL or '#whatsapp'}"{' target="_blank" rel="noopener noreferrer"' if WHATSAPP_URL else ''}><span>03 / MENSAJERÍA</span><h2>WHATSAPP</h2><p>{WHATSAPP_DISPLAY if WHATSAPP_URL else 'Número oficial pendiente de configurar'}</p></a><a href="mailto:{CONTACT_EMAIL}"><span>04 / EMAIL</span><h2>EMAIL ↗</h2><p>{CONTACT_EMAIL}</p></a></aside></section>'''
write('contacto/index.html',shell('contacto/index.html','Contacto DÉCADA | Dudas sobre prendas vintage','Contacta con DÉCADA para resolver dudas sobre prendas, tallas, medidas y pedidos. Estamos en Instagram, Vinted, WhatsApp y email.',contact))

size_guide_rows={
 'Camisetas y polos':[('XS','44-46','34-36','3'),('S','46-48','36-38','4'),('M','48-50','38-40','6'),('L','50-53','40-42','8'),('XL','53-56','42-44','10'),('XXL','56-60','44-46','12')],
 'Pantalones':[('XS / 36','66-70','25-27','4'),('S / 38','70-74','27-29','6'),('M / 40','74-78','29-31','8'),('L / 42','78-84','31-33','10'),('XL / 44','84-90','33-35','12'),('XXL / 46','90-96','35-37','14')]
}
def _size_table(rows,headers):
 head=''.join(f'<th>{h}</th>' for h in headers)
 body_rows=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in row)+'</tr>' for row in rows)
 return f'<table class="size-table"><thead><tr>{head}</tr></thead><tbody>{body_rows}</tbody></table>'
guide=f'''<section class="page-hero compact"><div class="crumb"><a href="../index.html">INICIO</a> / GUÍA DE TALLAS</div><p class="eyebrow">TALLAJE VINTAGE / SIN SORPRESAS</p><h1>ENCUENTRA<br>TU TALLA<span>.</span></h1><p>El tallaje vintage rara vez coincide con el actual. Usa estas tablas de referencia y, sobre todo, compara siempre con las medidas reales de cada pieza en su ficha.</p></section><section class="section guide-block"><div class="guide-head"><p class="eyebrow">01 / LO MÁS IMPORTANTE</p><h2>LA ETIQUETA NO MANDA<span>.</span></h2></div><p>Una "M" de los 90 puede quedar como una "S" actual, o al revés según la marca y la década. Por eso cada ficha de producto incluye las medidas reales tomadas a mano (pecho, hombros, cintura, largo) y un comparador para que introduzcas la medida de una prenda tuya y veas al momento si se ajusta.</p></section><section class="section guide-block"><div class="guide-head"><p class="eyebrow">02 / CAMISETAS, POLOS, SUDADERAS Y JERSÉIS</p><h2>REFERENCIA EN CM<span>.</span></h2></div><p>Medida de pecho tomada de axila a axila (multiplicar x2 para el contorno completo).</p>{_size_table(size_guide_rows['Camisetas y polos'],('TALLA','PECHO','HOMBROS','EDAD NIÑOS'))}</section><section class="section guide-block"><div class="guide-head"><p class="eyebrow">03 / VAQUEROS Y PANTALONES</p><h2>REFERENCIA EN CM<span>.</span></h2></div><p>Cintura tomada de lado a lado con la prenda abrochada (multiplicar x2 para el contorno completo).</p>{_size_table(size_guide_rows['Pantalones'],('TALLA','CINTURA','ENTREPIERNA','EDAD NIÑOS'))}</section><section class="section guide-block"><div class="guide-head"><p class="eyebrow">04 / CÓMO MEDIRTE</p><h2>CON UNA PRENDA TUYA<span>.</span></h2></div><ol class="guide-steps"><li><strong>Elige</strong> una prenda que ya tengas y que te quede como te gusta.</li><li><strong>Estírala</strong> en plano, sin tensar la tela.</li><li><strong>Mide</strong> pecho, hombros, cintura o largo según el tipo de prenda. <a href="../como-comprar/index.html#como-medimos">Instrucciones detalladas ↗</a></li><li><strong>Compara</strong> el resultado con las medidas reales de la ficha, o usa el comparador integrado.</li></ol></section><section class="section buying-cta"><p class="eyebrow">¿AÚN TIENES DUDAS?</p><h2>PREGÚNTANOS<span>.</span></h2><a class="button pink" href="../contacto/index.html?motivo=tallas#formulario">CONSULTAR UNA TALLA <span>↗</span></a></section>'''
write('guia-tallas/index.html',shell('guia-tallas/index.html','Guía de tallas vintage | DÉCADA','Tablas de referencia de tallas vintage y cómo medirte con una prenda propia para acertar al comprar en DÉCADA.',guide))

not_found=f'''<section class="page-hero compact not-found-hero"><div class="crumb"><a href="index.html">INICIO</a> / 404</div><p class="eyebrow">ARCHIVO Nº 404</p><h1>ESTA PIEZA<br>NO ESTÁ<span>.</span></h1><p>El enlace que has seguido no existe o esa prenda ya encontró a quien se la llevó. Cada pieza es única: puede que ya no esté disponible.</p><div class="not-found-actions"><a class="button pink" href="catalogo/index.html">EXPLORAR EL CATÁLOGO <span>↗</span></a><a class="under-link" href="index.html">VOLVER AL INICIO ↗</a></div></section>'''
write('404.html',shell('404.html','Página no encontrada | DÉCADA','La página que buscas no existe o ya no está disponible en DÉCADA.',not_found))

cart=f'''<section class="page-hero compact"><div class="crumb"><a href="../index.html">INICIO</a> / TU BOLSA</div><p class="eyebrow">TU SELECCIÓN</p><h1>MI BOLSA<span>.</span></h1><p>Guarda las piezas que te interesan mientras exploras DÉCADA.</p></section><section class="section bag-page"><div id="bag-items" aria-live="polite"></div><div id="bag-empty"><p>Tu bolsa está vacía. El archivo te espera.</p><a class="button pink" href="../catalogo/index.html">EXPLORAR PRENDAS <span>↗</span></a></div><aside class="bag-summary"><p>TU SELECCIÓN</p><h2>PIEZAS ÚNICAS,<br>DECISIONES RÁPIDAS.</h2><p>Comprueba la disponibilidad al abrir cada pieza y completa la compra en la tienda de DÉCADA.</p></aside></section>'''
write('carrito/index.html',shell('carrito/index.html','Tu bolsa | DÉCADA','Revisa las piezas vintage que te interesan en DÉCADA y consulta su disponibilidad en la tienda actual.',cart))

category_pages=[f'catalogo/{g}/{GROUP_SLUGS[k]}/index.html' for g in ('hombre','mujer','ninos') for k in GROUP_LABELS if any(group_of(p)==k for p in CATALOG[g])]
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{DOMAIN}{"/" if path=="index.html" else "/"+path.removesuffix("index.html")}</loc></url>\n' for path in ['index.html','catalogo/index.html','catalogo/hombre/index.html','catalogo/mujer/index.html','catalogo/ninos/index.html','como-comprar/index.html','marca/index.html','contacto/index.html','guia-tallas/index.html']+category_pages+[f'productos/{p["slug"]}/index.html' for p in PRODUCTS])+'</urlset>\n')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /carrito/\nSitemap: https://decada.store/sitemap.xml\n')
print(f'Generated {len(PRODUCTS)+11+len(category_pages)} HTML pages')
