from django.urls import path
from .views import home, products, product_detail, cart

urlpatterns = [
    path("", home, name="home"),  # Página principal
    path("products/", products, name="products"),  # Página de productos
    path("products/<int:product_id>/", product_detail, name="product_detail"),  # Detalle de un producto
    path("cart/", cart, name="cart"),  # Carrito de compras
]
