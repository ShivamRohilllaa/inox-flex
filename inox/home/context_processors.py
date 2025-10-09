from .models import Category

def categories(request):
    """
    Context processor to make categories available in all templates
    """
    categories = Category.objects.filter(status=True).prefetch_related('subcategories')
    return {
        'categories': categories,
    }
