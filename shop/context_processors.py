# shop/context_processors.py
from django.db.models import Sum
from .models import Cart, CartItem

def cart_counter(request):
    """Devuelve el total de unidades en el carrito para el badge global."""
    if not request.user.is_authenticated:
        return {"cart_count": 0}

    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return {"cart_count": 0}

    total = (
        CartItem.objects.filter(cart=cart).aggregate(total=Sum("quantity"))["total"]
        or 0
    )
    return {"cart_count": total}
