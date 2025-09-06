from django.contrib import admin
from .models import SEOPage, SchemaMarkup


@admin.register(SEOPage)
class SEOPageAdmin(admin.ModelAdmin):
    list_display = ['page_type', 'page_id', 'title', 'created_at']
    list_filter = ['page_type', 'created_at']
    search_fields = ['title', 'meta_description', 'meta_keywords']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SchemaMarkup)
class SchemaMarkupAdmin(admin.ModelAdmin):
    list_display = ['name', 'schema_type', 'page_type', 'page_id', 'is_active']
    list_filter = ['schema_type', 'page_type', 'is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']