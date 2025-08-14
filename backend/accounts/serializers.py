from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import CustomUser, DeviceLog, UserProfile
from .services import AccountsSMSService


class PhoneSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["phone"]

    def create(self, validated_data):
        phone = validated_data["phone"]
        user, created = CustomUser.objects.get_or_create(
            phone=phone,
            defaults={"is_active": False},  # Inactive until OTP verification
        )

        if not created and user.is_active:
            raise serializers.ValidationError("این شماره قبلا ثبت شده است")

        return user


class PhoneLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    otp = serializers.CharField(max_length=6, required=False)

    def validate_phone(self, value):
        if not CustomUser.objects.filter(phone=value).exists():
            raise ValidationError("حسابی با این شماره موبایل وجود ندارد")
        return value

    def validate(self, attrs):
        phone = attrs["phone"]

        # Step 1: Request OTP
        if "otp" not in attrs:
            AccountsSMSService.generate_and_send(phone)
            raise serializers.ValidationError({"detail": "کد تایید ارسال شد"})

        # Step 2: Verify OTP
        if not AccountsSMSService.verify_otp(phone, attrs["otp"]):
            raise ValidationError({"otp": "کد تایید نامعتبر است"})

        return attrs


class DeviceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceLog
        fields = [
            "id",
            "ip",
            "city",
            "country",
            "logged_at",
            "user_agent",
        ]

    def get_location(self, obj):
        if obj.city and obj.country:
            return f"{obj.city}, {obj.country}"
        return "نامشخص"


class UserProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "phone",
            "sms_marketing_optin",
            "sms_order_updates",
            "sms_newsletter",
            "birth_date",
            "preferred_language",
            "loyalty_points",
        ]
        extra_kwargs = {
            "birth_date": {"required": False},
        }
