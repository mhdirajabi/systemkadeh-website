from django.utils.deprecation import MiddlewareMixin
from django.utils import translation


class LanguageMiddleware(MiddlewareMixin):
    """میان‌افزار تنظیم زبان فارسی"""
    
    def process_request(self, request):
        # تنظیم زبان فارسی برای کل سایت
        translation.activate('fa')
        request.LANGUAGE_CODE = 'fa'