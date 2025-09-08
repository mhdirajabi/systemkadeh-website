from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from django.db.models import Count, Sum
from django.http import JsonResponse, HttpResponse
from apps.checkout.models import Order, OrderItem
from .models import PageView, SalesAggregate, KPIRecord
import csv
from openpyxl import Workbook


@method_decorator(staff_member_required, name='dispatch')
class AnalyticsDashboardView(TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # KPI's
        context['orders_total'] = Order.objects.count()
        context['revenue_total'] = Order.objects.filter(payment_status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        context['unique_visitors'] = PageView.objects.values('session_key').distinct().count()
        context['page_views'] = PageView.objects.count()
        return context


@staff_member_required
def sales_chart_data(request):
    period = request.GET.get('period', 'month')
    qs = Order.objects.filter(payment_status='paid')
    if period == 'day':
        qs = qs.annotate(p=TruncDate('created_at')).values('p').annotate(total=Sum('total_amount'), count=Count('id')).order_by('p')
    elif period == 'week':
        qs = qs.annotate(p=TruncWeek('created_at')).values('p').annotate(total=Sum('total_amount'), count=Count('id')).order_by('p')
    elif period == 'year':
        qs = qs.annotate(p=TruncYear('created_at')).values('p').annotate(total=Sum('total_amount'), count=Count('id')).order_by('p')
    else:
        qs = qs.annotate(p=TruncMonth('created_at')).values('p').annotate(total=Sum('total_amount'), count=Count('id')).order_by('p')
    labels = [x['p'].strftime('%Y-%m-%d') for x in qs]
    totals = [int(x['total'] or 0) for x in qs]
    counts = [x['count'] for x in qs]
    return JsonResponse({'labels': labels, 'totals': totals, 'counts': counts})


@staff_member_required
def pageviews_chart_data(request):
    period = request.GET.get('period', 'month')
    qs = PageView.objects.all()
    if period == 'day':
        qs = qs.annotate(p=TruncDate('created_at')).values('p').annotate(count=Count('id'), uniques=Count('session_key', distinct=True)).order_by('p')
    elif period == 'week':
        qs = qs.annotate(p=TruncWeek('created_at')).values('p').annotate(count=Count('id'), uniques=Count('session_key', distinct=True)).order_by('p')
    elif period == 'year':
        qs = qs.annotate(p=TruncYear('created_at')).values('p').annotate(count=Count('id'), uniques=Count('session_key', distinct=True)).order_by('p')
    else:
        qs = qs.annotate(p=TruncMonth('created_at')).values('p').annotate(count=Count('id'), uniques=Count('session_key', distinct=True)).order_by('p')
    labels = [x['p'].strftime('%Y-%m-%d') for x in qs]
    counts = [x['count'] for x in qs]
    uniques = [x['uniques'] for x in qs]
    return JsonResponse({'labels': labels, 'counts': counts, 'uniques': uniques})


@staff_member_required
def export_pageviews_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pageviews.csv"'
    writer = csv.writer(response)
    writer.writerow(['path', 'session_key', 'user', 'status_code', 'created_at'])
    for pv in PageView.objects.all().order_by('-created_at')[:10000]:
        writer.writerow([pv.path, pv.session_key, getattr(pv.user, 'phone', ''), pv.status_code, pv.created_at])
    return response


@staff_member_required
def export_pageviews_xlsx(request):
    wb = Workbook()
    ws = wb.active
    ws.append(['path', 'session_key', 'user', 'status_code', 'created_at'])
    for pv in PageView.objects.all().order_by('-created_at')[:10000]:
        ws.append([pv.path, pv.session_key, getattr(pv.user, 'phone', ''), pv.status_code, pv.created_at.strftime('%Y-%m-%d %H:%M')])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=pageviews.xlsx'
    wb.save(response)
    return response
