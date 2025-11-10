from .models import Category, Product, SiteSettings

def categories(request):
    """
    Context processor to make categories, products, and site settings available in all templates
    """
    categories = Category.objects.filter(status=True).prefetch_related('subcategories')
    products = Product.objects.filter(status=True).select_related('category')
    site_settings = SiteSettings.load()
    return {
        'categories': categories,
        'products': products,
        'site_settings': site_settings,
    }
