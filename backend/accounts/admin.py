from django.contrib import admin

from .models import DeviceLog, CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("phone", "date_joined", "is_active")
    search_fields = ("phone",)
    list_filter = ("is_active",)

    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("وضعیت", {"fields": ("is_active",)}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing user
            return ["phone"]  # Never allow phone changes
        return []


class DeviceLogAdmin(admin.ModelAdmin):
    list_display = ("user", "ip", "logged_at")
    list_filter = ("logged_at",)
    search_fields = ("user__phone", "ip")


admin.site.register(DeviceLog, DeviceLogAdmin)
