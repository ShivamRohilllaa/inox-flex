from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Product, Category, SubCategory, PageContent

class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 1.0
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        # Return list of static page names
        return [
            'homepage',
            'product_list',
            'category_list',
            'contact',
            'about',
        ]

    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        # Return current time for static pages
        return timezone.now()

class PageContentSitemap(Sitemap):
    """Sitemap for dynamic page content (About, Terms, Privacy, FAQ)"""
    priority = 0.8
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        return PageContent.objects.filter(status=True)

    def location(self, obj):
        # Map page types to their URLs
        page_type_map = {
            'about_us': 'about',
            'terms_conditions': 'terms',
            'privacy_policy': 'privacy',
            'faq': 'faq',
        }
        return reverse(page_type_map.get(obj.page_type, 'homepage'))

    def lastmod(self, obj):
        return obj.updated_at

class CategorySitemap(Sitemap):
    """Sitemap for category pages"""
    priority = 0.9
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return Category.objects.filter(status=True)

    def location(self, obj):
        return reverse('category_detail', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.updated_at

class SubCategorySitemap(Sitemap):
    """Sitemap for subcategory pages"""
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return SubCategory.objects.filter(status=True)

    def location(self, obj):
        return reverse('subcategory_detail', kwargs={
            'category_slug': obj.category.slug,
            'subcategory_slug': obj.slug
        })

    def lastmod(self, obj):
        return obj.updated_at

class ProductSitemap(Sitemap):
    """Sitemap for product pages"""
    priority = 0.9
    changefreq = 'weekly'
    protocol = 'https'
    limit = 5000  # Limit per sitemap file (Google's limit is 50,000)

    def items(self):
        return Product.objects.filter(status=True).select_related('category')

    def location(self, obj):
        return reverse('product_detail', kwargs={
            'category_slug': obj.category.slug,
            'product_slug': obj.slug
        })

    def lastmod(self, obj):
        return obj.updated_at

