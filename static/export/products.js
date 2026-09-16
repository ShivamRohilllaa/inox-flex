(function () {
    const params = new URLSearchParams(window.location.search);
    const search = (params.get('search') || '').toLowerCase();
    const category = params.get('category');
    if (!search && !category) return;
    const cards = document.querySelectorAll('#section-products .row.g-4 > .col-lg-4');
    let visible = 0;
    cards.forEach(card => {
        const link = card.querySelector('a[href]');
        const normalize = value => new URL(value, window.location.href).pathname.replace(/index\.html$/, '');
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
})();