from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Category(MPTTModel):
    """دسته‌بندی محصولات"""
    
    name = models.CharField(max_length=200, verbose_name='نام')
    slug = models.SlugField(unique=True, verbose_name='نامک')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True,
        verbose_name='تصویر'
    )
    icon = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='آیکون'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_featured = models.BooleanField(default=False, verbose_name='ویژه')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    # SEO Fields
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='عنوان سئو'
    )
    meta_description = models.TextField(
        blank=True,
        verbose_name='توضیحات سئو'
    )
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='کلمات کلیدی سئو'
    )
    
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='دسته‌بندی والد'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class MPTTMeta:
        order_insertion_by = ['order', 'name']
    
    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})
    
    @property
    def full_path(self):
        """مسیر کامل دسته‌بندی"""
        return ' > '.join([cat.name for cat in self.get_ancestors(include_self=True)])


class Brand(models.Model):
    """برند محصولات"""
    
    name = models.CharField(max_length=100, unique=True, verbose_name='نام')
    slug = models.SlugField(unique=True, verbose_name='نامک')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    logo = models.ImageField(
        upload_to='brands/',
        null=True,
        blank=True,
        verbose_name='لوگو'
    )
    website = models.URLField(blank=True, verbose_name='وب‌سایت')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برندها'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('catalog:brand_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    """محصولات"""
    
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('active', 'فعال'),
        ('inactive', 'غیرفعال'),
        ('discontinued', 'متوقف شده'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=300, verbose_name='نام')
    slug = models.SlugField(unique=True, verbose_name='نامک')
    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='کد محصول'
    )
    description = models.TextField(verbose_name='توضیحات')
    short_description = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='توضیحات کوتاه'
    )
    
    # Categorization
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='دسته‌بندی'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='برند'
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='قیمت'
    )
    compare_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='قیمت مقایسه'
    )
    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='قیمت تمام شده'
    )
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='موجودی'
    )
    low_stock_threshold = models.PositiveIntegerField(
        default=5,
        verbose_name='حداقل موجودی'
    )
    track_inventory = models.BooleanField(
        default=True,
        verbose_name='ردیابی موجودی'
    )
    allow_backorder = models.BooleanField(
        default=False,
        verbose_name='پیش‌سفارش'
    )
    
    # Status and Visibility
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='وضعیت'
    )
    is_featured = models.BooleanField(default=False, verbose_name='ویژه')
    is_digital = models.BooleanField(default=False, verbose_name='دیجیتال')
    requires_shipping = models.BooleanField(default=True, verbose_name='نیاز به ارسال')
    
    # Physical Properties
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='وزن (گرم)'
    )
    length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='طول (سانتی‌متر)'
    )
    width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='عرض (سانتی‌متر)'
    )
    height = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='ارتفاع (سانتی‌متر)'
    )
    
    # SEO Fields
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='عنوان سئو'
    )
    meta_description = models.TextField(
        blank=True,
        verbose_name='توضیحات سئو'
    )
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='کلمات کلیدی سئو'
    )
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    sale_count = models.PositiveIntegerField(default=0, verbose_name='تعداد فروش')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_featured']),
            models.Index(fields=['category', 'brand']),
            models.Index(fields=['price']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})
    
    @property
    def is_in_stock(self):
        """بررسی موجودی"""
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self):
        """بررسی کمبود موجودی"""
        if not self.track_inventory:
            return False
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def discount_percentage(self):
        """درصد تخفیف"""
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0
    
    @property
    def average_rating(self):
        """میانگین امتیاز"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    
    @property
    def review_count(self):
        """تعداد نظرات"""
        return self.reviews.filter(is_approved=True).count()


class ProductImage(models.Model):
    """تصاویر محصول"""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='محصول'
    )
    image = models.ImageField(
        upload_to='products/',
        verbose_name='تصویر'
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='متن جایگزین'
    )
    is_primary = models.BooleanField(default=False, verbose_name='تصویر اصلی')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصولات'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f'{self.product.name} - تصویر {self.order}'


class ProductAttribute(models.Model):
    """ویژگی‌های محصول"""
    
    name = models.CharField(max_length=100, verbose_name='نام')
    slug = models.SlugField(unique=True, verbose_name='نامک')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    is_required = models.BooleanField(default=False, verbose_name='اجباری')
    is_filterable = models.BooleanField(default=False, verbose_name='قابل فیلتر')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'ویژگی محصول'
        verbose_name_plural = 'ویژگی‌های محصولات'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    """مقادیر ویژگی‌های محصول"""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attribute_values',
        verbose_name='محصول'
    )
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name='ویژگی'
    )
    value = models.CharField(max_length=500, verbose_name='مقدار')
    
    class Meta:
        verbose_name = 'مقدار ویژگی محصول'
        verbose_name_plural = 'مقادیر ویژگی‌های محصولات'
        unique_together = ['product', 'attribute']
    
    def __str__(self):
        return f'{self.product.name} - {self.attribute.name}: {self.value}'


class ProductReview(models.Model):
    """نظرات محصولات"""
    
    RATING_CHOICES = [
        (1, 'خیلی بد'),
        (2, 'بد'),
        (3, 'متوسط'),
        (4, 'خوب'),
        (5, 'عالی'),
    ]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='محصول'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='کاربر'
    )
    rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        verbose_name='امتیاز'
    )
    title = models.CharField(max_length=200, verbose_name='عنوان')
    comment = models.TextField(verbose_name='نظر')
    is_approved = models.BooleanField(default=False, verbose_name='تأیید شده')
    is_verified_purchase = models.BooleanField(default=False, verbose_name='خرید تأیید شده')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'نظر محصول'
        verbose_name_plural = 'نظرات محصولات'
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f'{self.product.name} - {self.user.full_name}'


class ProductVariant(models.Model):
    """تنوع محصولات (رنگ، سایز و غیره)"""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name='محصول'
    )
    name = models.CharField(max_length=200, verbose_name='نام')
    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='کد تنوع'
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='قیمت'
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='موجودی'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'تنوع محصول'
        verbose_name_plural = 'تنوع‌های محصولات'
        ordering = ['name']
    
    def __str__(self):
        return f'{self.product.name} - {self.name}'


class Wishlist(models.Model):
    """لیست علاقه‌مندی‌ها"""
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='wishlist',
        verbose_name='کاربر'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wishlist',
        verbose_name='محصول'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'لیست علاقه‌مندی'
        verbose_name_plural = 'لیست‌های علاقه‌مندی'
        unique_together = ['user', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.full_name} - {self.product.name}'