from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import DeviceLog, CustomUser, UserProfile
from .tasks import notify_admin_task


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def sync_sms_permissions(sender, instance, **kwargs):
    """Ensure SMS preferences sync with marketing systems"""
    if not instance.profile.sms_marketing_optin:
        instance.allow_sms = False
        instance.save(update_fields=["allow_sms"])


@receiver(pre_save, sender=DeviceLog)
def check_suspicious_login(sender, instance, **kwargs):
    """
    Detects and alerts on suspicious login activity
    """
    if not instance.pk:
        one_hour_ago = timezone.now() - timedelta(hours=1)

        recent_logins = DeviceLog.objects.filter(
            user=instance.user, logged_at__gte=one_hour_ago
        ).count()

        if recent_logins > 3:
            notify_admin_task.delay(
                user_id=instance.user.id,
                ip_address=instance.ip,
                user_agent=instance.user_agent,
            )  # pyright: ignore[reportCallIssue]
