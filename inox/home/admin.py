from django.contrib import admin
from .models import Category, Product, SubCategory

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    list_editable = ['status']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'status', 'created_at', 'updated_at']
    list_filter = ['category', 'status', 'created_at', 'updated_at', 'price']
    search_fields = ['name', 'description', 'category__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    list_editable = ['price', 'status']
    raw_id_fields = ['category']

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'status', 'created_at', 'updated_at']
    list_filter = ['category', 'status', 'created_at', 'updated_at']
    search_fields = ['name', 'description', 'category__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['category', 'name']
    list_editable = ['status']
    raw_id_fields = ['category']
