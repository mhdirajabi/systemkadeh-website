from django.contrib import admin
from .models import SiteSettings, Banner, ContactMessage, Newsletter


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'phone', 'email', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'banner_type', 'is_active', 'order', 'created_at']
    list_filter = ['banner_type', 'is_active']
    list_editable = ['is_active', 'order']
    search_fields = ['title', 'subtitle']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['email']