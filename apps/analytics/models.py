from django.db import models


class PageView(models.Model):
    """ثبت بازدید صفحات برای KPI: Page Views و Unique Visitors"""
    
    session_key = models.CharField(max_length=40, db_index=True)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pageviews'
    )
    path = models.CharField(max_length=512, db_index=True)
    method = models.CharField(max_length=8, default='GET')
    referrer = models.CharField(max_length=512, blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    status_code = models.PositiveIntegerField(default=200)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = 'بازدید صفحه'
        verbose_name_plural = 'بازدید صفحات'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['path', 'created_at']),
        ]


class SalesAggregate(models.Model):
    """تجمیع فروش برای بازه‌های روزانه/هفتگی/ماهانه/سالانه"""
    
    PERIOD_CHOICES = [
        ('day', 'روزانه'),
        ('week', 'هفتگی'),
        ('month', 'ماهانه'),
        ('year', 'سالانه'),
    ]
    
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    orders_count = models.PositiveIntegerField(default=0)
    items_count = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    refunds = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'تجمیع فروش'
        verbose_name_plural = 'تجمیع‌های فروش'
        unique_together = ['period', 'period_start', 'period_end']
        indexes = [
            models.Index(fields=['period', 'period_start']),
        ]


class KPIRecord(models.Model):
    """ثبت KPI های کلیدی برای داشبورد مدیریتی"""
    
    name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=16, decimal_places=2)
    label = models.CharField(max_length=100, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = 'شاخص کلیدی عملکرد'
        verbose_name_plural = 'شاخص‌های کلیدی عملکرد'
