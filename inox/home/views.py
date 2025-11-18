from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .models import Category, Product, SubCategory, Contact, PageContent, TeamMember, SiteSettings
from .forms import ContactForm

# Create your views here.
def homepage(request):
    # Get categories with their active products for the homepage tabs
    categories = Category.objects.filter(status=True).prefetch_related(
        Prefetch('products', queryset=Product.objects.filter(status=True))
    )[:2]
    # Get all products for fallback display
    products = Product.objects.filter(status=True)[:6]
    site_settings = SiteSettings.load()
    
    context = {
        'categories': categories,
        'products': products,
        'seo_title': site_settings.default_seo_title,
        'seo_description': site_settings.default_seo_description,
        'seo_keywords': site_settings.default_seo_keywords,
        'og_image': site_settings.og_image_default.url if site_settings.og_image_default else None,
        'og_type': 'website',
    }
    return render(request, 'index.html', context)

def category_list(request):
    categories = Category.objects.filter(status=True)
    site_settings = SiteSettings.load()
    
    context = {
        'categories': categories,
        'seo_title': f'Categories - {site_settings.site_name}',
        'seo_description': f'Browse all product categories at {site_settings.site_name}. Find the perfect stainless steel hoses, pipe fittings, and industrial solutions.',
        'seo_keywords': f'categories, product categories, {site_settings.default_seo_keywords}',
        'og_type': 'website',
    }
    return render(request, 'categories/list.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, status=True)
    subcategories = SubCategory.objects.filter(category=category, status=True)
    products = Product.objects.filter(category=category, status=True)
    
    og_image = category.get_og_image()
    if og_image and not og_image.startswith('http'):
        og_image = request.build_absolute_uri(og_image)
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'products': products,
        'seo_title': category.get_seo_title(),
        'seo_description': category.get_seo_description(),
        'seo_keywords': category.seo_keywords,
        'og_title': category.get_seo_title(),
        'og_description': category.get_seo_description(),
        'og_image': og_image,
        'og_type': 'website',
        'canonical_url': request.build_absolute_uri(),
    }
    return render(request, 'categories/detail.html', context)

def subcategory_detail(request, category_slug, subcategory_slug):
    subcategory = get_object_or_404(
        SubCategory, 
        slug=subcategory_slug, 
        category__slug=category_slug,
        status=True
    )
    products = Product.objects.filter(
        category=subcategory.category, 
        status=True
    )
    
    og_image = subcategory.get_og_image()
    if og_image and not og_image.startswith('http'):
        og_image = request.build_absolute_uri(og_image)
    
    context = {
        'subcategory': subcategory,
        'products': products,
        'seo_title': subcategory.get_seo_title(),
        'seo_description': subcategory.get_seo_description(),
        'seo_keywords': subcategory.seo_keywords,
        'og_title': subcategory.get_seo_title(),
        'og_description': subcategory.get_seo_description(),
        'og_image': og_image,
        'og_type': 'website',
        'canonical_url': request.build_absolute_uri(),
    }
    return render(request, 'subcategories/detail.html', context)

def product_list(request):
    products = Product.objects.filter(status=True)
    categories = Category.objects.filter(status=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Category filter
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category__slug=category_filter)
    
    # No pagination needed for now, show all products
    # paginator = Paginator(products, 12)
    # page_number = request.GET.get('page')
    # products = paginator.get_page(page_number)
    
    site_settings = SiteSettings.load()
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'seo_title': f'Products - {site_settings.site_name}',
        'seo_description': f'Browse our complete range of stainless steel products including hoses, pipe fittings, expansion joints, and more at {site_settings.site_name}.',
        'seo_keywords': f'products, stainless steel products, {site_settings.default_seo_keywords}',
        'og_type': 'website',
    }
    return render(request, 'products.html', context)

def product_detail(request, category_slug, product_slug):
    product = get_object_or_404(
        Product, 
        slug=product_slug, 
        category__slug=category_slug,
        status=True
    )
    related_products = Product.objects.filter(
        category=product.category, 
        status=True
    ).exclude(id=product.id)[:4]
    
    og_image = product.get_og_image()
    if og_image and not og_image.startswith('http'):
        og_image = request.build_absolute_uri(og_image)
    
    context = {
        'product': product,
        'related_products': related_products,
        'seo_title': product.get_seo_title(),
        'seo_description': product.get_seo_description(),
        'seo_keywords': product.seo_keywords or f"{product.name}, {product.category.name}",
        'og_title': product.get_seo_title(),
        'og_description': product.get_seo_description(),
        'og_image': og_image,
        'og_type': 'product',
        'twitter_card': 'summary_large_image',
        'canonical_url': request.build_absolute_uri(),
    }
    return render(request, 'product-details.html', context)

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Prepare data for WhatsApp message
                first_name = form.cleaned_data.get('first_name', '')
                last_name = form.cleaned_data.get('last_name', '')
                email = form.cleaned_data.get('email', '')
                description = form.cleaned_data.get('description', '')
                
                return JsonResponse({
                    'success': True,
                    'message': 'Your message has been sent successfully! We will get back to you soon.',
                    'form_data': {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'description': description
                    }
                })
            else:
                messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
                return redirect('contact')
        else:
            # Handle form errors for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the errors in the form.',
                    'errors': form.errors
                })
            else:
                messages.error(request, 'Please correct the errors in the form.')
    else:
        form = ContactForm()
    
    site_settings = SiteSettings.load()
    
    context = {
        'form': form,
        'seo_title': f'Contact Us - {site_settings.site_name}',
        'seo_description': f'Get in touch with {site_settings.site_name}. Contact us for inquiries about our stainless steel hoses, pipe fittings, and industrial solutions.',
        'seo_keywords': f'contact, contact us, {site_settings.default_seo_keywords}',
        'og_type': 'website',
    }
    return render(request, 'contact.html', context)

def page_content_view(request, page_type):
    try:
        page_content = get_object_or_404(PageContent, page_type=page_type, status=True)
    except:
        page_content = None
    
    # Get team members for about page
    team_members = None
    if page_type == 'about_us':
        team_members = TeamMember.objects.filter(status=True)
    
    # SEO context from page_content
    context = {
        'page_content': page_content,
        'page_type': page_type,
        'team_members': team_members,
    }
    
    # Add SEO data if page_content exists
    if page_content:
        og_image = page_content.get_og_image()
        twitter_image = page_content.get_twitter_image()
        
        if og_image and not og_image.startswith('http'):
            og_image = request.build_absolute_uri(og_image)
        if twitter_image and not twitter_image.startswith('http'):
            twitter_image = request.build_absolute_uri(twitter_image)
        
        context.update({
            'seo_title': page_content.get_seo_title(),
            'seo_description': page_content.get_seo_description(),
            'seo_keywords': page_content.seo_keywords,
            'og_title': page_content.get_og_title(),
            'og_description': page_content.get_og_description(),
            'og_image': og_image,
            'og_type': 'website',
            'twitter_card': page_content.twitter_card_type,
            'twitter_title': page_content.get_twitter_title(),
            'twitter_description': page_content.get_twitter_description(),
            'twitter_image': twitter_image,
            'canonical_url': request.build_absolute_uri(),
        })
    
    # Map page types to templates
    template_map = {
        'about_us': 'about.html',
        'terms_conditions': 'terms.html',
        'privacy_policy': 'privacy.html',
        'faq': 'faq.html',
    }
    
    template = template_map.get(page_type, 'default.html')
    return render(request, template, context)

def robots_txt(request):
    """Generate robots.txt file"""
    host = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    sitemap_url = f"{protocol}://{host}/sitemap.xml"
    
    robots_content = f"""User-agent: *
Allow: /

# Sitemap
Sitemap: {sitemap_url}

# Disallow admin and private areas
Disallow: /admin/
Disallow: /staticfiles/
"""
    return HttpResponse(robots_content, content_type='text/plain')