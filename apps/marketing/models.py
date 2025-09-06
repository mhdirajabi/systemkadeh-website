from django.db import models
from django.utils.translation import gettext_lazy as _


class Campaign(models.Model):
    """کمپین‌های بازاریابی"""
    
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('active', 'فعال'),
        ('paused', 'متوقف'),
        ('completed', 'تکمیل شده'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='نام کمپین')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='وضعیت'
    )
    start_date = models.DateTimeField(verbose_name='تاریخ شروع')
    end_date = models.DateTimeField(verbose_name='تاریخ پایان')
    
    # Targeting
    target_audience = models.JSONField(
        default=dict,
        verbose_name='مخاطبان هدف'
    )
    
    # Statistics
    total_views = models.PositiveIntegerField(default=0, verbose_name='تعداد کل بازدیدها')
    total_clicks = models.PositiveIntegerField(default=0, verbose_name='تعداد کل کلیک‌ها')
    total_conversions = models.PositiveIntegerField(default=0, verbose_name='تعداد کل تبدیل‌ها')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'کمپین بازاریابی'
        verbose_name_plural = 'کمپین‌های بازاریابی'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Discount(models.Model):
    """تخفیف‌های ویژه"""
    
    DISCOUNT_TYPES = [
        ('percentage', 'درصدی'),
        ('fixed', 'مبلغ ثابت'),
        ('buy_x_get_y', 'خرید X دریافت Y'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='نام تخفیف')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPES,
        verbose_name='نوع تخفیف'
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='مقدار تخفیف'
    )
    minimum_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='حداقل مبلغ خرید'
    )
    maximum_discount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='حداکثر تخفیف'
    )
    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='حد استفاده'
    )
    used_count = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد استفاده شده'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    valid_from = models.DateTimeField(verbose_name='اعتبار از')
    valid_until = models.DateTimeField(verbose_name='اعتبار تا')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'تخفیف ویژه'
        verbose_name_plural = 'تخفیف‌های ویژه'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name