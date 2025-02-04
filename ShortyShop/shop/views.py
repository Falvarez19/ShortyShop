from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from shop.models import Product
from django.contrib.auth.decorators import user_passes_test
from .models import Product
from .forms import ProductForm
import mercadopago
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from .models import Product 

# Página principal

def home(request):
    return render(request, "shop/home.html")

# Página de productos
def products(request):
    return render(request, "shop/products.html")

# Página de detalles de un producto
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

# Página del carrito de compras
@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, "shop/cart.html", {"cart": cart})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')
@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect("cart")


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == "POST":
        quantity = request.POST.get("quantity")
        cart_item.quantity = int(quantity) if quantity.isdigit() and int(quantity) > 0 else 1
        cart_item.save()

    return redirect("cart")


def is_admin(user):
    return user.is_authenticated and user.is_staff  # Solo administradores

#añadir producto
@user_passes_test(is_admin)
def add_product(request):
    categories = Product.objects.values('category').distinct()  # Obtiene las categorías únicas
    form = ProductForm()

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("product_list")

    return render(request, "shop/add_product.html", {"form": form, "categories": categories})



@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Product.objects.values_list('category', flat=True).distinct()  # Obtiene las categorías únicas

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_list")

    else:
        form = ProductForm(instance=product)

    return render(request, "shop/edit_product.html", {
        "form": form,
        "categories": categories,
    })


@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete()
        return redirect("product_list")

    return render(request, "shop/delete_product.html", {"product": product})

def product_list(request):
    products = Product.objects.all()  # Obtiene todos los productos
    return render(request, "shop/product_list.html", {"products": products})

def about(request):
    return render(request, "shop/about.html")
#Mercadopago 
def checkout_mercadopago(request):
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    cart = request.session.get('cart', {})
    items = []

    for product_id, product_data in cart.items():
        items.append({
            "title": product_data["name"],
            "quantity": product_data["quantity"],
            "currency_id": "ARS",  # Ajusta según el país
            "unit_price": float(product_data["price"])
        })

    preference_data = {
        "items": items,
        "back_urls": {
            "success": request.build_absolute_uri("/pago-exitoso/"),
            "failure": request.build_absolute_uri("/pago-fallido/"),
            "pending": request.build_absolute_uri("/pago-pendiente/")
        },
        "auto_return": "approved",
    }

    preference_response = sdk.preference().create(preference_data)
    preference_id = preference_response["response"]["id"]

    return JsonResponse({"preference_id": preference_id})

def pago_exitoso(request):
    return render(request, "shop/pago_exitoso.html")

def pago_fallido(request):
    return render(request, "shop/pago_fallido.html")


def category_view(request, category_name, gender_name):
    """Vista para mostrar productos según categoría y género"""
    products = Product.objects.filter(category=category_name, gender=gender_name)
    return render(request, "shop/category.html", {"products": products, "category": category_name, "gender": gender_name})



def en_construccion(request):
    return render(request, 'shop/en_construccion.html')

def error_403(request, exception):
    return render(request, "shop/403.html", status=403)