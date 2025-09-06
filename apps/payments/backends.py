from abc import ABC, abstractmethod
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)


class PaymentProvider(ABC):
    """کلاس پایه برای ارائه‌دهندگان پرداخت"""
    
    def __init__(self, config):
        self.config = config
    
    @abstractmethod
    def create_payment(self, amount, order_number, callback_url, description=""):
        """ایجاد پرداخت"""
        pass
    
    @abstractmethod
    def verify_payment(self, transaction_id, amount):
        """تأیید پرداخت"""
        pass
    
    @abstractmethod
    def refund_payment(self, transaction_id, amount):
        """مرجوع پرداخت"""
        pass


class ZarinpalProvider(PaymentProvider):
    """ارائه‌دهنده زرین‌پال"""
    
    def __init__(self, config):
        super().__init__(config)
        self.merchant_id = config.get('merchant_id', '')
        self.sandbox = config.get('sandbox', True)
        self.base_url = 'https://sandbox.zarinpal.com' if self.sandbox else 'https://api.zarinpal.com'
    
    def create_payment(self, amount, order_number, callback_url, description=""):
        try:
            url = f"{self.base_url}/pg/v4/payment/request.json"
            data = {
                'merchant_id': self.merchant_id,
                'amount': int(amount),
                'description': description or f'پرداخت سفارش {order_number}',
                'callback_url': callback_url,
                'metadata': {
                    'order_number': order_number
                }
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('data', {}).get('code') == 100:
                authority = result['data']['authority']
                payment_url = f"{self.base_url}/pg/StartPay/{authority}"
                return {
                    'success': True,
                    'authority': authority,
                    'payment_url': payment_url
                }
            else:
                return {
                    'success': False,
                    'error': result.get('errors', {}).get('message', 'خطای نامشخص')
                }
                
        except Exception as e:
            logger.error(f"Zarinpal payment creation error: {e}")
            return {'success': False, 'error': str(e)}
    
    def verify_payment(self, authority, amount):
        try:
            url = f"{self.base_url}/pg/v4/payment/verify.json"
            data = {
                'merchant_id': self.merchant_id,
                'amount': int(amount),
                'authority': authority
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('data', {}).get('code') == 100:
                return {
                    'success': True,
                    'transaction_id': result['data']['ref_id'],
                    'card_pan': result['data'].get('card_pan', ''),
                    'fee': result['data'].get('fee', 0)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('errors', {}).get('message', 'خطای نامشخص')
                }
                
        except Exception as e:
            logger.error(f"Zarinpal payment verification error: {e}")
            return {'success': False, 'error': str(e)}
    
    def refund_payment(self, transaction_id, amount):
        # زرین‌پال API مرجوعی ندارد
        return {'success': False, 'error': 'مرجوعی از طریق زرین‌پال پشتیبانی نمی‌شود'}


class ZibalProvider(PaymentProvider):
    """ارائه‌دهنده زیبال"""
    
    def __init__(self, config):
        super().__init__(config)
        self.merchant_id = config.get('merchant_id', '')
        self.sandbox = config.get('sandbox', True)
        self.base_url = 'https://sandbox.zibal.ir' if self.sandbox else 'https://gateway.zibal.ir'
    
    def create_payment(self, amount, order_number, callback_url, description=""):
        try:
            url = f"{self.base_url}/v1/request"
            data = {
                'merchant': self.merchant_id,
                'amount': int(amount),
                'description': description or f'پرداخت سفارش {order_number}',
                'callbackUrl': callback_url,
                'orderId': order_number
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('result') == 100:
                track_id = result['trackId']
                payment_url = f"{self.base_url}/v1/request/{track_id}"
                return {
                    'success': True,
                    'track_id': track_id,
                    'payment_url': payment_url
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'خطای نامشخص')
                }
                
        except Exception as e:
            logger.error(f"Zibal payment creation error: {e}")
            return {'success': False, 'error': str(e)}
    
    def verify_payment(self, track_id, amount):
        try:
            url = f"{self.base_url}/v1/verify"
            data = {
                'merchant': self.merchant_id,
                'trackId': track_id,
                'amount': int(amount)
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('result') == 100:
                return {
                    'success': True,
                    'transaction_id': result.get('refNumber', track_id),
                    'card_pan': result.get('cardNumber', ''),
                    'fee': result.get('fee', 0)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'خطای نامشخص')
                }
                
        except Exception as e:
            logger.error(f"Zibal payment verification error: {e}")
            return {'success': False, 'error': str(e)}
    
    def refund_payment(self, transaction_id, amount):
        # زیبال API مرجوعی ندارد
        return {'success': False, 'error': 'مرجوعی از طریق زیبال پشتیبانی نمی‌شود'}


class TerbPayProvider(PaymentProvider):
    """ارائه‌دهنده ترب‌پی (پرداخت اقساطی)"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.sandbox = config.get('sandbox', True)
        self.base_url = 'https://sandbox.terbpay.com' if self.sandbox else 'https://api.terbpay.com'
    
    def create_payment(self, amount, order_number, callback_url, description="", installment_count=12):
        try:
            url = f"{self.base_url}/v1/installment/request"
            data = {
                'api_key': self.api_key,
                'amount': int(amount),
                'order_id': order_number,
                'description': description or f'پرداخت اقساطی سفارش {order_number}',
                'callback_url': callback_url,
                'installment_count': installment_count,
                'customer_info': {
                    'order_number': order_number
                }
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('status') == 'success':
                return {
                    'success': True,
                    'transaction_id': result['transaction_id'],
                    'payment_url': result['payment_url'],
                    'installment_plan': result.get('installment_plan', {})
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'خطای نامشخص')
                }
                
        except Exception as e:
            logger.error(f"TerbPay payment creation error: {e}")
            return {'success': False, 'error': str(e)}
    
    def verify_payment(self, transaction_id, amount):
        try:
            url = f"{self.base_url}/v1/installment/verify"
            data = {
                'api_key': self.api_key,
                'transaction_id': transaction_id,
                'amount': int(amount)
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('status') == 'success':
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'installment_plan': result.get('installment_plan', {})
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'خطای نامشخص')
                }
                
        except Exception as e:
            logger.error(f"TerbPay payment verification error: {e}")
            return {'success': False, 'error': str(e)}
    
    def refund_payment(self, transaction_id, amount):
        try:
            url = f"{self.base_url}/v1/installment/refund"
            data = {
                'api_key': self.api_key,
                'transaction_id': transaction_id,
                'amount': int(amount)
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('status') == 'success':
                return {
                    'success': True,
                    'refund_id': result.get('refund_id')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'خطای نامشخص')
                }
                
        except Exception as e:
            logger.error(f"TerbPay refund error: {e}")
            return {'success': False, 'error': str(e)}


class PaymentGateway:
    """درگاه پرداخت"""
    
    def __init__(self):
        self.providers = self._load_providers()
    
    def _load_providers(self):
        """بارگذاری ارائه‌دهندگان"""
        providers = {}
        
        # زرین‌پال
        if hasattr(settings, 'PAYMENT_PROVIDERS') and 'zarinpal' in settings.PAYMENT_PROVIDERS:
            providers['zarinpal'] = ZarinpalProvider(settings.PAYMENT_PROVIDERS['zarinpal'])
        
        # زیبال
        if hasattr(settings, 'PAYMENT_PROVIDERS') and 'zibal' in settings.PAYMENT_PROVIDERS:
            providers['zibal'] = ZibalProvider(settings.PAYMENT_PROVIDERS['zibal'])
        
        # ترب‌پی
        if hasattr(settings, 'PAYMENT_PROVIDERS') and 'terbpay' in settings.PAYMENT_PROVIDERS:
            providers['terbpay'] = TerbPayProvider(settings.PAYMENT_PROVIDERS['terbpay'])
        
        return providers
    
    def create_payment(self, provider_name, amount, order_number, callback_url, description="", **kwargs):
        """ایجاد پرداخت"""
        if provider_name not in self.providers:
            return {'success': False, 'error': 'ارائه‌دهنده پرداخت یافت نشد'}
        
        provider = self.providers[provider_name]
        return provider.create_payment(amount, order_number, callback_url, description, **kwargs)
    
    def verify_payment(self, provider_name, transaction_id, amount):
        """تأیید پرداخت"""
        if provider_name not in self.providers:
            return {'success': False, 'error': 'ارائه‌دهنده پرداخت یافت نشد'}
        
        provider = self.providers[provider_name]
        return provider.verify_payment(transaction_id, amount)
    
    def refund_payment(self, provider_name, transaction_id, amount):
        """مرجوع پرداخت"""
        if provider_name not in self.providers:
            return {'success': False, 'error': 'ارائه‌دهنده پرداخت یافت نشد'}
        
        provider = self.providers[provider_name]
        return provider.refund_payment(transaction_id, amount)