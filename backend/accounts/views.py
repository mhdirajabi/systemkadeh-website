import re

import logging

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import DeviceLog
from .serializers import (
    DeviceLogSerializer,
    PhoneSignUpSerializer,
    PhoneLoginSerializer,
    UserProfileSerializer,
)
from .services import AccountsSMSService

logger = logging.getLogger(__name__)

User = get_user_model()


# Common authentication flows:
@method_decorator(ratelimit(key="ip", rate="5/h"), name="dispatch")
class SignUpAPIView(APIView):
    """
    Phone-only registration flow:
    1. POST /signup/ → Send OTP
    2. POST /verify/ → Confirm OTP
    """

    def post(self, request):
        serializer = PhoneSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        AccountsSMSService.generate_and_send(user.phone)

        return Response(
            {"detail": "کد تایید به شماره موبایل شما ارسال شد"},
            status=status.HTTP_201_CREATED,
        )


@method_decorator(ratelimit(key="ip", rate="5/h"), name="dispatch")
class LoginAPIView(APIView):
    def post(self, request):
        serializer = PhoneLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        user = User.objects.get(phone=phone)

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        # Log device info (for security)
        self._log_login_attempt(request, user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {"phone": user.phone},
            }
        )

    def _log_login_attempt(self, request, user):
        DeviceLog.objects.create(
            user=user,
            ip=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(
                {"error": "توکن نامعتبر است"}, status=status.HTTP_400_BAD_REQUEST
            )


# OTP management views:
@method_decorator(ratelimit(key="ip", rate="10/h"), name="dispatch")
class VerifyOTPView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        code = request.data.get("code")

        if not AccountsSMSService.verify_otp(phone, code):
            return Response(
                {"error": "کد تایید نامعتبر یا منقضی شده است"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Activate user
        user = User.objects.get(phone=phone)
        user.is_active = True
        user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {"phone": user.phone},
            }
        )


class SendOTPView(APIView):
    @method_decorator(ratelimit(key="ip", rate="5/h", method="POST"))
    def post(self, request):
        phone = request.data.get("phone")
        if not phone or not re.match(r"^09\d{9}$", phone):
            return Response(
                {"error": "شماره موبایل باید با 09 شروع شود و 11 رقم باشد"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            AccountsSMSService.generate_and_send(phone)
            return Response({"detail": "کد تایید ارسال شد"}, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except Exception as e:
            logger.error(f"OTP send failed: {str(e)}")
            return Response(
                {"error": "خطا در سیستم ارسال کد"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResendOTPView(APIView):
    @method_decorator(ratelimit(key="ip", rate="3/h", method="POST"))
    def post(self, request):
        phone = request.data.get("phone")
        if not get_user_model().objects.filter(phone=phone).exists():
            return Response(
                {"error": "حسابی با این شماره موبایل ثبت نشده است"},
                status=status.HTTP_404_NOT_FOUND,
            )

        AccountsSMSService.generate_and_send(phone)
        return Response({"detail": "کد تایید مجدد ارسال شد"}, status=status.HTTP_200_OK)


# Security views:
class DeviceListView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key="user", rate="30/m", method="GET"))
    def get(self, request):
        devices = DeviceLog.objects.filter(user=request.user).order_by("-logged_at")
        serializer = DeviceLogSerializer(devices, many=True)
        return Response(serializer.data)


class RevokeDeviceView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key="user", rate="10/h", method="DELETE"))
    def delete(self, request, pk):
        device = get_object_or_404(DeviceLog, pk=pk, user=request.user)
        device.delete()
        return Response(
            {"detail": "دستگاه با موفقیت حذف شد"}, status=status.HTTP_204_NO_CONTENT
        )


# User profile views:
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProfileCompletionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Check which profile fields are missing"""
        profile = request.user.profile
        missing = []

        if not profile.birth_date:
            missing.append("birth_date")

        return Response({"is_complete": len(missing) == 0, "missing_fields": missing})


class SMSUnsubscribeView(APIView):
    """Single endpoint to manage all SMS preferences"""

    def post(self, request):
        profile = request.user.profile
        profile.sms_marketing_optin = False
        profile.sms_newsletter = False
        profile.save()
        return Response({"detail": "شما از دریافت پیام‌های تبلیغاتی انصراف دادید"})
