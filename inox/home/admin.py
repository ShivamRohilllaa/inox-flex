from django.contrib import admin
from .models import Category, Product, SubCategory, Contact, PageContent

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['name', 'slug', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    list_editable = ['status']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'price', 'status', 'created_at', 'updated_at']
    list_filter = ['category', 'status', 'created_at', 'updated_at', 'price']
    search_fields = ['name', 'slug', 'description', 'category__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    list_editable = ['price', 'status']
    raw_id_fields = ['category']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'status', 'created_at', 'updated_at']
    list_filter = ['category', 'status', 'created_at', 'updated_at']
    search_fields = ['name', 'slug', 'description', 'category__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['category', 'name']
    list_editable = ['status']
    raw_id_fields = ['category']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['first_name', 'last_name', 'email', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    list_editable = ['status']
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Inquiry Details', {
            'fields': ('description', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ['get_page_type_display', 'title', 'status', 'created_at', 'updated_at']
    list_filter = ['page_type', 'status', 'created_at', 'updated_at']
    search_fields = ['title', 'content', 'meta_description', 'meta_keywords']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['page_type']
    list_editable = ['status']
    fieldsets = (
        ('Page Information', {
            'fields': ('page_type', 'title', 'status')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('SEO Settings', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
