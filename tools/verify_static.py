#!/usr/bin/env python3
"""Verify exported routes, local references, public data and copied assets."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import urlopen
import sys
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
site = root / 'static-site'
manifest = json.loads((site / 'export-manifest.json').read_text())
sitemap_urls = [element.text for element in ET.parse(site / 'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(sitemap_urls) == len(set(sitemap_urls))
assert set(sitemap_urls) == {manifest['base_url'] + route for route in manifest['pages']}
assert all(url.endswith('/') and '.html' not in url for url in sitemap_urls)
assert f"Sitemap: {manifest['base_url']}/sitemap.xml" in (site / 'robots.txt').read_text()
errors = []
# These source-template icons are missing in the original Django project too.
known_missing = {f'/static/images/icons/white/{name}.webp' for name in ('engineer', 'quality', 'material', 'custom', 'global', 'support')}
inherited = set()

class References(HTMLParser):
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'canonical':
            assert attrs['href'] == manifest['base_url'] + route
        for name, value in attrs.items():
            if name not in ('href', 'src') or not value:
                continue
            if value.startswith('/'):
                errors.append(f'{route}: non-portable reference {value}')
            url = urlsplit(urljoin(route + 'index.html', value))
            if url.scheme or url.netloc or not url.path:
                continue
            target = site / unquote(url.path).lstrip('/')
            if url.path.endswith('/'):
                target = target / 'index.html'
            if not target.is_file():
                if url.path in known_missing:
                    inherited.add(url.path)
                else:
                    errors.append(f'{route}: missing {url.path}')

for route, checksum in manifest['pages'].items():
    page = site / route.lstrip('/') / 'index.html'
    html = page.read_text()
    assert hashlib.sha256(page.read_bytes()).hexdigest() == checksum, route
    assert '{% ' not in html and 'csrfmiddlewaretoken' not in html, route
    References().feed(html)
    assert f'href="{manifest["base_url"]}{route}"' in html, ('canonical', route)
    assert 'rel="icon"' in html and 'favicon-32.png' in html, route
    if len(sys.argv) > 1:
        with urlopen(sys.argv[1].rstrip('/') + route) as response:
            assert response.status == 200
            assert response.read() == page.read_bytes(), route
for source in (root / 'inox/static').rglob('*'):
    if source.is_file() and source.name != '.DS_Store':
        assert source.read_bytes() == (site / 'static' / source.relative_to(root / 'inox/static')).read_bytes(), source
for source in (root / 'inox/media').rglob('*'):
    if source.is_file() and source.name != '.DS_Store':
        assert source.read_bytes() == (site / 'media' / source.relative_to(root / 'inox/media')).read_bytes(), source
records = json.loads((site / 'data/content.json').read_text())
assert len(records) == manifest['public_records']
allowed = {'home.category', 'home.subcategory', 'home.product', 'home.pagecontent', 'home.teammember', 'home.sitesettings'}
assert all(record['model'] in allowed for record in records)
assert not list(site.rglob('*.sqlite3')) and not (site / 'admin').exists()
contact = (site / 'contact/index.html').read_text()
assert 'fetch(' not in contact and 'Continue on WhatsApp' in contact
assert 'method="post"' not in contact
print(f'Checked {len(manifest["pages"])} pages, {len(records)} public records, and exact copies of local assets.')
print(f'Inherited missing source icons: {len(inherited)}')
for error in errors:
    print('ERROR:', error)
if errors:
    raise SystemExit(1)
print('PASS: no new broken local references; no database or private tables exported.')
