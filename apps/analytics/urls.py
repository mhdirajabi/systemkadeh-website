from django.urls import path
from . import views


app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('charts/sales/', views.sales_chart_data, name='sales_chart_data'),
    path('charts/pageviews/', views.pageviews_chart_data, name='pageviews_chart_data'),
    path('export/pageviews.csv', views.export_pageviews_csv, name='export_pageviews_csv'),
    path('export/pageviews.xlsx', views.export_pageviews_xlsx, name='export_pageviews_xlsx'),
]
