from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import hashlib

from .models import Address


@receiver(post_save, sender=Address)
def initiate_verification(sender, instance, created, **kwargs):
    if created and not instance.verification_token:
        # Generate cryptographic token
        raw_token = f"{instance.id}{instance.user_id}{timezone.now().timestamp()}"
        instance.verification_token = hashlib.sha256(raw_token.encode()).hexdigest()
        instance.save(update_fields=["verification_token"])

        # Async verification task
        verify_address.delay(instance.id)
