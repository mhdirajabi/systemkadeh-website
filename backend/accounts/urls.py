from django.urls import path
from .views import (
    ProfileCompletionView,
    ProfileView,
    SMSUnsubscribeView,
    SendOTPView,
    ResendOTPView,
    VerifyOTPView,
    SignUpAPIView,
    LoginAPIView,
    LogoutView,
    DeviceListView,
    RevokeDeviceView,
)

urlpatterns = [
    # OTP Flow
    path("otp/send/", SendOTPView.as_view(), name="send-otp"),
    path("otp/resend/", ResendOTPView.as_view(), name="resend-otp"),
    path("otp/verify/", VerifyOTPView.as_view(), name="verify-otp"),
    # Auth Flow
    path("signup/", SignUpAPIView.as_view(), name="signup"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # Device Management
    path("devices/", DeviceListView.as_view(), name="device-list"),
    path("devices/<int:pk>/", RevokeDeviceView.as_view(), name="revoke-device"),
    # Profile
    path("profile/", ProfileView.as_view(), name="user-profile"),
    path("profile/unsubscribe/", SMSUnsubscribeView.as_view()),
    path("profile/completion/", ProfileCompletionView.as_view()),
]
