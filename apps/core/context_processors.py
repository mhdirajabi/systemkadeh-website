from .models import SiteSettings, Banner


def site_settings(request):
    """اضافه کردن تنظیمات سایت به context"""
    try:
        settings = SiteSettings.objects.first()
        if not settings:
            settings = SiteSettings.objects.create()
    except:
        settings = None
    
    return {
        'site_settings': settings,
    }


def banners(request):
    """اضافه کردن بنرهای فعال به context"""
    banners = Banner.objects.filter(is_active=True).order_by('order')
    return {
        'banners': banners,
    }