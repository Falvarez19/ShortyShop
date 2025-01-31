from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from shop.models import Product
from django.contrib.auth.decorators import user_passes_test
from .models import Product
from .forms import ProductForm

# Página principal
def home(request):
    return render(request, "shop/home.html")

# Página de productos
def products(request):
    return render(request, "shop/products.html")

# Página de detalles de un producto
def product_detail(request, product_id):
    return render(request, "shop/product_detail.html", {"product_id": product_id})

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

    return redirect("cart")


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


@user_passes_test(is_admin)
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm()

    return render(request, "shop/add_product.html", {"form": form})


@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)

    return render(request, "shop/edit_product.html", {"form": form, "product": product})


@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete()
        return redirect("product_list")

    return render(request, "shop/delete_product.html", {"product": product})

def product_list(request):
    products = Product.objects.all()
    return render(request, "shop/product_list.html", {"products": products})

from django.shortcuts import render

def about(request):
    return render(request, "shop/about.html")