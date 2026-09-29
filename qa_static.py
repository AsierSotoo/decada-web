"""Repeatable, dependency-free checks. These do NOT replace browser QA."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = []
        self.h1 = 0
        self.ld = []
        self.reading_ld = False
    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == 'h1': self.h1 += 1
        if 'id' in data: self.ids.append(data['id'])
        for attr in ('src','href'):
            if data.get(attr): self.links.append(data[attr])
        if tag == 'script' and data.get('type') == 'application/ld+json':
            self.reading_ld = True
            self.ld.append('')
    def handle_endtag(self, tag):
        if tag == 'script': self.reading_ld = False
    def handle_data(self, data):
        if self.reading_ld: self.ld[-1] += data

pages = {}
errors = []
for path in ROOT.rglob('*.html'):
    parser = Page()
    source = path.read_text(encoding='utf-8')
    parser.feed(source)
    pages[path.resolve()] = parser
    if parser.h1 != 1: errors.append(f'{path}: {parser.h1} H1s')
    if len(set(parser.ids)) != len(parser.ids): errors.append(f'{path}: duplicate IDs')
    for ld in parser.ld:
        try: json.loads(ld)
        except ValueError: errors.append(f'{path}: invalid JSON-LD')
    if 'productos' in path.parts:
        if source.index('class="detail-actions"') > source.index('class="measure-panel"'): errors.append(f'{path}: CTA after measurements')
        if 'class="button outline detail-buy"' in source: errors.append(f'{path}: looping purchase CTA')
for path, parser in pages.items():
    for link in parser.links:
        parts = urlsplit(link)
        if parts.scheme or parts.netloc: continue
        target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
        if target.is_dir(): target = target / 'index.html'
        if not target.is_file(): errors.append(f'{path.relative_to(ROOT)}: missing {link}')
        elif target.stat().st_size == 0: errors.append(f'{path.relative_to(ROOT)}: empty {link}')
        elif parts.fragment and target in pages and parts.fragment not in pages[target].ids:
            errors.append(f'{path.relative_to(ROOT)}: missing anchor {link}')
css_text = (ROOT/'styles.css').read_text(encoding='utf-8')
css_text_no_data_uris = re.sub(r'url\((["\'])data:.*?\1\)', '', css_text, flags=re.S)
for css_url in re.findall(r'url\([\'"]?([^\)\'\"]+)', css_text_no_data_uris):
    if not css_url.startswith(('data:','http')) and not (ROOT/css_url).is_file(): errors.append(f'CSS missing: {css_url}')
ET.parse(ROOT/'sitemap.xml')
assert not errors, '\n'.join(errors)
print(f'PASS: {len(pages)} pages; local links, anchors, images, H1, IDs, JSON-LD, fonts and CTA order.')
print('Browser rendering and interactive tests are separate and still required.')
