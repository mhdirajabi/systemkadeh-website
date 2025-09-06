from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Order, OrderItem, ShippingMethod
from apps.cart.models import Cart, CartItem
from apps.payments.models import Payment, PaymentProvider
from apps.payments.backends import PaymentGateway


class CheckoutView(TemplateView):
    """صفحه تسویه حساب"""
    template_name = 'checkout/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'برای تسویه حساب باید وارد شوید.')
            return redirect('accounts:login')
        
        cart = Cart.objects.filter(user=self.request.user).first()
        if not cart or cart.is_empty:
            messages.error(self.request, 'سبد خرید شما خالی است.')
            return redirect('cart:cart')
        
        context['cart'] = cart
        context['addresses'] = self.request.user.addresses.all()
        context['shipping_methods'] = ShippingMethod.objects.filter(is_active=True)
        
        return context
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or cart.is_empty:
            messages.error(request, 'سبد خرید شما خالی است.')
            return redirect('cart:cart')
        
        # دریافت اطلاعات فرم
        shipping_address_id = request.POST.get('shipping_address')
        shipping_method_id = request.POST.get('shipping_method')
        payment_method = request.POST.get('payment_method')
        
        try:
            with transaction.atomic():
                # ایجاد سفارش
                order = self.create_order(request, cart, shipping_address_id, shipping_method_id)
                
                # ایجاد آیتم‌های سفارش
                self.create_order_items(order, cart)
                
                # ایجاد پرداخت
                payment = self.create_payment(order, payment_method)
                
                # پاک کردن سبد خرید
                cart.delete()
                
                # هدایت به درگاه پرداخت
                if payment_method == 'online':
                    return self.redirect_to_payment_gateway(payment)
                else:
                    messages.success(request, 'سفارش شما با موفقیت ثبت شد.')
                    return redirect('checkout:checkout_success', order_number=order.order_number)
        
        except Exception as e:
            messages.error(request, f'خطا در ثبت سفارش: {str(e)}')
            return redirect('checkout:checkout')
    
    def create_order(self, request, cart, shipping_address_id, shipping_method_id):
        """ایجاد سفارش"""
        shipping_address = get_object_or_404(
            request.user.addresses,
            id=shipping_address_id
        )
        
        shipping_method = get_object_or_404(
            ShippingMethod,
            id=shipping_method_id,
            is_active=True
        )
        
        # محاسبه هزینه ارسال
        shipping_cost = shipping_method.calculate_cost(cart.total_price)
        
        # محاسبه تخفیف
        discount_amount = 0
        if 'applied_coupon' in request.session:
            discount_amount = request.session['applied_coupon']['discount']
        
        # محاسبه مجموع کل
        total_amount = cart.total_price + shipping_cost - discount_amount
        
        order = Order.objects.create(
            user=request.user,
            subtotal=cart.total_price,
            shipping_cost=shipping_cost,
            discount_amount=discount_amount,
            total_amount=total_amount,
            shipping_name=shipping_address.title,
            shipping_phone=str(shipping_address.phone),
            shipping_address=shipping_address.address,
            shipping_city=shipping_address.city,
            shipping_province=shipping_address.province,
            shipping_postal_code=shipping_address.postal_code
        )
        
        return order
    
    def create_order_items(self, order, cart):
        """ایجاد آیتم‌های سفارش"""
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                price=cart_item.price,
                total_price=cart_item.total_price
            )
    
    def create_payment(self, order, payment_method):
        """ایجاد پرداخت"""
        provider = PaymentProvider.objects.filter(
            is_active=True,
            provider_type='gateway' if payment_method == 'online' else 'installment'
        ).first()
        
        if not provider:
            raise Exception('ارائه‌دهنده پرداخت یافت نشد')
        
        payment = Payment.objects.create(
            order=order,
            provider=provider,
            payment_type=payment_method,
            amount=order.total_amount
        )
        
        return payment
    
    def redirect_to_payment_gateway(self, payment):
        """هدایت به درگاه پرداخت"""
        gateway = PaymentGateway()
        
        result = gateway.create_payment(
            provider_name=payment.provider.slug,
            amount=payment.amount,
            order_number=payment.order.order_number,
            callback_url=f'/payments/verify/{payment.payment_id}/',
            description=f'پرداخت سفارش {payment.order.order_number}'
        )
        
        if result['success']:
            payment.provider_transaction_id = result.get('authority') or result.get('track_id')
            payment.status = 'processing'
            payment.save()
            
            return redirect(result['payment_url'])
        else:
            raise Exception(result['error'])


class CheckoutSuccessView(TemplateView):
    """صفحه موفقیت آمیز بودن پرداخت"""
    template_name = 'checkout/success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_number = kwargs.get('order_number')
        context['order'] = get_object_or_404(Order, order_number=order_number)
        return context


class CheckoutCancelView(TemplateView):
    """صفحه لغو پرداخت"""
    template_name = 'checkout/cancel.html'