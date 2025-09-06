from django.db import models
from django.utils.translation import gettext_lazy as _


class SEOPage(models.Model):
    """صفحات سئو"""
    
    PAGE_TYPES = [
        ('home', 'صفحه اصلی'),
        ('category', 'دسته‌بندی'),
        ('product', 'محصول'),
        ('blog', 'وبلاگ'),
        ('static', 'صفحه استاتیک'),
    ]
    
    page_type = models.CharField(
        max_length=20,
        choices=PAGE_TYPES,
        verbose_name='نوع صفحه'
    )
    page_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='شناسه صفحه'
    )
    title = models.CharField(max_length=200, verbose_name='عنوان')
    meta_description = models.TextField(verbose_name='توضیحات متا')
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='کلمات کلیدی'
    )
    canonical_url = models.URLField(
        blank=True,
        verbose_name='آدرس کانونیکال'
    )
    robots_meta = models.CharField(
        max_length=100,
        default='index, follow',
        verbose_name='متای ربات‌ها'
    )
    
    # Open Graph
    og_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='عنوان Open Graph'
    )
    og_description = models.TextField(
        blank=True,
        verbose_name='توضیحات Open Graph'
    )
    og_image = models.ImageField(
        upload_to='seo/og/',
        null=True,
        blank=True,
        verbose_name='تصویر Open Graph'
    )
    
    # Twitter Card
    twitter_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='عنوان Twitter'
    )
    twitter_description = models.TextField(
        blank=True,
        verbose_name='توضیحات Twitter'
    )
    twitter_image = models.ImageField(
        upload_to='seo/twitter/',
        null=True,
        blank=True,
        verbose_name='تصویر Twitter'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'صفحه سئو'
        verbose_name_plural = 'صفحات سئو'
        unique_together = ['page_type', 'page_id']
    
    def __str__(self):
        return f'{self.get_page_type_display()} - {self.title}'


class SchemaMarkup(models.Model):
    """اسکیما مارک‌آپ"""
    
    SCHEMA_TYPES = [
        ('Product', 'محصول'),
        ('Organization', 'سازمان'),
        ('BreadcrumbList', 'لیست مسیر'),
        ('Article', 'مقاله'),
        ('Review', 'نظر'),
        ('FAQ', 'سوالات متداول'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='نام')
    schema_type = models.CharField(
        max_length=50,
        choices=SCHEMA_TYPES,
        verbose_name='نوع اسکیما'
    )
    page_type = models.CharField(
        max_length=20,
        choices=SEOPage.PAGE_TYPES,
        verbose_name='نوع صفحه'
    )
    page_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='شناسه صفحه'
    )
    markup = models.JSONField(verbose_name='مارک‌آپ')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'اسکیما مارک‌آپ'
        verbose_name_plural = 'اسکیما مارک‌آپ‌ها'
        unique_together = ['schema_type', 'page_type', 'page_id']
    
    def __str__(self):
        return f'{self.schema_type} - {self.name}'