from .models import Cart
from django.contrib.sessions.models import Session


def cart(request):
    """اضافه کردن سبد خرید به context"""
    cart = None
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        try:
            session = Session.objects.get(session_key=request.session.session_key)
            cart, _ = Cart.objects.get_or_create(session=session)
        except Session.DoesNotExist:
            cart = None
    
    return {
        'cart': cart,
    }