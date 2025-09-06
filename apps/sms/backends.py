from abc import ABC, abstractmethod
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)


class SMSBackend(ABC):
    """کلاس پایه برای ارسال پیامک"""
    
    @abstractmethod
    def send_sms(self, phone, message):
        """ارسال پیامک"""
        pass


class ConsoleSMSBackend(SMSBackend):
    """بک‌اند کنسول برای تست"""
    
    def send_sms(self, phone, message):
        logger.info(f"SMS to {phone}: {message}")
        return {
            'success': True,
            'message_id': 'console_test',
            'cost': 0
        }


class KavenegarSMSBackend(SMSBackend):
    """بک‌اند کاوه‌نگار"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'KAVENEGAR_API_KEY', '')
        self.base_url = 'https://api.kavenegar.com/v1'
    
    def send_sms(self, phone, message):
        try:
            url = f"{self.base_url}/{self.api_key}/sms/send.json"
            data = {
                'receptor': str(phone).replace('+98', '0'),
                'message': message,
                'sender': '10008663'  # شماره فرستنده
            }
            
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if result.get('return', {}).get('status') == 200:
                return {
                    'success': True,
                    'message_id': result['entries'][0]['messageid'],
                    'cost': result['entries'][0].get('cost', 0)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('return', {}).get('message', 'خطای نامشخص')
                }
                
        except Exception as e:
            logger.error(f"Kavenegar SMS error: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class MelipayamakSMSBackend(SMSBackend):
    """بک‌اند ملی‌پیامک"""
    
    def __init__(self):
        self.username = getattr(settings, 'MELIPAYAMAK_USERNAME', '')
        self.password = getattr(settings, 'MELIPAYAMAK_PASSWORD', '')
        self.base_url = 'https://rest.payamak-panel.com/api/SendSMS/SendSMS'
    
    def send_sms(self, phone, message):
        try:
            data = {
                'username': self.username,
                'password': self.password,
                'to': str(phone).replace('+98', '0'),
                'from': '50004001001000',  # شماره فرستنده
                'text': message
            }
            
            response = requests.post(self.base_url, data=data, timeout=10)
            result = response.json()
            
            if result.get('RetStatus') == 1:
                return {
                    'success': True,
                    'message_id': result.get('StrRetStatus'),
                    'cost': 0
                }
            else:
                return {
                    'success': False,
                    'error': result.get('StrRetStatus', 'خطای نامشخص')
                }
                
        except Exception as e:
            logger.error(f"Melipayamak SMS error: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class SMSGateway:
    """درگاه پیامک"""
    
    def __init__(self):
        self.backend = self._get_backend()
    
    def _get_backend(self):
        backend_name = getattr(settings, 'SMS_BACKEND', 'console')
        
        if backend_name == 'kavenegar':
            return KavenegarSMSBackend()
        elif backend_name == 'melipayamak':
            return MelipayamakSMSBackend()
        else:
            return ConsoleSMSBackend()
    
    def send_sms(self, phone, message):
        """ارسال پیامک"""
        return self.backend.send_sms(phone, message)
    
    def send_otp(self, phone, code):
        """ارسال کد یکبارمصرف"""
        message = f"کد تأیید سیستمکده: {code}\nاین کد تا ۵ دقیقه معتبر است."
        return self.send_sms(phone, message)
    
    def send_welcome(self, phone, name):
        """ارسال پیام خوش‌آمدگویی"""
        message = f"سلام {name} عزیز!\nبه خانواده بزرگ سیستمکده خوش آمدید! 🎉\nبا ما بهترین تجربه خرید را داشته باشید."
        return self.send_sms(phone, message)
    
    def send_order_confirmation(self, phone, order_number):
        """ارسال تأیید سفارش"""
        message = f"سفارش شما با شماره {order_number} ثبت شد.\nبه زودی با شما تماس خواهیم گرفت.\nسیستمکده"
        return self.send_sms(phone, message)
    
    def send_marketing(self, phone, message):
        """ارسال پیام بازاریابی"""
        return self.send_sms(phone, message)