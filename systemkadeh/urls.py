"""
URL configuration for SystemKadeh project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from apps.seo.sitemaps import ProductSitemap, CategorySitemap, BlogSitemap, StaticSitemap

sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'blog': BlogSitemap,
    'static': StaticSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('catalog/', include('apps.catalog.urls')),
    path('cart/', include('apps.cart.urls')),
    path('checkout/', include('apps.checkout.urls')),
    path('payments/', include('apps.payments.urls')),
    path('blog/', include('apps.blog.urls')),
    path('marketing/', include('apps.marketing.urls')),
    path('sms/', include('apps.sms.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('adminpanel/', include('apps.adminpanel.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns