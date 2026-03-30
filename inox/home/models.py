from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.utils.html import strip_tags
from ckeditor.fields import RichTextField
import re

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, null=True)
    description = RichTextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    status = models.BooleanField(default=True)
    # SEO Fields
    seo_title = models.CharField(max_length=70, blank=True, null=True, help_text="SEO Title (recommended: 50-60 characters)")
    seo_description = models.TextField(max_length=160, blank=True, null=True, help_text="SEO Meta Description (recommended: 150-160 characters)")
    seo_keywords = models.CharField(max_length=255, blank=True, null=True, help_text="SEO Keywords (comma-separated)")
    og_image = models.ImageField(upload_to='seo/og/', blank=True, null=True, help_text="Open Graph Image (1200x630px recommended)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _strip_html(self, html_content):
        """Strip HTML tags from RichTextField content"""
        if not html_content:
            return ""
        text = strip_tags(html_content)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _generate_seo_title(self):
        """Generate SEO title from name"""
        # Keep title under 60 characters for best SEO
        title = self.name
        if len(title) > 60:
            title = title[:57] + "..."
        return title
    
    def _generate_seo_description(self):
        """Generate SEO description from description field"""
        if not self.description:
            return f"Browse {self.name} products. Quality stainless steel solutions for your industrial needs."
        
        # Strip HTML and get clean text
        text = self._strip_html(self.description)
        
        # If description is too short, add more context
        if len(text) < 50:
            text = f"{text}. Quality stainless steel solutions for your industrial needs."
        
        # Truncate to 160 characters (optimal for SEO)
        if len(text) > 160:
            # Try to cut at word boundary
            truncated = text[:157]
            last_space = truncated.rfind(' ')
            if last_space > 100:  # Only use word boundary if reasonable
                text = truncated[:last_space] + "..."
            else:
                text = truncated + "..."
        
        return text
    
    def _generate_seo_keywords(self):
        """Generate SEO keywords from name and category"""
        keywords = [self.name.lower()]
        # Add variations
        name_words = self.name.lower().split()
        keywords.extend(name_words)
        # Add common industry terms
        keywords.extend(['stainless steel', 'industrial', 'hoses', 'pipe fittings'])
        # Remove duplicates and join
        return ', '.join(list(dict.fromkeys(keywords))[:10])  # Max 10 keywords
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Auto-generate SEO fields if blank
        if not self.seo_title:
            self.seo_title = self._generate_seo_title()
        
        if not self.seo_description:
            self.seo_description = self._generate_seo_description()
        
        if not self.seo_keywords:
            self.seo_keywords = self._generate_seo_keywords()
        
        super().save(*args, **kwargs)
    
    def get_seo_title(self):
        return self.seo_title or self.name
    
    def get_seo_description(self):
        return self.seo_description or (self.description[:157] + '...' if self.description and len(self.description) > 160 else self.description)
    
    def get_og_image(self):
        if self.og_image:
            return self.og_image.url
        elif self.image:
            return self.image.url
        return None

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, null=True)
    description = RichTextField(blank=True, null=True)
    specifications = RichTextField(blank=True, null=True, help_text="Add product specifications, technical details, or table data here. You can use HTML tables.")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Alternative: Use image URL instead of uploading")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    status = models.BooleanField(default=True)
    # SEO Fields
    seo_title = models.CharField(max_length=70, blank=True, null=True, help_text="SEO Title (recommended: 50-60 characters)")
    seo_description = models.TextField(max_length=160, blank=True, null=True, help_text="SEO Meta Description (recommended: 150-160 characters)")
    seo_keywords = models.CharField(max_length=255, blank=True, null=True, help_text="SEO Keywords (comma-separated)")
    og_image = models.ImageField(upload_to='seo/og/', blank=True, null=True, help_text="Open Graph Image (1200x630px recommended)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _strip_html(self, html_content):
        """Strip HTML tags from RichTextField content"""
        if not html_content:
            return ""
        text = strip_tags(html_content)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _generate_seo_title(self):
        """Generate SEO title from product name and category"""
        title = self.name
        # Add category if title is short
        if len(title) < 40 and self.category:
            title = f"{title} - {self.category.name}"
        # Keep under 60 characters
        if len(title) > 60:
            title = title[:57] + "..."
        return title
    
    def _generate_seo_description(self):
        """Generate SEO description from product description"""
        if not self.description:
            category_name = self.category.name if self.category else "products"
            return f"Buy {self.name} - Premium quality stainless steel {category_name.lower()}. Trusted manufacturer with ISO certified products."
        
        text = self._strip_html(self.description)
        
        if len(text) < 50:
            category_name = self.category.name if self.category else "products"
            text = f"{text}. Premium quality stainless steel {category_name.lower()} from trusted manufacturer."
        
        if len(text) > 160:
            truncated = text[:157]
            last_space = truncated.rfind(' ')
            if last_space > 100:
                text = truncated[:last_space] + "..."
            else:
                text = truncated + "..."
        
        return text
    
    def _generate_seo_keywords(self):
        """Generate SEO keywords from product name, category"""
        keywords = [self.name.lower()]
        name_words = self.name.lower().split()
        keywords.extend(name_words)
        
        if self.category:
            keywords.append(self.category.name.lower())
            keywords.extend(self.category.name.lower().split())
        
        keywords.extend(['stainless steel', 'industrial', 'manufacturer', 'ISO certified'])
        return ', '.join(list(dict.fromkeys(keywords))[:10])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Auto-generate SEO fields if blank
        if not self.seo_title:
            self.seo_title = self._generate_seo_title()
        
        if not self.seo_description:
            self.seo_description = self._generate_seo_description()
        
        if not self.seo_keywords:
            self.seo_keywords = self._generate_seo_keywords()
        
        super().save(*args, **kwargs)
    
    def get_image(self):
        """Returns image URL - prioritizes uploaded image, then image_url, then default"""
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None
    
    def get_seo_title(self):
        return self.seo_title or self.name
    
    def get_seo_description(self):
        return self.seo_description or (self.description[:157] + '...' if self.description and len(self.description) > 160 else self.description)
    
    def get_og_image(self):
        if self.og_image:
            return self.og_image.url
        elif self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, null=True)
    description = RichTextField(blank=True, null=True)
    image = models.ImageField(upload_to='subcategories/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    status = models.BooleanField(default=True)
    # SEO Fields
    seo_title = models.CharField(max_length=70, blank=True, null=True, help_text="SEO Title (recommended: 50-60 characters)")
    seo_description = models.TextField(max_length=160, blank=True, null=True, help_text="SEO Meta Description (recommended: 150-160 characters)")
    seo_keywords = models.CharField(max_length=255, blank=True, null=True, help_text="SEO Keywords (comma-separated)")
    og_image = models.ImageField(upload_to='seo/og/', blank=True, null=True, help_text="Open Graph Image (1200x630px recommended)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _strip_html(self, html_content):
        """Strip HTML tags from RichTextField content"""
        if not html_content:
            return ""
        text = strip_tags(html_content)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _generate_seo_title(self):
        """Generate SEO title from subcategory and category name"""
        if self.category:
            title = f"{self.name} - {self.category.name}"
        else:
            title = self.name
        
        if len(title) > 60:
            title = title[:57] + "..."
        return title
    
    def _generate_seo_description(self):
        """Generate SEO description from subcategory description"""
        if not self.description:
            category_name = self.category.name if self.category else "products"
            return f"Browse {self.name} {category_name.lower()}. Quality stainless steel solutions for your industrial needs."
        
        text = self._strip_html(self.description)
        
        if len(text) < 50:
            category_name = self.category.name if self.category else "products"
            text = f"{text}. Quality stainless steel {category_name.lower()} solutions."
        
        if len(text) > 160:
            truncated = text[:157]
            last_space = truncated.rfind(' ')
            if last_space > 100:
                text = truncated[:last_space] + "..."
            else:
                text = truncated + "..."
        
        return text
    
    def _generate_seo_keywords(self):
        """Generate SEO keywords from subcategory and category"""
        keywords = [self.name.lower()]
        name_words = self.name.lower().split()
        keywords.extend(name_words)
        
        if self.category:
            keywords.append(self.category.name.lower())
            keywords.extend(self.category.name.lower().split())
        
        keywords.extend(['stainless steel', 'industrial', 'subcategory'])
        return ', '.join(list(dict.fromkeys(keywords))[:10])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Auto-generate SEO fields if blank
        if not self.seo_title:
            self.seo_title = self._generate_seo_title()
        
        if not self.seo_description:
            self.seo_description = self._generate_seo_description()
        
        if not self.seo_keywords:
            self.seo_keywords = self._generate_seo_keywords()
        
        super().save(*args, **kwargs)
    
    def get_seo_title(self):
        return self.seo_title or f"{self.name} - {self.category.name}"
    
    def get_seo_description(self):
        return self.seo_description or (self.description[:157] + '...' if self.description and len(self.description) > 160 else self.description)
    
    def get_og_image(self):
        if self.og_image:
            return self.og_image.url
        elif self.image:
            return self.image.url
        return None

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Contact(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
    ]
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    description = RichTextField(help_text="Describe your inquiry or requirements")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Inquiry'
        verbose_name_plural = 'Contact Inquiries'
    
    @property
    def full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    def __str__(self):
        return f"{self.full_name} - {self.email}"

class PageContent(models.Model):
    PAGE_TYPE_CHOICES = [
        ('about_us', 'About Us'),
        ('terms_conditions', 'Terms & Conditions'),
        ('privacy_policy', 'Privacy Policy'),
        ('faq', 'FAQ'),
    ]
    
    page_type = models.CharField(max_length=20, choices=PAGE_TYPE_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    content = RichTextField(help_text="Main content for the page")
    # SEO Fields
    seo_title = models.CharField(max_length=70, blank=True, null=True, help_text="SEO Title (recommended: 50-60 characters)")
    seo_description = models.TextField(max_length=160, blank=True, null=True, help_text="SEO Meta Description (recommended: 150-160 characters)")
    seo_keywords = models.CharField(max_length=500, blank=True, null=True, help_text="SEO Keywords (comma-separated)")
    og_title = models.CharField(max_length=95, blank=True, null=True, help_text="Open Graph Title (recommended: 60-95 characters)")
    og_description = models.TextField(max_length=200, blank=True, null=True, help_text="Open Graph Description (recommended: 200 characters)")
    og_image = models.ImageField(upload_to='seo/og/', blank=True, null=True, help_text="Open Graph Image (1200x630px recommended)")
    twitter_card_type = models.CharField(
        max_length=20,
        choices=[('summary', 'Summary'), ('summary_large_image', 'Summary Large Image')],
        default='summary_large_image',
        help_text="Twitter Card Type"
    )
    twitter_title = models.CharField(max_length=70, blank=True, null=True, help_text="Twitter Card Title")
    twitter_description = models.TextField(max_length=200, blank=True, null=True, help_text="Twitter Card Description")
    twitter_image = models.ImageField(upload_to='seo/twitter/', blank=True, null=True, help_text="Twitter Card Image (1200x675px recommended)")
    status = models.BooleanField(default=True, help_text="Show/hide this page")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['page_type']
        verbose_name = 'Page Content'
        verbose_name_plural = 'Page Contents'
    
    def _strip_html(self, html_content):
        """Strip HTML tags from RichTextField content"""
        if not html_content:
            return ""
        text = strip_tags(html_content)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _generate_seo_title(self):
        """Generate SEO title from page title"""
        title = self.title
        if len(title) > 60:
            title = title[:57] + "..."
        return title
    
    def _generate_seo_description(self):
        """Generate SEO description from page content"""
        if not self.content:
            page_type_map = {
                'about_us': 'Learn about our company, mission, and values. Leading manufacturer of stainless steel hoses and pipe fittings.',
                'terms_conditions': 'Read our terms and conditions. Understand the legal terms for using our services and products.',
                'privacy_policy': 'Read our privacy policy. Learn how we collect, use, and protect your personal information.',
                'faq': 'Frequently asked questions about our products, services, and company. Find answers to common queries.',
            }
            return page_type_map.get(self.page_type, 'Quality stainless steel solutions for your industrial needs.')
        
        text = self._strip_html(self.content)
        
        if len(text) < 50:
            text = f"{text}. Quality stainless steel solutions for your industrial needs."
        
        if len(text) > 160:
            truncated = text[:157]
            last_space = truncated.rfind(' ')
            if last_space > 100:
                text = truncated[:last_space] + "..."
            else:
                text = truncated + "..."
        
        return text
    
    def _generate_seo_keywords(self):
        """Generate SEO keywords based on page type"""
        base_keywords = ['inox flex', 'stainless steel', 'industrial']
        
        page_type_keywords = {
            'about_us': ['about us', 'company', 'manufacturer', 'history'],
            'terms_conditions': ['terms', 'conditions', 'legal', 'agreement'],
            'privacy_policy': ['privacy', 'policy', 'data protection', 'security'],
            'faq': ['faq', 'questions', 'answers', 'help', 'support'],
        }
        
        keywords = base_keywords + page_type_keywords.get(self.page_type, [])
        keywords.append(self.title.lower())
        keywords.extend(self.title.lower().split())
        
        return ', '.join(list(dict.fromkeys(keywords))[:10])
    
    def save(self, *args, **kwargs):
        # Auto-generate SEO fields if blank
        if not self.seo_title:
            self.seo_title = self._generate_seo_title()
        
        if not self.seo_description:
            self.seo_description = self._generate_seo_description()
        
        if not self.seo_keywords:
            self.seo_keywords = self._generate_seo_keywords()
        
        # Auto-generate OG fields if blank
        if not self.og_title:
            self.og_title = self.get_seo_title()
        
        if not self.og_description:
            self.og_description = self.get_seo_description()
        
        # Auto-generate Twitter fields if blank
        if not self.twitter_title:
            self.twitter_title = self.get_seo_title()
        
        if not self.twitter_description:
            self.twitter_description = self.get_seo_description()
        
        super().save(*args, **kwargs)
    
    def get_seo_title(self):
        return self.seo_title or self.title
    
    def get_seo_description(self):
        if self.seo_description:
            return self.seo_description
        text = self._strip_html(self.content) if self.content else ""
        if len(text) > 160:
            return text[:157] + "..."
        return text or "Quality stainless steel solutions for your industrial needs."
    
    def get_og_title(self):
        return self.og_title or self.get_seo_title()
    
    def get_og_description(self):
        return self.og_description or self.get_seo_description()
    
    def get_og_image(self):
        return self.og_image.url if self.og_image else None
    
    def get_twitter_title(self):
        return self.twitter_title or self.get_seo_title()
    
    def get_twitter_description(self):
        return self.twitter_description or self.get_seo_description()
    
    def get_twitter_image(self):
        if self.twitter_image:
            return self.twitter_image.url
        elif self.og_image:
            return self.og_image.url
        return None
    
    def __str__(self):
        return f"{self.get_page_type_display()} - {self.title}"

class SiteSettings(models.Model):
    """
    Site-wide settings that can be managed from admin panel
    Only one instance should exist (singleton pattern)
    """
    phone_number = models.CharField(
        max_length=20, 
        default="+918750971212",
        help_text="Phone number for WhatsApp and contact (format: +918750971212)"
    )
    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="WhatsApp number (if different from phone number). Leave blank to use phone_number."
    )
    email = models.EmailField(
        default="info@inoxflex.co.in",
        help_text="Contact email address"
    )
    address = models.TextField(
        default="417/21, Nehru Park, Old DSP Street, Bahadurgarh",
        help_text="Office address"
    )
    # Social Media Links
    facebook_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Facebook page URL"
    )
    youtube_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="YouTube channel URL"
    )
    instagram_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Instagram profile URL"
    )
    twitter_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Twitter/X profile URL"
    )
    linkedin_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="LinkedIn profile URL"
    )
    # Default SEO Settings
    default_seo_title = models.CharField(
        max_length=70,
        default="Inox Flex - Stainless Steel Hoses & Pipe Fittings",
        help_text="Default SEO Title for pages without specific SEO (recommended: 50-60 characters)"
    )
    default_seo_description = models.TextField(
        max_length=160,
        default="Leading manufacturer and exporter of Stainless Steel Corrugated Hoses, Hose Assemblies, Metallic Bellows, Expansion Joints, and Pipe Fittings.",
        help_text="Default SEO Meta Description (recommended: 150-160 characters)"
    )
    default_seo_keywords = models.CharField(
        max_length=255,
        default="stainless steel hoses, pipe fittings, corrugated hoses, expansion joints, metallic bellows",
        help_text="Default SEO Keywords (comma-separated)"
    )
    site_name = models.CharField(
        max_length=100,
        default="Inox Flex",
        help_text="Site Name for Open Graph tags"
    )
    og_image_default = models.ImageField(
        upload_to='seo/og/',
        blank=True,
        null=True,
        help_text="Default Open Graph Image (1200x630px recommended)"
    )
    twitter_handle = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Twitter Handle (e.g., @inoxflex) - without @ symbol"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Prevent deletion
        pass
    
    @classmethod
    def load(cls):
        """Get or create the singleton instance"""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
    
    def get_whatsapp_number(self):
        """Returns WhatsApp number or phone number if WhatsApp number is not set"""
        return self.whatsapp_number or self.phone_number
    
    def get_whatsapp_url_number(self):
        """Returns WhatsApp number formatted for URL (without + and spaces)"""
        number = self.get_whatsapp_number()
        # Remove + and spaces
        return number.replace('+', '').replace(' ', '').replace('-', '')
    
    def __str__(self):
        return "Site Settings"

class TeamMember(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=100, help_text="e.g., Founder & Director, CEO")
    description = models.TextField(
        help_text="Brief description about the team member"
    )
    # Social Media Links
    facebook_url = models.URLField(max_length=500, blank=True, null=True, help_text="Facebook profile URL")
    twitter_url = models.URLField(max_length=500, blank=True, null=True, help_text="Twitter/X profile URL")
    linkedin_url = models.URLField(max_length=500, blank=True, null=True, help_text="LinkedIn profile URL")
    instagram_url = models.URLField(max_length=500, blank=True, null=True, help_text="Instagram profile URL")
    order = models.IntegerField(
        default=0,
        help_text="Display order (lower numbers appear first)"
    )
    status = models.BooleanField(default=True, help_text="Show/hide this team member")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'first_name']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'
    
    @property
    def full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    def get_initials(self):
        """Returns initials from first and last name"""
        initials = self.first_name[0].upper() if self.first_name else ''
        if self.last_name:
            initials += self.last_name[0].upper()
        else:
            # If no last name, use second character of first name if available
            if len(self.first_name) > 1:
                initials += self.first_name[1].upper()
        return initials[:2]  # Return max 2 characters
    
    def __str__(self):
        return f"{self.full_name} - {self.role}"