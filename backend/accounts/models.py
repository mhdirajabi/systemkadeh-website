from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class CustomUser(AbstractUser):
    # Remove username field completely
    username = None

    phone = models.CharField(
        _("phone number"),
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^09\d{9}$",
                message=_("شماره موبایل باید با 09 شروع شود و 11 رقم باشد"),
            )
        ],
        error_messages={"unique": _("این شماره موبایل قبلا ثبت شده است")},
    )

    # Security
    otp_secret = models.CharField(max_length=32)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    last_failed_attempt = models.DateTimeField(null=True, blank=True)
    phone_verified = models.BooleanField(default=False)

    # Tracking
    signup_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)

    # Permissions
    terms_accepted = models.BooleanField(default=False)
    allow_sms = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    # Remove username field
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    class Meta:
        app_label = "accounts"
        verbose_name = _("user")
        verbose_name_plural = _("users")
        permissions = [
            ("can_reset_otp", _("Can reset OTP secret")),
            ("unlock_account", _("Can unlock locked accounts")),
            ("can_verify_users", _("Can manually verify users")),
        ]

    def active_devices(self):
        return self.devicelog_set.order_by("-logged_at")[:5]


class DeviceLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=300)
    logged_at = models.DateTimeField(auto_now_add=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        from .utils import geoip_service

        if not self.pk and self.ip:  # Only on creation
            location = geoip_service.get_location(self.ip)
            self.city = location["city"]
            self.country = location["country"]
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    # Phone-based communication preferences
    sms_marketing_optin = models.BooleanField(
        default=True, verbose_name="SMS Campaigns"
    )
    sms_order_updates = models.BooleanField(
        default=True, verbose_name="Order Notifications"
    )
    sms_newsletter = models.BooleanField(default=False, verbose_name="Newsletter")

    # User metadata
    birth_date = models.DateField(null=True, blank=True)

    # Loyalty program (will be expanded later)
    loyalty_points = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.phone}"
