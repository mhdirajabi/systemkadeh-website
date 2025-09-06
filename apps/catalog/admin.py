from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Brand, Product, ProductImage, ProductAttribute,
    ProductAttributeValue, ProductReview, ProductVariant, Wishlist
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'is_featured', 'order', 'product_count']
    list_filter = ['is_active', 'is_featured', 'parent']
    list_editable = ['is_active', 'is_featured', 'order']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'تعداد محصولات'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'order', 'product_count']
    list_filter = ['is_active']
    list_editable = ['is_active', 'order']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'تعداد محصولات'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1
    fields = ['attribute', 'value']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['name', 'sku', 'price', 'stock_quantity', 'is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category', 'brand', 'price', 'stock_quantity',
        'status', 'is_featured', 'view_count', 'sale_count'
    ]
    list_filter = ['status', 'is_featured', 'category', 'brand', 'created_at']
    list_editable = ['status', 'is_featured', 'price', 'stock_quantity']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductAttributeValueInline, ProductVariantInline]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'slug', 'sku', 'description', 'short_description')
        }),
        ('دسته‌بندی', {
            'fields': ('category', 'brand')
        }),
        ('قیمت‌گذاری', {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        ('موجودی', {
            'fields': ('stock_quantity', 'low_stock_threshold', 'track_inventory', 'allow_backorder')
        }),
        ('وضعیت و نمایش', {
            'fields': ('status', 'is_featured', 'is_digital', 'requires_shipping')
        }),
        ('ویژگی‌های فیزیکی', {
            'fields': ('weight', 'length', 'width', 'height'),
            'classes': ('collapse',)
        }),
        ('سئو', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('آمار', {
            'fields': ('view_count', 'sale_count'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_primary', 'order']
    list_filter = ['is_primary', 'created_at']
    list_editable = ['is_primary', 'order']
    search_fields = ['product__name', 'alt_text']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return '-'
    image_preview.short_description = 'پیش‌نمایش'


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_required', 'is_filterable', 'order']
    list_filter = ['is_required', 'is_filterable']
    list_editable = ['is_required', 'is_filterable', 'order']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['product', 'attribute', 'value']
    list_filter = ['attribute']
    search_fields = ['product__name', 'attribute__name', 'value']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_verified_purchase', 'created_at']
    list_editable = ['is_approved']
    search_fields = ['product__name', 'user__first_name', 'user__last_name', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'sku', 'price', 'stock_quantity', 'is_active']
    list_filter = ['is_active', 'created_at']
    list_editable = ['price', 'stock_quantity', 'is_active']
    search_fields = ['product__name', 'name', 'sku']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__first_name', 'user__last_name', 'product__name']
    readonly_fields = ['created_at']