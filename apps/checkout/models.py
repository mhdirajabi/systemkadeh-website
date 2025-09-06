from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid


class Order(models.Model):
    """سفارشات"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('confirmed', 'تأیید شده'),
        ('processing', 'در حال پردازش'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
        ('refunded', 'مرجوع شده'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('failed', 'پرداخت ناموفق'),
        ('refunded', 'مرجوع شده'),
    ]
    
    # Basic Information
    order_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='شماره سفارش'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='کاربر'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت پرداخت'
    )
    
    # Pricing
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='مجموع'
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name='هزینه ارسال'
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name='مبلغ تخفیف'
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='مبلغ کل'
    )
    
    # Shipping Information
    shipping_name = models.CharField(
        max_length=200,
        verbose_name='نام گیرنده'
    )
    shipping_phone = models.CharField(
        max_length=20,
        verbose_name='تلفن گیرنده'
    )
    shipping_address = models.TextField(verbose_name='آدرس ارسال')
    shipping_city = models.CharField(
        max_length=100,
        verbose_name='شهر'
    )
    shipping_province = models.CharField(
        max_length=100,
        verbose_name='استان'
    )
    shipping_postal_code = models.CharField(
        max_length=10,
        verbose_name='کد پستی'
    )
    
    # Additional Information
    notes = models.TextField(
        blank=True,
        verbose_name='یادداشت'
    )
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='شماره پیگیری'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f'سفارش {self.order_number}'
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """تولید شماره سفارش"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        return f'ORD{timestamp}'
    
    @property
    def is_paid(self):
        """بررسی پرداخت شده بودن"""
        return self.payment_status == 'paid'
    
    @property
    def can_cancel(self):
        """بررسی امکان لغو"""
        return self.status in ['pending', 'confirmed']
    
    @property
    def can_refund(self):
        """بررسی امکان مرجوع"""
        return self.status in ['delivered'] and self.payment_status == 'paid'


class OrderItem(models.Model):
    """آیتم‌های سفارش"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سفارش'
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        verbose_name='محصول'
    )
    variant = models.ForeignKey(
        'catalog.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='تنوع'
    )
    quantity = models.PositiveIntegerField(verbose_name='تعداد')
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='قیمت'
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='قیمت کل'
    )
    
    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'
        unique_together = ['order', 'product', 'variant']
    
    def __str__(self):
        variant_text = f' - {self.variant.name}' if self.variant else ''
        return f'{self.product.name}{variant_text} x {self.quantity}'
    
    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)
    
    @property
    def display_name(self):
        """نام نمایشی"""
        if self.variant:
            return f'{self.product.name} - {self.variant.name}'
        return self.product.name


class ShippingMethod(models.Model):
    """روش‌های ارسال"""
    
    name = models.CharField(max_length=100, verbose_name='نام')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='هزینه'
    )
    free_shipping_threshold = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='حداقل خرید برای ارسال رایگان'
    )
    estimated_days = models.PositiveIntegerField(
        default=1,
        verbose_name='تخمین روزهای ارسال'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'روش ارسال'
        verbose_name_plural = 'روش‌های ارسال'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def calculate_cost(self, order_total):
        """محاسبه هزینه ارسال"""
        if self.free_shipping_threshold and order_total >= self.free_shipping_threshold:
            return 0
        return self.cost


class OrderStatusHistory(models.Model):
    """تاریخچه وضعیت سفارش"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name='سفارش'
    )
    status = models.CharField(
        max_length=20,
        choices=Order.STATUS_CHOICES,
        verbose_name='وضعیت'
    )
    note = models.TextField(
        blank=True,
        verbose_name='یادداشت'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'تاریخچه وضعیت'
        verbose_name_plural = 'تاریخچه وضعیت‌ها'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.order.order_number} - {self.get_status_display()}'


class OrderNote(models.Model):
    """یادداشت‌های سفارش"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name='سفارش'
    )
    note = models.TextField(verbose_name='یادداشت')
    is_public = models.BooleanField(
        default=False,
        verbose_name='عمومی'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'یادداشت سفارش'
        verbose_name_plural = 'یادداشت‌های سفارش'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.order.order_number} - {self.note[:50]}'