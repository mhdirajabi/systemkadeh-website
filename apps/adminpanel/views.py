from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, Permission
from django.db.models import Sum, Count
from apps.checkout.models import Order
from apps.catalog.models import Product
from apps.accounts.models import User
from apps.analytics.models import PageView


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class PanelDashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'adminpanel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users_count'] = User.objects.count()
        context['products_count'] = Product.objects.count()
        context['orders_count'] = Order.objects.count()
        context['revenue_total'] = Order.objects.filter(payment_status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        context['page_views'] = PageView.objects.count()
        return context
