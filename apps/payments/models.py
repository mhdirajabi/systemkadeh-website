from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid


class PaymentProvider(models.Model):
    """ارائه‌دهندگان پرداخت"""
    
    PROVIDER_TYPES = [
        ('gateway', 'درگاه پرداخت'),
        ('installment', 'پرداخت اقساطی'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='نام')
    slug = models.SlugField(unique=True, verbose_name='نامک')
    provider_type = models.CharField(
        max_length=20,
        choices=PROVIDER_TYPES,
        verbose_name='نوع ارائه‌دهنده'
    )
    description = models.TextField(blank=True, verbose_name='توضیحات')
    logo = models.ImageField(
        upload_to='payment_providers/',
        null=True,
        blank=True,
        verbose_name='لوگو'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    # Configuration
    config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='تنظیمات'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'ارائه‌دهنده پرداخت'
        verbose_name_plural = 'ارائه‌دهندگان پرداخت'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Payment(models.Model):
    """پرداخت‌ها"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('processing', 'در حال پردازش'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
        ('refunded', 'مرجوع شده'),
    ]
    
    PAYMENT_TYPES = [
        ('online', 'آنلاین'),
        ('installment', 'اقساطی'),
        ('cash_on_delivery', 'پرداخت در محل'),
    ]
    
    # Basic Information
    payment_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        verbose_name='شناسه پرداخت'
    )
    order = models.ForeignKey(
        'checkout.Order',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='سفارش'
    )
    provider = models.ForeignKey(
        PaymentProvider,
        on_delete=models.CASCADE,
        verbose_name='ارائه‌دهنده'
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPES,
        default='online',
        verbose_name='نوع پرداخت'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    
    # Amount Information
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='مبلغ'
    )
    currency = models.CharField(
        max_length=10,
        default='IRR',
        verbose_name='واحد پول'
    )
    
    # Provider Information
    provider_transaction_id = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='شناسه تراکنش ارائه‌دهنده'
    )
    provider_response = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='پاسخ ارائه‌دهنده'
    )
    
    # Additional Information
    description = models.TextField(
        blank=True,
        verbose_name='توضیحات'
    )
    failure_reason = models.TextField(
        blank=True,
        verbose_name='دلیل عدم موفقیت'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت‌ها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_id']),
            models.Index(fields=['order', 'status']),
            models.Index(fields=['provider_transaction_id']),
        ]
    
    def __str__(self):
        return f'پرداخت {self.payment_id} - {self.order.order_number}'
    
    @property
    def is_successful(self):
        """بررسی موفقیت پرداخت"""
        return self.status == 'completed'
    
    @property
    def is_pending(self):
        """بررسی در انتظار بودن"""
        return self.status == 'pending'


class InstallmentPlan(models.Model):
    """طرح‌های اقساطی"""
    
    name = models.CharField(max_length=200, verbose_name='نام')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    provider = models.ForeignKey(
        PaymentProvider,
        on_delete=models.CASCADE,
        related_name='installment_plans',
        verbose_name='ارائه‌دهنده'
    )
    
    # Plan Configuration
    min_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='حداقل مبلغ'
    )
    max_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='حداکثر مبلغ'
    )
    installment_count = models.PositiveIntegerField(
        verbose_name='تعداد اقساط'
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='نرخ سود (درصد)'
    )
    
    # Eligibility
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    eligible_categories = models.ManyToManyField(
        'catalog.Category',
        blank=True,
        verbose_name='دسته‌بندی‌های مجاز'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'طرح اقساطی'
        verbose_name_plural = 'طرح‌های اقساطی'
        ordering = ['name']
    
    def __str__(self):
        return f'{self.name} - {self.installment_count} قسط'
    
    def calculate_monthly_payment(self, amount):
        """محاسبه قسط ماهانه"""
        if self.interest_rate == 0:
            return amount / self.installment_count
        
        # محاسبه با سود مرکب
        monthly_rate = self.interest_rate / 100 / 12
        monthly_payment = amount * (monthly_rate * (1 + monthly_rate) ** self.installment_count) / \
                         ((1 + monthly_rate) ** self.installment_count - 1)
        return monthly_payment
    
    def is_eligible(self, amount, category=None):
        """بررسی واجد شرایط بودن"""
        if not self.is_active:
            return False
        
        if amount < self.min_amount:
            return False
        
        if self.max_amount and amount > self.max_amount:
            return False
        
        if category and self.eligible_categories.exists():
            return self.eligible_categories.filter(id=category.id).exists()
        
        return True


class InstallmentPayment(models.Model):
    """پرداخت‌های اقساطی"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('paid', 'پرداخت شده'),
        ('overdue', 'سررسید گذشته'),
        ('cancelled', 'لغو شده'),
    ]
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='installments',
        verbose_name='پرداخت'
    )
    plan = models.ForeignKey(
        InstallmentPlan,
        on_delete=models.CASCADE,
        verbose_name='طرح اقساطی'
    )
    installment_number = models.PositiveIntegerField(verbose_name='شماره قسط')
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='مبلغ قسط'
    )
    due_date = models.DateField(verbose_name='تاریخ سررسید')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پرداخت')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'قسط'
        verbose_name_plural = 'اقساط'
        ordering = ['installment_number']
        unique_together = ['payment', 'installment_number']
    
    def __str__(self):
        return f'قسط {self.installment_number} - {self.payment.order.order_number}'
    
    @property
    def is_overdue(self):
        """بررسی سررسید گذشته"""
        return self.due_date < timezone.now().date() and self.status == 'pending'


class PaymentRefund(models.Model):
    """مرجوعی پرداخت‌ها"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('approved', 'تأیید شده'),
        ('rejected', 'رد شده'),
        ('completed', 'تکمیل شده'),
    ]
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refunds',
        verbose_name='پرداخت'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='مبلغ مرجوعی'
    )
    reason = models.TextField(verbose_name='دلیل مرجوعی')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    provider_refund_id = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='شناسه مرجوعی ارائه‌دهنده'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='یادداشت‌ها'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'مرجوعی پرداخت'
        verbose_name_plural = 'مرجوعی‌های پرداخت'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'مرجوعی {self.payment.order.order_number} - {self.amount}'