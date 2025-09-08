from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteSettings(models.Model):
    """تنظیمات کلی سایت سیستمکده"""
    
    site_name = models.CharField(
        max_length=100,
        default='سیستمکده',
        verbose_name='نام سایت'
    )
    site_description = models.TextField(
        default='فروشگاه تخصصی لوازم صوتی، تصویری، مانیتور اندروید و تجهیزات امنیتی خودرو',
        verbose_name='توضیحات سایت'
    )
    site_keywords = models.TextField(
        default='سیستم صوتی خودرو، مانیتور اندروید، تجهیزات امنیتی، سیستمکده',
        verbose_name='کلمات کلیدی'
    )
    logo = models.ImageField(
        upload_to='site/',
        null=True,
        blank=True,
        verbose_name='لوگو'
    )
    favicon = models.ImageField(
        upload_to='site/',
        null=True,
        blank=True,
        verbose_name='فاویکون'
    )
    phone = models.CharField(
        max_length=20,
        default='021-12345678',
        verbose_name='تلفن تماس'
    )
    email = models.EmailField(
        default='info@systemkadeh.com',
        verbose_name='ایمیل'
    )
    address = models.TextField(
        default='تهران، ایران',
        verbose_name='آدرس'
    )
    instagram = models.URLField(
        blank=True,
        verbose_name='اینستاگرام'
    )
    telegram = models.URLField(
        blank=True,
        verbose_name='تلگرام'
    )
    whatsapp = models.URLField(
        blank=True,
        verbose_name='واتساپ'
    )
    
    # SEO Settings
    google_analytics = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='کد گوگل آنالیتیکس'
    )
    google_tag_manager = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='کد گوگل تگ منیجر'
    )
    
    # Business Settings
    currency = models.CharField(
        max_length=10,
        default='تومان',
        verbose_name='واحد پول'
    )
    currency_symbol = models.CharField(
        max_length=5,
        default='تومان',
        verbose_name='نماد پول'
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=50000,
        verbose_name='هزینه ارسال'
    )
    free_shipping_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=500000,
        verbose_name='حداقل خرید برای ارسال رایگان'
    )
    
    # Live Chat Settings
    chat_provider = models.CharField(
        max_length=50,
        choices=[('none', 'خاموش'), ('goftino', 'گفتینو'), ('mochat', 'موچت'), ('tawk', 'Tawk.to')],
        default='none',
        verbose_name='ارائه‌دهنده چت آنلاین'
    )
    chat_site_token = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='توکن/شناسه سایت چت'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'تنظیمات سایت'
        verbose_name_plural = 'تنظیمات سایت'
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            # Only allow one instance
            return
        super().save(*args, **kwargs)


class Banner(models.Model):
    """بنرهای تبلیغاتی"""
    
    BANNER_TYPES = [
        ('home', 'صفحه اصلی'),
        ('category', 'دسته‌بندی'),
        ('product', 'محصول'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    subtitle = models.CharField(max_length=300, blank=True, verbose_name='زیرعنوان')
    image = models.ImageField(upload_to='banners/', verbose_name='تصویر')
    link = models.URLField(blank=True, verbose_name='لینک')
    banner_type = models.CharField(
        max_length=20,
        choices=BANNER_TYPES,
        default='home',
        verbose_name='نوع بنر'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'بنر'
        verbose_name_plural = 'بنرها'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    """پیام‌های تماس با ما"""
    
    STATUS_CHOICES = [
        ('new', 'جدید'),
        ('read', 'خوانده شده'),
        ('replied', 'پاسخ داده شده'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='نام')
    email = models.EmailField(verbose_name='ایمیل')
    phone = models.CharField(max_length=20, verbose_name='تلفن')
    subject = models.CharField(max_length=200, verbose_name='موضوع')
    message = models.TextField(verbose_name='پیام')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='وضعیت'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'پیام تماس'
        verbose_name_plural = 'پیام‌های تماس'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} - {self.subject}'


class Newsletter(models.Model):
    """عضویت در خبرنامه"""
    
    email = models.EmailField(unique=True, verbose_name='ایمیل')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'عضویت خبرنامه'
        verbose_name_plural = 'عضویت‌های خبرنامه'
    
    def __str__(self):
        return self.email