#!/usr/bin/env python3
"""Export the public Django site using a consistent, disposable SQLite snapshot."""
import argparse
import hashlib
import json
import os
import posixpath
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'inox'
sys.dont_write_bytecode = True
sys.path.insert(0, str(APP))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inox.settings')

CONTACT_JS = '''document.getElementById('contact_form').addEventListener('submit', function(event) {
    event.preventDefault();
    if (!this.reportValidity()) return;
    const values = new FormData(this);
    const name = [values.get('first_name'), values.get('last_name')].filter(Boolean).join(' ');
    const message = 'Hello, I am ' + name + '.\\n\\nEmail: ' + values.get('email') + '\\n\\nMessage: ' + values.get('description');
    window.location.assign('https://wa.me/PHONE_NUMBER?text=' + encodeURIComponent(message));
});'''

FILTER_JS = '''(function () {
    const params = new URLSearchParams(window.location.search);
    const search = (params.get('search') || '').toLowerCase();
    const category = params.get('category');
    if (!search && !category) return;
    const cards = document.querySelectorAll('#section-products .row.g-4 > .col-lg-4');
    let visible = 0;
    cards.forEach(card => {
        const link = card.querySelector('a[href]');
        const normalize = value => new URL(value, window.location.href).pathname.replace(/index\\.html$/, '');
        const product = window.INOX_PRODUCTS.find(item => normalize(item.url) === normalize(link.getAttribute('href')));
        const match = product && (!category || product.category_slug === category) &&
            (!search || product.search.includes(search));
        card.hidden = !match;
        if (match) visible++;
    });
    if (!visible) {
        const message = document.createElement('div');
        message.className = 'col-12 text-center';
        message.textContent = 'No products available at the moment. Please check back later.';
        document.querySelector('#section-products .row.g-4').prepend(message);
    }
})();'''


def relative_url(page, value, routes):
    """Relative clean URLs for hosting; local-file navigation is adapted by JS."""
    if value.startswith('//'):
        return 'https:' + value
    url = urlsplit(value)
    if url.scheme or url.netloc or not url.path.startswith('/'):
        return value
    path = url.path
    is_page = path.rstrip('/') + '/' in routes
    if is_page:
        path = path.rstrip('/') + '/'
    relative = posixpath.relpath(path, page)
    if is_page:
        relative = './' if relative == '.' else relative.rstrip('/') + '/'
    return urlunsplit(('', '', relative, url.query, url.fragment))


def portable_html(html, page, routes):
    def attribute(match):
        return match[1] + match[2] + relative_url(page, match[3], routes) + match[2]
    html = re.sub(r'''(\b(?:href|src|action|poster)\s*=\s*)(["'])(.*?)\2''', attribute, html, flags=re.I)
    # Background images in inline styles and data-bgimage use CSS url() syntax.
    html = re.sub(r'''url\(\s*(["']?)(/[^\s)'"]+)\1\s*\)''',
                  lambda m: 'url(' + m[1] + relative_url(page, m[2], routes) + m[1] + ')', html)
    html = re.sub(r'''(data-bgimage=["'])(/[^\s"']+)''',
                  lambda m: m[1] + relative_url(page, m[2], routes), html)
    return html


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='https://inoxflex.co.in', help='Public origin for canonical URLs and sitemap')
    args = parser.parse_args()
    origin = urlsplit(args.base_url)
    if origin.scheme not in ('http', 'https') or not origin.netloc or origin.path not in ('', '/') or origin.query or origin.fragment:
        parser.error('--base-url must be an HTTP(S) origin, without a path/query/fragment')
    base_url = args.base_url.rstrip('/')
    output = ROOT / 'static-site'
    from django.conf import settings
    source_db = Path(settings.DATABASES['default']['NAME'])
    with tempfile.TemporaryDirectory(prefix='inox-static-') as tmp:
        snapshot = Path(tmp) / 'snapshot.sqlite3'
        with sqlite3.connect(f'file:{source_db}?mode=ro', uri=True) as source, sqlite3.connect(snapshot) as dest:
            source.backup(dest)
        settings.DATABASES['default']['NAME'] = snapshot
        settings.TEMPLATES[0]['DIRS'] = [str(APP / 'templates')]
        settings.ALLOWED_HOSTS = [origin.hostname]
        import django
        django.setup()
        from django.test import Client
        from django.urls import reverse
        from django.template import Template, RequestContext
        from django.test import RequestFactory
        from home.models import Category, Product, SubCategory, PageContent, SiteSettings
        from django.core.serializers import serialize
        from django.db import connections

        staging = Path(tmp) / 'site'
        staging.mkdir()
        # Copy only website assets, never the database, accounts, sessions or enquiries.
        for name in ('static', 'media'):
            shutil.copytree(APP / name, staging / name, ignore=shutil.ignore_patterns('.DS_Store', '__pycache__'))
        extra = staging / 'static' / 'export'
        extra.mkdir(parents=True)
        site_settings = SiteSettings.load()
        phone = re.sub(r'\D', '', site_settings.get_whatsapp_number())
        if not phone:
            raise RuntimeError('Site settings must contain a WhatsApp/contact phone number')
        (extra / 'contact.js').write_text(CONTACT_JS.replace('PHONE_NUMBER', phone))
        (extra / 'products.js').write_text(FILTER_JS)
        (extra / 'navigation.js').write_text('''// Clean hosted URLs; explicit files only when opened directly from disk.
if (location.protocol === 'file:') {
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('a[href]').forEach(link => {
            const raw = link.getAttribute('href');
            if (!raw || raw.startsWith('#')) return;
            const url = new URL(raw, location.href);
            if (url.protocol === 'file:' && url.pathname.endsWith('/')) {
                url.pathname += 'index.html';
                link.href = url.href;
            }
        });
    });
} else if (location.pathname.endsWith('/index.html')) {
    history.replaceState(null, '', location.pathname.replace(/index\\.html$/, '') + location.search + location.hash);
}
''')
        products = list(Product.objects.filter(status=True).select_related('category'))
        product_index = [dict(url=reverse('product_detail', kwargs={'category_slug': p.category.slug, 'product_slug': p.slug}), category_slug=p.category.slug, search=f'{p.name} {p.description or ""} {p.category.name}'.lower()) for p in products]
        routes = [reverse(name) for name in ('homepage', 'product_list', 'category_list', 'contact', 'about', 'terms', 'privacy')]
        for model, name in ((Category, 'category_detail'), (SubCategory, 'subcategory_detail'), (Product, 'product_detail')):
            for obj in model.objects.filter(status=True):
                kwargs = {'slug': obj.slug} if model == Category else {'category_slug': obj.category.slug, 'subcategory_slug' if model == SubCategory else 'product_slug': obj.slug}
                path = reverse(name, kwargs=kwargs)
                if path in routes:
                    raise RuntimeError(f'Duplicate public URL: {path}')
                routes.append(path)
        # The original project lacks faq.html. Export actual FAQ content using its existing legal-page layout.
        faq = PageContent.objects.filter(page_type='faq', status=True).first()
        if faq:
            routes.append('/faq/')
        for product in product_index:
            product['url'] = relative_url('/products/', product['url'], routes)
        (extra / 'product-index.js').write_text('window.INOX_PRODUCTS = ' + json.dumps(product_index, ensure_ascii=True).replace('<', '\\u003c') + ';\n')
        client = Client(HTTP_HOST=origin.netloc)
        checksums = {}
        for path in routes:
            if path == '/faq/' and not (APP / 'templates/faq.html').exists():
                template = (APP / 'templates/privacy.html').read_text()
                template = template.replace('Privacy Policy', 'FAQ').replace('Legal</div>', 'Company</div>')
                request = RequestFactory().get(path, secure=origin.scheme == 'https', HTTP_HOST=origin.netloc)
                html = Template(template).render(RequestContext(request, {'page_content': faq, 'seo_title': faq.get_seo_title(), 'seo_description': faq.get_seo_description(), 'seo_keywords': faq.seo_keywords, 'og_image': faq.get_og_image(), 'canonical_url': base_url + path}))
            else:
                response = client.get(path, secure=origin.scheme == 'https')
                if response.status_code != 200:
                    raise RuntimeError(f'{path}: HTTP {response.status_code}')
                html = response.content.decode()
            html = re.sub(r'<input\b[^>]*name=["\']csrfmiddlewaretoken["\'][^>]*>', '', html)
            if path == '/contact/':
                html = html.replace('src="images/misc/5.webp"', 'src="/static/images/misc/5.webp"')
                html, count = re.subn(r'<script>\s*// Check for Django messages.*?</script>', '<script src="/static/export/contact.js"></script>', html, flags=re.S)
                if count != 1:
                    raise RuntimeError('Contact script changed; review static form adapter')
                html = html.replace("value='Send Message'", "value='Continue on WhatsApp'")
                html = html.replace('method="post" action=""', 'method="get" action="https://wa.me/' + phone + '"')
                html = html.replace('</form>', '<p class="small mt-3">Continue on WhatsApp to send your enquiry.</p><noscript>Please enable JavaScript or use the contact details on this page.</noscript></form>', 1)
            if path == '/products/':
                html = html.replace('</body>', '<script src="/static/export/product-index.js"></script><script src="/static/export/products.js"></script></body>')
            html = html.replace('</head>', '<script src="/static/export/navigation.js" defer></script></head>')
            html = portable_html(html, path, routes)
            target = staging / path.lstrip('/') / 'index.html'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding='utf-8')
            checksums[path] = hashlib.sha256(html.encode()).hexdigest()
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{escape(base_url + path)}</loc></url>\n' for path in routes) + '</urlset>\n'
        (staging / 'sitemap.xml').write_text(sitemap)
        (staging / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {base_url}/sitemap.xml\n')
        # Public CMS snapshot for reference. Private tables are deliberately not serialized.
        public = []
        for model in (Category, SubCategory, Product, PageContent):
            public.extend(model.objects.filter(status=True))
        from home.models import TeamMember
        public.extend(TeamMember.objects.filter(status=True))
        public.append(site_settings)
        (staging / 'data').mkdir()
        (staging / 'data/content.json').write_text(serialize('json', public, indent=2), encoding='utf-8')
        (staging / 'export-manifest.json').write_text(json.dumps({'generated_at': datetime.now(timezone.utc).isoformat(), 'base_url': base_url, 'pages': checksums, 'public_records': len(public), 'contact_mode': 'whatsapp'}, indent=2))
        connections.close_all()
        # Only replace this exporter's marked output, never an unrelated directory.
        if output.exists():
            if not (output / 'export-manifest.json').exists():
                raise RuntimeError(f'Refusing to replace unrecognized output directory: {output}')
            shutil.rmtree(output)
        shutil.copytree(staging, output)
        print(f'Exported {len(routes)} pages and {len(public)} public records to {output}')


if __name__ == '__main__':
    main()
