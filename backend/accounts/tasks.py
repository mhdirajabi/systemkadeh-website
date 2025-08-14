# backend/accounts/tasks.py
from celery import shared_task
from django.core.mail import mail_admins
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import CustomUser


@shared_task(bind=True)
def notify_admin_task(self, user_id: int, ip_address: str, user_agent: str):
    """Properly typed Celery task with phone field access"""
    try:
        user = CustomUser.objects.get(pk=user_id)
        subject = f"Suspicious login activity for {user.phone}"  # Now recognized
        message = f"""
        User: {user.phone}
        IP: {ip_address}
        User Agent: {user_agent}
        """
        mail_admins(subject, message)
    except CustomUser.DoesNotExist:
        self.retry(countdown=60, max_retries=3)
    except Exception:
        # Log the error
        from django.core.exceptions import ImproperlyConfigured

        if hasattr(user, "phone"):  # pyright: ignore[reportPossiblyUnboundVariable]
            raise ImproperlyConfigured(
                "User model must have 'phone' field. "
                "Did you forget to use your custom User model?"
            )
        raise
