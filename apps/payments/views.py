from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Payment, PaymentProvider
from .backends import PaymentGateway


@csrf_exempt
def verify_payment(request, payment_id):
    """تأیید پرداخت"""
    payment = get_object_or_404(Payment, payment_id=payment_id)
    
    if request.method == 'GET':
        # دریافت پارامترهای بازگشت از درگاه
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')
        
        if status == 'OK' and authority:
            try:
                with transaction.atomic():
                    # تأیید پرداخت
                    gateway = PaymentGateway()
                    result = gateway.verify_payment(
                        provider_name=payment.provider.slug,
                        transaction_id=authority,
                        amount=payment.amount
                    )
                    
                    if result['success']:
                        # به‌روزرسانی وضعیت پرداخت
                        payment.status = 'completed'
                        payment.provider_transaction_id = result['transaction_id']
                        payment.provider_response = result
                        payment.save()
                        
                        # به‌روزرسانی وضعیت سفارش
                        payment.order.payment_status = 'paid'
                        payment.order.status = 'confirmed'
                        payment.order.save()
                        
                        messages.success(request, 'پرداخت با موفقیت انجام شد.')
                        return redirect('checkout:checkout_success', order_number=payment.order.order_number)
                    else:
                        payment.status = 'failed'
                        payment.failure_reason = result['error']
                        payment.save()
                        
                        messages.error(request, f'پرداخت ناموفق: {result["error"]}')
                        return redirect('checkout:checkout_cancel')
            
            except Exception as e:
                payment.status = 'failed'
                payment.failure_reason = str(e)
                payment.save()
                
                messages.error(request, f'خطا در تأیید پرداخت: {str(e)}')
                return redirect('checkout:checkout_cancel')
        else:
            payment.status = 'cancelled'
            payment.save()
            
            messages.warning(request, 'پرداخت لغو شد.')
            return redirect('checkout:checkout_cancel')
    
    return redirect('core:home')


@csrf_exempt
def payment_callback(request, payment_id):
    """کالبک پرداخت"""
    payment = get_object_or_404(Payment, payment_id=payment_id)
    
    # این endpoint برای دریافت کالبک از درگاه‌های پرداخت استفاده می‌شود
    # بسته به درگاه پرداخت، پارامترهای مختلفی دریافت می‌شود
    
    return JsonResponse({'status': 'received'})


@login_required
@require_POST
@csrf_exempt
def refund_payment(request, payment_id):
    """مرجوع پرداخت"""
    payment = get_object_or_404(Payment, payment_id=payment_id)
    
    # بررسی دسترسی کاربر
    if payment.order.user != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'دسترسی غیرمجاز'})
    
    # بررسی امکان مرجوع
    if not payment.order.can_refund:
        return JsonResponse({'success': False, 'message': 'امکان مرجوع این سفارش وجود ندارد'})
    
    try:
        with transaction.atomic():
            # درخواست مرجوع از درگاه
            gateway = PaymentGateway()
            result = gateway.refund_payment(
                provider_name=payment.provider.slug,
                transaction_id=payment.provider_transaction_id,
                amount=payment.amount
            )
            
            if result['success']:
                # به‌روزرسانی وضعیت پرداخت
                payment.status = 'refunded'
                payment.save()
                
                # به‌روزرسانی وضعیت سفارش
                payment.order.payment_status = 'refunded'
                payment.order.status = 'refunded'
                payment.order.save()
                
                return JsonResponse({'success': True, 'message': 'مرجوع با موفقیت انجام شد'})
            else:
                return JsonResponse({'success': False, 'message': result['error']})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})