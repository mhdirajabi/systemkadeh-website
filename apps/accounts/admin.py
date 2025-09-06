from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserAddress, OTPCode, UserProfile, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['phone', 'email', 'first_name', 'last_name', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['is_verified', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['phone', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email', 'birth_date', 'avatar')}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌های مهم', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'city', 'is_default', 'created_at']
    list_filter = ['is_default', 'province', 'city', 'created_at']
    search_fields = ['user__phone', 'user__first_name', 'user__last_name', 'title', 'address']
    list_editable = ['is_default']


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['phone', 'code', 'is_used', 'expires_at', 'created_at']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['phone']
    readonly_fields = ['created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'newsletter_subscribed', 'sms_notifications', 'email_notifications']
    list_filter = ['newsletter_subscribed', 'sms_notifications', 'email_notifications']
    search_fields = ['user__phone', 'user__first_name', 'user__last_name']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'is_active', 'last_activity']
    list_filter = ['is_active', 'last_activity', 'created_at']
    search_fields = ['user__phone', 'user__first_name', 'user__last_name', 'ip_address']
    readonly_fields = ['created_at', 'last_activity']