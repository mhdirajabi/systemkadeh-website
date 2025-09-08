from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import PageView


class AnalyticsMiddleware(MiddlewareMixin):
    """میان‌افزار ثبت بازدید صفحات"""
    
    def process_response(self, request, response):
        try:
            if request.method in ['GET'] and not request.path.startswith(('/static/', '/media/', '/admin/', '/__debug__')):
                session_key = request.session.session_key or ''
                if not session_key:
                    try:
                        request.session.save()
                        session_key = request.session.session_key or ''
                    except Exception:
                        session_key = ''
                PageView.objects.create(
                    session_key=session_key[:40],
                    user=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
                    path=request.path[:512],
                    method=request.method,
                    referrer=request.META.get('HTTP_REFERER', '')[:512],
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
                    ip_address=request.META.get('REMOTE_ADDR'),
                    status_code=response.status_code,
                )
        except Exception:
            # لاگ را بی‌صدا نادیده بگیر تا در مسیر درخواست اختلالی ایجاد نشود
            pass
        return response
