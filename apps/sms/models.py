from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class SMSProvider(models.Model):
    """ارائه‌دهندگان پیامک"""
    
    name = models.CharField(max_length=100, verbose_name='نام')
    api_key = models.CharField(max_length=200, verbose_name='کلید API')
    api_url = models.URLField(verbose_name='آدرس API')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    priority = models.PositiveIntegerField(default=1, verbose_name='اولویت')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'ارائه‌دهنده پیامک'
        verbose_name_plural = 'ارائه‌دهندگان پیامک'
        ordering = ['priority', 'name']
    
    def __str__(self):
        return self.name


class SMSLog(models.Model):
    """لاگ پیامک‌ها"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('sent', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('failed', 'ناموفق'),
    ]
    
    phone = PhoneNumberField(verbose_name='شماره موبایل')
    message = models.TextField(verbose_name='پیام')
    provider = models.ForeignKey(
        SMSProvider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='ارائه‌دهنده'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    response = models.TextField(
        blank=True,
        verbose_name='پاسخ API'
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='هزینه'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'لاگ پیامک'
        verbose_name_plural = 'لاگ پیامک‌ها'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.phone} - {self.status}'


class SMSTemplate(models.Model):
    """قالب‌های پیامک"""
    
    TEMPLATE_TYPES = [
        ('otp', 'کد یکبارمصرف'),
        ('welcome', 'خوش‌آمدگویی'),
        ('order_confirmation', 'تأیید سفارش'),
        ('order_shipped', 'ارسال سفارش'),
        ('order_delivered', 'تحویل سفارش'),
        ('marketing', 'تبلیغاتی'),
        ('reminder', 'یادآوری'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='نام')
    template_type = models.CharField(
        max_length=30,
        choices=TEMPLATE_TYPES,
        verbose_name='نوع قالب'
    )
    content = models.TextField(verbose_name='محتوای پیام')
    variables = models.JSONField(
        default=list,
        blank=True,
        verbose_name='متغیرها'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'قالب پیامک'
        verbose_name_plural = 'قالب‌های پیامک'
    
    def __str__(self):
        return self.name


class MarketingCampaign(models.Model):
    """کمپین‌های بازاریابی پیامکی"""
    
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('scheduled', 'زمان‌بندی شده'),
        ('running', 'در حال اجرا'),
        ('completed', 'تکمیل شده'),
        ('cancelled', 'لغو شده'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='نام کمپین')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    template = models.ForeignKey(
        SMSTemplate,
        on_delete=models.CASCADE,
        verbose_name='قالب پیام'
    )
    target_audience = models.JSONField(
        default=dict,
        verbose_name='مخاطبان هدف'
    )
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='زمان ارسال'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='وضعیت'
    )
    total_recipients = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد کل مخاطبان'
    )
    sent_count = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد ارسال شده'
    )
    delivered_count = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد تحویل داده شده'
    )
    failed_count = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد ناموفق'
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='هزینه کل'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'کمپین بازاریابی'
        verbose_name_plural = 'کمپین‌های بازاریابی'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name