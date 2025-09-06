from .models import Cart


def cart(request):
    """اضافه کردن سبد خرید به context"""
    cart = None
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    elif request.session.session_key:
        cart, created = Cart.objects.get_or_create(session_id=request.session.session_key)
    
    return {
        'cart': cart,
    }