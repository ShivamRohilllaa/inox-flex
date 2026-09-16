# Inox Flex static version

`static-site/` is a standalone snapshot of the public website. It contains plain HTML, CSS, JavaScript, images, fonts, the PDF catalogue, sitemap, and robots.txt. Deploy that directory as the web root on a static host with directory index support. No Django, database, Node build, or API is needed to serve it. Double-click `static-site/index.html` to open it directly in Chrome. Local assets use relative paths. Hosted navigation uses clean directory URLs; a small JavaScript adapter adds index.html only for direct file browsing. Keep the entire folder together.

## Optional HTTP preview

From this repository's root:

```sh
python3 -m http.server 8001 --bind 127.0.0.1 --directory static-site
```

Open http://127.0.0.1:8001/ . The Django version remains separate on port 8000.

## Refresh from the database

```sh
myenv/bin/python tools/export_static.py
```

The exporter snapshots `inox/db.sqlite3` using SQLite's backup API, renders the existing Django templates against that disposable snapshot, and copies local assets. It does not modify the source database or Django templates. A successful build replaces the generated `static-site/` directory; make persistent changes in the original templates/database or the exporter, then rebuild.

For another production domain:

```sh
myenv/bin/python tools/export_static.py --base-url https://example.com
```

The configured origin is used for canonical/social URLs and the sitemap. Page navigation and local assets stay on the host serving the static version. Relative links also support hosting under a subdirectory; canonical metadata still uses the configured production origin.

## Included content and behavior

- Homepage, product list/details, category/subcategory pages, contact, about, terms and privacy use the same templates and current active database content.
- Existing descriptions, specifications, images, team members, settings and SEO fields are preserved. `data/content.json` contains the public CMS records; `export-manifest.json` lists pages and hashes.
- FAQ is exported if an active FAQ record exists. Since the source lacks a FAQ template, the exporter uses the existing legal-page layout for that content.
- Product `?search=` and `?category=` filters run in the browser.
- Contact form opens a composed WhatsApp enquiry using the database's WhatsApp/contact number. The visitor sends it in WhatsApp. Static hosting cannot save enquiries to the database, and the form does not claim that a message has already been sent.
- Admin login, customer enquiries, user accounts, sessions, and inactive records are not published.
- Database changes become visible after rebuilding; this is a snapshot, not a live database connection.

## Verification

```sh
python3 tools/verify_static.py http://127.0.0.1:8001
```

Checks every exported page over HTTP, page hashes, local links, exact asset copies, and the public-data allowlist. Omit the URL to run file checks without a server.

The six missing homepage icons are replaced with bundled Font Awesome icons. External product image URLs/links embedded in CMS descriptions and third-party services such as Google Translate and Analytics remain. External resources still need internet access. The static export fixes the contact page's relative image path to use the existing local image.
