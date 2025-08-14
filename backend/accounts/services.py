import logging
import pyotp
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)

User = get_user_model()


class AccountsSMSService:
    OTP_TIMEOUT = 300  # 5 minutes
    ATTEMPT_TIMEOUT = 900  # 15 minutes
    MAX_ATTEMPTS = 3

    @classmethod
    def generate_and_send(cls, phone):
        redis = caches["default"].client.get_client()
        otp_key = f"otp_{phone}"
        attempts_key = f"otp_attempts_{phone}"

        try:
            # Start Redis pipeline for atomic operations
            with redis.pipeline() as pipe:
                while True:
                    try:
                        # Watch the attempts key for changes
                        pipe.watch(attempts_key)

                        # Get current attempts
                        current_attempts = int(pipe.get(attempts_key)) or 0

                        if current_attempts >= cls.MAX_ATTEMPTS:
                            raise PermissionDenied(
                                "درخواست‌های شما بیش از حد مجاز است. لطفاً 15 دقیقه دیگر تلاش کنید."
                            )

                        # Generate OTP
                        secret = pyotp.random_base32()
                        otp = pyotp.TOTP(secret).now()

                        # Start transaction
                        pipe.multi()
                        pipe.incr(attempts_key)
                        pipe.expire(attempts_key, cls.ATTEMPT_TIMEOUT)
                        pipe.setex(otp_key, cls.OTP_TIMEOUT, secret)
                        pipe.execute()
                        break

                    except redis.WatchError:
                        continue

            # Send SMS
            cls._send_sms(
                phone,
                f"""کد تایید سیستمکده:
                        {otp}
                    اعتبار: 5 دقیقه
                """,
            )
            logger.info(f"OTP sent to {phone}")
            return otp

        except Exception as e:
            logger.error(f"OTP failed for {phone}: {str(e)}")
            raise

    @staticmethod
    def _send_sms(phone, message):
        """Replace this with your actual SMS gateway integration"""
        # Example: Kavenegar, Twilio, etc.
        print(f"SMS to {phone}: {message}")  # Remove in production
        # Implement actual SMS sending here

    @staticmethod
    def verify_otp(phone, code):
        redis = otp_cache.client.get_client()
        secret = redis.get(f"otp_{phone}")
        if not secret:
            return False

        return pyotp.TOTP(secret).verify(code)

    @staticmethod
    def send_profile_update_confirmation(phone):
        """Send SMS when profile is updated"""
        message = "تنظیمات حساب شما با موفقیت به روز رسانی شد"
        AccountsSMSService._send_sms(phone, message)

    @staticmethod
    def _get_template(message_key, language="fa"):
        templates = {
            "welcome": {
                "fa": "به سیستم خوش آمدید! کد تخفیف اول: 1234",
                "en": "Welcome! Your discount code: 1234",
            },
            "profile_update": {"fa": "پروفایل شما به روز شد", "en": "Profile updated"},
        }
        return templates.get(message_key, {}).get(language, message_key)

    @staticmethod
    def send_template(phone, template_key):
        profile = User.objects.get(phone=phone).profile
        message = AccountsSMSService._get_template(
            template_key, profile.preferred_language
        )
        AccountsSMSService._send_sms(phone, message)
