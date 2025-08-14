from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings


class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
        editable=False,  # Prevent user_id tampering
    )
    postal_code = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(regex=r"^\d{10}$", message="کد پستی باید 10 رقم باشد")
        ],
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verification_token = models.CharField(max_length=64, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "is_default"],
                condition=models.Q(is_default=True),
                name="unique_default_address",
            )
        ]
        permissions = [("verify_address", "Can verify address legitimacy")]

    def save(self, *args, **kwargs):
        # Prevent multiple defaults
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(
                is_default=False
            )
        super().save(*args, **kwargs)
