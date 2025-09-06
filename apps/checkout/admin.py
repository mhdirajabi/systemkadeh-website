from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, ShippingMethod, OrderStatusHistory, OrderNote


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['product', 'variant', 'quantity', 'price', 'total_price']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['created_at']
    fields = ['status', 'note', 'created_at']


class OrderNoteInline(admin.TabularInline):
    model = OrderNote
    extra = 0
    readonly_fields = ['created_at']
    fields = ['note', 'is_public', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'payment_status',
        'total_amount', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at']
    list_editable = ['status', 'payment_status']
    search_fields = ['order_number', 'user__phone', 'user__first_name', 'user__last_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderStatusHistoryInline, OrderNoteInline]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('قیمت‌گذاری', {
            'fields': ('subtotal', 'shipping_cost', 'discount_amount', 'total_amount')
        }),
        ('اطلاعات ارسال', {
            'fields': (
                'shipping_name', 'shipping_phone', 'shipping_address',
                'shipping_city', 'shipping_province', 'shipping_postal_code'
            )
        }),
        ('اطلاعات اضافی', {
            'fields': ('notes', 'tracking_number'),
            'classes': ('collapse',)
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'variant', 'quantity', 'price', 'total_price']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['order__order_number', 'product__name']
    readonly_fields = ['total_price']


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost', 'free_shipping_threshold', 'estimated_days', 'is_active', 'order']
    list_filter = ['is_active']
    list_editable = ['cost', 'is_active', 'order']
    search_fields = ['name', 'description']


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'note', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'note']
    readonly_fields = ['created_at']


@admin.register(OrderNote)
class OrderNoteAdmin(admin.ModelAdmin):
    list_display = ['order', 'note_preview', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['order__order_number', 'note']
    readonly_fields = ['created_at']
    
    def note_preview(self, obj):
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'پیش‌نمایش یادداشت'