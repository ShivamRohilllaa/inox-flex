from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Homepage
    path('', views.homepage, name='homepage'),
    
    # SEO
    path('robots.txt', views.robots_txt, name='robots_txt'),
    
    # Static Pages (must come early to avoid conflicts)
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.page_content_view, {'page_type': 'about_us'}, name='about'),
    path('terms/', views.page_content_view, {'page_type': 'terms_conditions'}, name='terms'),
    path('privacy/', views.page_content_view, {'page_type': 'privacy_policy'}, name='privacy'),
    path('faq/', views.page_content_view, {'page_type': 'faq'}, name='faq'),
    
    # Product and Category URLs
    path('products/', views.product_list, name='product_list'),
    path('categories/', views.category_list, name='category_list'),
    
    # Category detail (specific prefix)
    path('cat/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Subcategory detail (specific prefix)
    path('sub/<slug:category_slug>/<slug:subcategory_slug>/', views.subcategory_detail, name='subcategory_detail'),
    
    # Product detail (two slugs without prefix - comes last)
    path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
