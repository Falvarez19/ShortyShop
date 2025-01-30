# shop/views.py

from django.shortcuts import render

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
def cart(request):
    return render(request, "shop/cart.html")
