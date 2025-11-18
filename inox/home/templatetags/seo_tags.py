from django import template
from django.conf import settings
from home.models import SiteSettings

register = template.Library()

@register.inclusion_tag('seo/meta_tags.html', takes_context=True)
def seo_meta_tags(context):
    """
    Renders comprehensive SEO meta tags including:
    - Basic meta tags (title, description, keywords)
    - Open Graph tags
    - Twitter Card tags
    - Canonical URL
    """
    request = context.get('request')
    site_settings = SiteSettings.load()
    
    # Get SEO data from context
    seo_data = {
        'title': context.get('seo_title') or site_settings.default_seo_title,
        'description': context.get('seo_description') or site_settings.default_seo_description,
        'keywords': context.get('seo_keywords') or site_settings.default_seo_keywords,
        'og_title': context.get('og_title') or context.get('seo_title') or site_settings.default_seo_title,
        'og_description': context.get('og_description') or context.get('seo_description') or site_settings.default_seo_description,
        'og_image': context.get('og_image') or (site_settings.og_image_default.url if site_settings.og_image_default else None),
        'og_type': context.get('og_type', 'website'),
        'twitter_card': context.get('twitter_card', 'summary_large_image'),
        'twitter_title': context.get('twitter_title') or context.get('seo_title') or site_settings.default_seo_title,
        'twitter_description': context.get('twitter_description') or context.get('seo_description') or site_settings.default_seo_description,
        'twitter_image': context.get('twitter_image') or context.get('og_image') or (site_settings.og_image_default.url if site_settings.og_image_default else None),
        'canonical_url': context.get('canonical_url'),
        'site_name': site_settings.site_name,
        'twitter_handle': site_settings.twitter_handle,
    }
    
    # Build full URLs for images
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        
        if seo_data['og_image'] and not seo_data['og_image'].startswith('http'):
            seo_data['og_image'] = f"{protocol}://{host}{seo_data['og_image']}"
        
        if seo_data['twitter_image'] and not seo_data['twitter_image'].startswith('http'):
            seo_data['twitter_image'] = f"{protocol}://{host}{seo_data['twitter_image']}"
        
        if not seo_data['canonical_url']:
            seo_data['canonical_url'] = f"{protocol}://{host}{request.path}"
    
    return seo_data

