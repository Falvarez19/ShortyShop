from django.urls import path
from .views import  en_construccion ,category_view ,about, home, products, product_detail, cart, add_product, edit_product, delete_product, product_list, add_to_cart, remove_from_cart, update_cart, checkout_mercadopago, pago_fallido, pago_exitoso
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("", home, name="home"),  # Página principal
    path("products/", products, name="products"),  # Página de productos
    path("products/<int:product_id>/", product_detail, name="product_detail"),  # Detalle de un producto
    path("cart/", cart, name="cart"),  # Carrito de compras
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),#añadir al carrito
    path("cart/remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
    path("cart/update/<int:item_id>/", update_cart, name="update_cart"),
    path("products/", product_list, name="product_list"),
    path("products/add/", add_product, name="add_product"),
    path("products/edit/<int:product_id>/", edit_product, name="edit_product"),
    path("products/delete/<int:product_id>/", delete_product, name="delete_product"),
    path("about/", about, name="about"),  # Nueva página "Sobre Nosotros"
    path("pago-exitoso/", pago_exitoso, name="pago_exitoso"),
    path("pago-fallido/", pago_fallido, name="pago_fallido"),
    path("checkout-mercadopago/", checkout_mercadopago, name="checkout_mercadopago"),
    path('categoria/<str:category_name>/<str:gender_name>/', category_view, name='category_view'),
    path('construccion/', en_construccion, name='en_construccion'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)