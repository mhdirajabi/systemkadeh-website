from django.contrib import admin
from .models import SMSProvider, SMSLog, SMSTemplate, MarketingCampaign


@admin.register(SMSProvider)
class SMSProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'priority', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active', 'priority']
    search_fields = ['name']


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ['phone', 'status', 'provider', 'cost', 'created_at']
    list_filter = ['status', 'provider', 'created_at']
    search_fields = ['phone', 'message']
    readonly_fields = ['created_at', 'sent_at']
    date_hierarchy = 'created_at'


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['name', 'content']


@admin.register(MarketingCampaign)
class MarketingCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'total_recipients', 'sent_count', 'delivered_count', 'total_cost', 'created_at']
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']
    date_hierarchy = 'created_at'