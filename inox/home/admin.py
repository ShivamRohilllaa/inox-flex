from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Product, SubCategory, Contact, PageContent, SiteSettings, TeamMember

# Register your models here.

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['name', 'slug', 'description', 'seo_title', 'seo_description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    list_editable = ['status']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'image', 'status')
        }),
        ('SEO Settings', {
            'fields': ('seo_title', 'seo_description', 'seo_keywords', 'og_image'),
            'classes': ('collapse',),
            'description': 'Leave blank to auto-generate from name/description'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'category', 'price', 'status', 'created_at', 'updated_at']
    list_filter = ['category', 'status', 'created_at', 'updated_at', 'price']
    search_fields = ['name', 'slug', 'description', 'category__name', 'seo_title', 'seo_description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    list_editable = ['price', 'status']
    raw_id_fields = ['category']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'slug', 'category', 'price', 'status')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Specifications & Technical Details', {
            'fields': ('specifications',),
            'description': 'Add product specifications, technical details, or table data. You can create HTML tables using the editor.'
        }),
        ('Images', {
            'fields': ('image', 'image_url'),
            'description': 'Upload an image OR provide an image URL (image upload takes priority)'
        }),
        ('SEO Settings', {
            'fields': ('seo_title', 'seo_description', 'seo_keywords', 'og_image'),
            'classes': ('collapse',),
            'description': 'Leave blank to auto-generate from name/description'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SubCategory)
class SubCategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'category', 'status', 'created_at', 'updated_at']
    list_filter = ['category', 'status', 'created_at', 'updated_at']
    search_fields = ['name', 'slug', 'description', 'category__name', 'seo_title', 'seo_description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['category', 'name']
    list_editable = ['status']
    raw_id_fields = ['category']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'image', 'status')
        }),
        ('SEO Settings', {
            'fields': ('seo_title', 'seo_description', 'seo_keywords', 'og_image'),
            'classes': ('collapse',),
            'description': 'Leave blank to auto-generate from name/description'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Contact)
class ContactAdmin(ModelAdmin):
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
class PageContentAdmin(ModelAdmin):
    list_display = ['get_page_type_display', 'title', 'status', 'created_at', 'updated_at']
    list_filter = ['page_type', 'status', 'created_at', 'updated_at']
    search_fields = ['title', 'content', 'seo_title', 'seo_description', 'seo_keywords']
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
        ('Basic SEO', {
            'fields': ('seo_title', 'seo_description', 'seo_keywords'),
            'description': 'Basic meta tags for search engines'
        }),
        ('Open Graph (Facebook, LinkedIn)', {
            'fields': ('og_title', 'og_description', 'og_image'),
            'classes': ('collapse',),
            'description': 'Leave blank to use basic SEO values'
        }),
        ('Twitter Card', {
            'fields': ('twitter_card_type', 'twitter_title', 'twitter_description', 'twitter_image'),
            'classes': ('collapse',),
            'description': 'Leave blank to use Open Graph values'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False
    
    list_display = ['phone_number', 'whatsapp_number', 'email', 'updated_at']
    fieldsets = (
        ('Contact Information', {
            'fields': ('phone_number', 'whatsapp_number', 'email', 'address')
        }),
        ('Social Media Links', {
            'fields': ('facebook_url', 'youtube_url', 'instagram_url', 'twitter_url', 'linkedin_url'),
            'description': 'Add your social media profile URLs. Leave blank to hide the icon.'
        }),
        ('Default SEO Settings', {
            'fields': ('site_name', 'default_seo_title', 'default_seo_description', 'default_seo_keywords'),
            'description': 'Default SEO values used when pages don\'t have specific SEO settings'
        }),
        ('Social Media SEO', {
            'fields': ('og_image_default', 'twitter_handle'),
            'classes': ('collapse',),
            'description': 'Default images and handles for social media sharing'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

@admin.register(TeamMember)
class TeamMemberAdmin(ModelAdmin):
    list_display = ['full_name', 'role', 'order', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['first_name', 'last_name', 'role', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['order', 'first_name']
    list_editable = ['order', 'status']
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'role', 'description', 'order', 'status')
        }),
        ('Social Media Links', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url'),
            'description': 'Add social media profile URLs. Leave blank to hide the icon.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
