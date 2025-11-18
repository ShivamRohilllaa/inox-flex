from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from ckeditor.fields import RichTextField

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, null=True)
    description = RichTextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, null=True)
    description = RichTextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Alternative: Use image URL instead of uploading")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_image(self):
        """Returns image URL - prioritizes uploaded image, then image_url, then default"""
        if self.image:
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

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
    meta_description = models.TextField(max_length=300, blank=True, null=True, help_text="SEO meta description")
    meta_keywords = models.CharField(max_length=500, blank=True, null=True, help_text="SEO meta keywords")
    status = models.BooleanField(default=True, help_text="Show/hide this page")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['page_type']
        verbose_name = 'Page Content'
        verbose_name_plural = 'Page Contents'
    
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
        default="inoxflex10@gmail.com",
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