# Inox Flex static website

This branch contains the standalone static website at the repository root.

- `index.html`: homepage
- `about/`, `contact/`, `products/`, `cat/`, `sub/`: pages with clean directory URLs
- `hoses/`, `pipe-fittings/`: product details
- `static/`, `media/`: styles, scripts, images, fonts and catalogue
- `sitemap.xml`, `robots.txt`: search engine files

No Python, Django, virtual environment, database or build step is required.
Open `index.html` directly, keeping this folder together, or serve the folder on any static host.

## GitHub Pages

In repository Settings → Pages, select **Deploy from a branch**, choose **static_website**, and choose **/ (root)**. The `.nojekyll` file preserves the static assets without Jekyll processing.

Production canonical URLs and sitemap currently use `https://inoxflex.co.in`. Configure the custom domain and DNS when deploying to that domain. No live DNS or hosting settings were changed by this branch cleanup.

The contact form opens a WhatsApp draft. External images, Google services and WhatsApp require internet access.
