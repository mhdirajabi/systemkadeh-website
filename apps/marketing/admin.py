from django.contrib import admin
from .models import Campaign, Discount


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'start_date', 'end_date', 'total_views', 'total_clicks', 'total_conversions']
    list_filter = ['status', 'start_date', 'end_date', 'created_at']
    list_editable = ['status']
    search_fields = ['name', 'description']
    readonly_fields = ['total_views', 'total_clicks', 'total_conversions', 'created_at', 'updated_at']


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_type', 'value', 'is_active', 'valid_from', 'valid_until', 'used_count']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until', 'created_at']
    list_editable = ['is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['used_count', 'created_at', 'updated_at']