from django.contrib import admin
from django.http import HttpResponse
import csv
from openpyxl import Workbook
from .models import PageView, SalesAggregate, KPIRecord


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['path', 'user', 'session_key', 'status_code', 'created_at']
    list_filter = ['status_code', 'created_at']
    search_fields = ['path', 'session_key', 'user__phone']
    date_hierarchy = 'created_at'
    actions = ['export_csv', 'export_xlsx']

    def export_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pageviews.csv"'
        writer = csv.writer(response)
        writer.writerow(['path', 'user', 'session_key', 'status_code', 'created_at'])
        for pv in queryset:
            writer.writerow([pv.path, getattr(pv.user, 'phone', ''), pv.session_key, pv.status_code, pv.created_at])
        return response
    export_csv.short_description = 'خروجی CSV'

    def export_xlsx(self, request, queryset):
        wb = Workbook()
        ws = wb.active
        ws.append(['path', 'user', 'session_key', 'status_code', 'created_at'])
        for pv in queryset:
            ws.append([pv.path, getattr(pv.user, 'phone', ''), pv.session_key, pv.status_code, pv.created_at])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=pageviews.xlsx'
        wb.save(response)
        return response
    export_xlsx.short_description = 'خروجی XLSX'


@admin.register(SalesAggregate)
class SalesAggregateAdmin(admin.ModelAdmin):
    list_display = ['period', 'period_start', 'period_end', 'orders_count', 'items_count', 'revenue', 'refunds']
    list_filter = ['period', 'period_start']
    search_fields = ['period']
    actions = ['export_csv', 'export_xlsx']

    def export_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales.csv"'
        writer = csv.writer(response)
        writer.writerow(['period', 'period_start', 'period_end', 'orders_count', 'items_count', 'revenue', 'refunds'])
        for r in queryset:
            writer.writerow([r.period, r.period_start, r.period_end, r.orders_count, r.items_count, r.revenue, r.refunds])
        return response

    def export_xlsx(self, request, queryset):
        wb = Workbook()
        ws = wb.active
        ws.append(['period', 'period_start', 'period_end', 'orders_count', 'items_count', 'revenue', 'refunds'])
        for r in queryset:
            ws.append([r.period, r.period_start, r.period_end, r.orders_count, r.items_count, r.revenue, r.refunds])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=sales.xlsx'
        wb.save(response)
        return response


@admin.register(KPIRecord)
class KPIRecordAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'label', 'recorded_at']
    list_filter = ['name', 'recorded_at']
    search_fields = ['name', 'label']
