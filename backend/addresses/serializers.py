from rest_framework import serializers
from .models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["user", "created_at"]

    def validate_postal_code(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("کد پستی باید ۱۰ رقم باشد.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user

        # اگه is_default هست، قبلی رو بردار
        if validated_data.get("is_default", False):
            Address.objects.filter(user=user).update(is_default=False)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("is_default", False):
            Address.objects.filter(user=instance.user).exclude(pk=instance.pk).update(
                is_default=False
            )
        return super().update(instance, validated_data)
