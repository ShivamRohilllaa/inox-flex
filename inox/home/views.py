from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, Product, SubCategory, Contact, PageContent
from .forms import ContactForm

# Create your views here.
def homepage(request):
    products = Product.objects.filter(status=True)[:6]
    context = {
        'products': products,
    }
    return render(request, 'index.html', context)

def category_list(request):
    categories = Category.objects.filter(status=True)
    context = {
        'categories': categories,
    }
    return render(request, 'categories/list.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, status=True)
    subcategories = SubCategory.objects.filter(category=category, status=True)
    products = Product.objects.filter(category=category, status=True)
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'products': products,
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
    
    context = {
        'subcategory': subcategory,
        'products': products,
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
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
    }
    return render(request, 'products/list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, status=True)
    related_products = Product.objects.filter(
        category=product.category, 
        status=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/detail.html', context)

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
    }
    return render(request, 'contact.html', context)

def page_content_view(request, page_type):
    try:
        page_content = get_object_or_404(PageContent, page_type=page_type, status=True)
    except:
        page_content = None
    
    context = {
        'page_content': page_content,
        'page_type': page_type,
    }
    
    # Map page types to templates
    template_map = {
        'about_us': 'about.html',
        'terms_conditions': 'terms.html',
        'privacy_policy': 'privacy.html',
        'faq': 'faq.html',
    }
    
    template = template_map.get(page_type, 'default.html')
    return render(request, template, context)