from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Homepage
    path('', views.homepage, name='homepage'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('cat/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # SubCategory URLs
    path('<slug:category_slug>/<slug:subcategory_slug>/', views.subcategory_detail, name='subcategory_detail'),
    
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Contact URL
    path('contact/', views.contact_view, name='contact'),
    
    # Page Content URLs
    path('about/', views.page_content_view, {'page_type': 'about_us'}, name='about'),
    path('terms/', views.page_content_view, {'page_type': 'terms_conditions'}, name='terms'),
    path('privacy/', views.page_content_view, {'page_type': 'privacy_policy'}, name='privacy'),
    path('faq/', views.page_content_view, {'page_type': 'faq'}, name='faq'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
