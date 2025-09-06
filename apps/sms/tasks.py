from celery import shared_task
from django.utils import timezone
from .models import SMSLog, SMSProvider, SMSTemplate
from .backends import SMSGateway
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_otp_sms(phone, code):
    """ارسال کد یکبارمصرف"""
    try:
        gateway = SMSGateway()
        result = gateway.send_otp(phone, code)
        
        # ذخیره لاگ
        SMSLog.objects.create(
            phone=phone,
            message=f"کد تأیید: {code}",
            status='sent' if result['success'] else 'failed',
            response=str(result),
            cost=result.get('cost', 0)
        )
        
        return result
        
    except Exception as e:
        logger.error(f"OTP SMS task error: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def send_welcome_sms(phone, name):
    """ارسال پیام خوش‌آمدگویی"""
    try:
        gateway = SMSGateway()
        result = gateway.send_welcome(phone, name)
        
        # ذخیره لاگ
        SMSLog.objects.create(
            phone=phone,
            message=f"خوش‌آمدگویی برای {name}",
            status='sent' if result['success'] else 'failed',
            response=str(result),
            cost=result.get('cost', 0)
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Welcome SMS task error: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def send_order_confirmation_sms(phone, order_number):
    """ارسال تأیید سفارش"""
    try:
        gateway = SMSGateway()
        result = gateway.send_order_confirmation(phone, order_number)
        
        # ذخیره لاگ
        SMSLog.objects.create(
            phone=phone,
            message=f"تأیید سفارش {order_number}",
            status='sent' if result['success'] else 'failed',
            response=str(result),
            cost=result.get('cost', 0)
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Order confirmation SMS task error: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def send_marketing_campaign(campaign_id):
    """ارسال کمپین بازاریابی"""
    try:
        from .models import MarketingCampaign
        from apps.accounts.models import User
        
        campaign = MarketingCampaign.objects.get(id=campaign_id)
        campaign.status = 'running'
        campaign.started_at = timezone.now()
        campaign.save()
        
        gateway = SMSGateway()
        
        # دریافت مخاطبان
        users = User.objects.filter(is_active=True)
        
        # فیلتر بر اساس معیارهای کمپین
        if campaign.target_audience.get('newsletter_subscribed'):
            users = users.filter(profile__newsletter_subscribed=True)
        
        if campaign.target_audience.get('sms_notifications'):
            users = users.filter(profile__sms_notifications=True)
        
        if campaign.target_audience.get('verified_users'):
            users = users.filter(is_verified=True)
        
        total_recipients = users.count()
        campaign.total_recipients = total_recipients
        campaign.save()
        
        sent_count = 0
        delivered_count = 0
        failed_count = 0
        total_cost = 0
        
        for user in users:
            try:
                # جایگزینی متغیرها در قالب
                message = campaign.template.content
                message = message.replace('{name}', user.first_name)
                message = message.replace('{phone}', str(user.phone))
                
                result = gateway.send_marketing(user.phone, message)
                
                # ذخیره لاگ
                SMSLog.objects.create(
                    phone=user.phone,
                    message=message,
                    status='sent' if result['success'] else 'failed',
                    response=str(result),
                    cost=result.get('cost', 0)
                )
                
                if result['success']:
                    sent_count += 1
                    delivered_count += 1
                    total_cost += result.get('cost', 0)
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Marketing SMS error for {user.phone}: {e}")
                failed_count += 1
        
        # به‌روزرسانی آمار کمپین
        campaign.sent_count = sent_count
        campaign.delivered_count = delivered_count
        campaign.failed_count = failed_count
        campaign.total_cost = total_cost
        campaign.status = 'completed'
        campaign.completed_at = timezone.now()
        campaign.save()
        
        return {
            'success': True,
            'sent_count': sent_count,
            'delivered_count': delivered_count,
            'failed_count': failed_count,
            'total_cost': total_cost
        }
        
    except Exception as e:
        logger.error(f"Marketing campaign task error: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def cleanup_old_otp_codes():
    """پاک‌سازی کدهای یکبارمصرف قدیمی"""
    from apps.accounts.models import OTPCode
    
    try:
        # حذف کدهای منقضی شده
        expired_codes = OTPCode.objects.filter(
            expires_at__lt=timezone.now()
        )
        count = expired_codes.count()
        expired_codes.delete()
        
        logger.info(f"Cleaned up {count} expired OTP codes")
        return {'success': True, 'cleaned_count': count}
        
    except Exception as e:
        logger.error(f"OTP cleanup error: {e}")
        return {'success': False, 'error': str(e)}