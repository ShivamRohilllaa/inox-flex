// Clean hosted URLs; explicit files only when opened directly from disk.
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
    history.replaceState(null, '', location.pathname.replace(/index\.html$/, '') + location.search + location.hash);
}
