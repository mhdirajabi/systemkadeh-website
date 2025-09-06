from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.sessions.models import Session
from apps.catalog.models import Product, ProductVariant


class Cart(models.Model):
    """سبد خرید"""
    
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='جلسه'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='کاربر'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید'
        unique_together = ['session', 'user']
    
    def __str__(self):
        if self.user:
            return f'سبد خرید {self.user.full_name}'
        return f'سبد خرید جلسه {self.session.session_key}'
    
    @property
    def total_items(self):
        """تعداد کل آیتم‌ها"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """مجموع قیمت"""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def is_empty(self):
        """بررسی خالی بودن سبد"""
        return not self.items.exists()


class CartItem(models.Model):
    """آیتم‌های سبد خرید"""
    
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سبد خرید'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='محصول'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='تنوع'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='تعداد'
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='قیمت'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'آیتم سبد خرید'
        verbose_name_plural = 'آیتم‌های سبد خرید'
        unique_together = ['cart', 'product', 'variant']
        ordering = ['created_at']
    
    def __str__(self):
        variant_text = f' - {self.variant.name}' if self.variant else ''
        return f'{self.product.name}{variant_text} x {self.quantity}'
    
    @property
    def total_price(self):
        """قیمت کل آیتم"""
        return self.price * self.quantity
    
    @property
    def display_name(self):
        """نام نمایشی"""
        if self.variant:
            return f'{self.product.name} - {self.variant.name}'
        return self.product.name
    
    def save(self, *args, **kwargs):
        # تنظیم قیمت بر اساس تنوع یا محصول
        if self.variant and self.variant.price:
            self.price = self.variant.price
        else:
            self.price = self.product.price
        super().save(*args, **kwargs)


class Coupon(models.Model):
    """کوپن‌های تخفیف"""
    
    COUPON_TYPES = [
        ('percentage', 'درصدی'),
        ('fixed', 'مبلغ ثابت'),
        ('free_shipping', 'ارسال رایگان'),
    ]
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='کد کوپن'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='نام کوپن'
    )
    description = models.TextField(
        blank=True,
        verbose_name='توضیحات'
    )
    coupon_type = models.CharField(
        max_length=20,
        choices=COUPON_TYPES,
        verbose_name='نوع کوپن'
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
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    valid_from = models.DateTimeField(
        verbose_name='اعتبار از'
    )
    valid_until = models.DateTimeField(
        verbose_name='اعتبار تا'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'کوپن تخفیف'
        verbose_name_plural = 'کوپن‌های تخفیف'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} ({self.code})'
    
    @property
    def is_valid(self):
        """بررسی اعتبار کوپن"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if now < self.valid_from or now > self.valid_until:
            return False
        
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        
        return True
    
    def can_use(self, user, cart_total):
        """بررسی امکان استفاده از کوپن"""
        if not self.is_valid:
            return False, 'کوپن معتبر نیست'
        
        if self.minimum_amount and cart_total < self.minimum_amount:
            return False, f'حداقل مبلغ خرید {self.minimum_amount} تومان است'
        
        # بررسی استفاده قبلی کاربر (اختیاری)
        # if CouponUsage.objects.filter(coupon=self, user=user).exists():
        #     return False, 'شما قبلاً از این کوپن استفاده کرده‌اید'
        
        return True, 'کوپن قابل استفاده است'
    
    def calculate_discount(self, cart_total):
        """محاسبه تخفیف"""
        if self.coupon_type == 'percentage':
            discount = (cart_total * self.value) / 100
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
        elif self.coupon_type == 'fixed':
            discount = min(self.value, cart_total)
        else:  # free_shipping
            discount = 0
        
        return discount


class CouponUsage(models.Model):
    """استفاده از کوپن‌ها"""
    
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='usages',
        verbose_name='کوپن'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='coupon_usages',
        verbose_name='کاربر'
    )
    order = models.ForeignKey(
        'checkout.Order',
        on_delete=models.CASCADE,
        related_name='coupon_usages',
        verbose_name='سفارش'
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='مبلغ تخفیف'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'استفاده از کوپن'
        verbose_name_plural = 'استفاده‌های کوپن'
        unique_together = ['coupon', 'order']
    
    def __str__(self):
        return f'{self.coupon.code} - {self.user.full_name}'