from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.db import transaction
from .models import Cart, CartItem, Coupon
from apps.catalog.models import Product, ProductVariant
from .forms import CouponForm


class CartView(TemplateView):
    """صفحه سبد خرید"""
    template_name = 'cart/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['coupon_form'] = CouponForm()
        return context


@require_POST
@csrf_exempt
def add_to_cart(request):
    """افزودن محصول به سبد خرید"""
    try:
        product_id = request.POST.get('product_id')
        variant_id = request.POST.get('variant_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if not product_id:
            return JsonResponse({'success': False, 'message': 'محصول یافت نشد.'})
        
        product = get_object_or_404(Product, id=product_id, status='active')
        variant = None
        
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product, is_active=True)
        
        # بررسی موجودی (فقط اعتبارسنجی، بدون کاهش موجودی در این مرحله)
        if product.track_inventory:
            available_stock = variant.stock_quantity if variant else product.stock_quantity
            if available_stock < quantity:
                return JsonResponse({'success': False, 'message': 'موجودی کافی نیست'})
        
        # دریافت یا ایجاد سبد خرید
        cart = get_cart(request)
        
        # بررسی وجود آیتم در سبد
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'محصول به سبد خرید اضافه شد.',
            'cart_total': cart.total_items,
            'cart_price': cart.total_price
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
@csrf_exempt
def update_cart_item(request, item_id):
    """به‌روزرسانی آیتم سبد خرید"""
    try:
        cart_item = get_object_or_404(CartItem, id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            return remove_from_cart(request, item_id)
        
        # بررسی موجودی (بدون تغییر موجودی)
        if cart_item.product.track_inventory:
            available_stock = cart_item.variant.stock_quantity if cart_item.variant else cart_item.product.stock_quantity
            if available_stock < quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'موجودی کافی نیست. موجودی: {available_stock}'
                })
        
        old_quantity = cart_item.quantity
        cart_item.quantity = quantity
        cart_item.save()
        
        # عدم تغییر موجودی در این مرحله؛ موجودی در مرحله تسویه کم می‌شود
        
        return JsonResponse({
            'success': True,
            'message': 'سبد خرید به‌روزرسانی شد.',
            'item_total': cart_item.total_price,
            'cart_total': cart_item.cart.total_items,
            'cart_price': cart_item.cart.total_price
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
@csrf_exempt
def remove_from_cart(request, item_id):
    """حذف آیتم از سبد خرید"""
    try:
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        # عدم دستکاری موجودی هنگام حذف از سبد
        
        cart_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'محصول از سبد خرید حذف شد.',
            'cart_total': cart_item.cart.total_items,
            'cart_price': cart_item.cart.total_price
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
@csrf_exempt
def apply_coupon(request):
    """اعمال کوپن تخفیف"""
    try:
        coupon_code = request.POST.get('coupon_code', '').strip().upper()
        
        if not coupon_code:
            return JsonResponse({'success': False, 'message': 'کد کوپن الزامی است.'})
        
        cart = get_cart(request)
        if cart.is_empty:
            return JsonResponse({'success': False, 'message': 'سبد خرید خالی است.'})
        
        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'کوپن یافت نشد.'})
        
        can_use, message = coupon.can_use(request.user, cart.total_price)
        if not can_use:
            return JsonResponse({'success': False, 'message': message})
        
        discount = coupon.calculate_discount(cart.total_price)
        
        # ذخیره کوپن در session
        request.session['applied_coupon'] = {
            'code': coupon.code,
            'discount': float(discount),
            'type': coupon.coupon_type
        }
        
        return JsonResponse({
            'success': True,
            'message': 'کوپن با موفقیت اعمال شد.',
            'discount': discount,
            'new_total': cart.total_price - discount
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
@csrf_exempt
def remove_coupon(request):
    """حذف کوپن تخفیف"""
    try:
        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']
            return JsonResponse({
                'success': True,
                'message': 'کوپن حذف شد.'
            })
        
        return JsonResponse({'success': False, 'message': 'کوپنی اعمال نشده است.'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def get_cart(request):
    """دریافت یا ایجاد سبد خرید"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_id=request.session.session_key)
    
    return cart


@login_required
def transfer_cart(request):
    """انتقال سبد خرید از session به کاربر"""
    if not request.session.session_key:
        return
    
    try:
        session_cart = Cart.objects.filter(session_id=request.session.session_key).first()
        if not session_cart:
            return
        
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        
        # انتقال آیتم‌ها
        for item in session_cart.items.all():
            existing_item = user_cart.items.filter(
                product=item.product,
                variant=item.variant
            ).first()
            
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                item.cart = user_cart
                item.save()
        
        # حذف سبد session
        session_cart.delete()
        
    except Exception as e:
        pass  # خطا را نادیده بگیر