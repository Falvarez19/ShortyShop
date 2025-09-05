from django.urls import path
from .views import  list_models , admin_models, delete_model, add_model ,product_list_repuestos, product_list_accesorios, get_models ,mis_compras, products_by_category, products_by_brand ,en_construccion, about, cart_view, add_product, edit_product, delete_product, product_list, add_to_cart, remove_from_cart, update_cart,  product_detail, home, products_by_model
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
#Pestañas principales
    path("", home, name="home"),
    path("about/", about, name="about"),
    path("marca/<str:marca>/", products_by_brand, name="products_by_brand"),
    path("categoria/<str:category>/", products_by_category, name="products_by_category"),
    path('mis_compras/', mis_compras, name='mis_compras'),
    path('construccion/', en_construccion, name='en_construccion'),
    path("repuestos/", product_list_repuestos, name="repuestos"),
    path("accesorios/", product_list_accesorios, name="accesorios"),
#carrito
    path("cart/", cart_view, name="cart"),  
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path("cart/remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
    path("cart/update/<int:item_id>/", update_cart, name="update_cart"),
#APIs modelos
    path("api/models/add/", add_model, name="add_model"),
    path('get-models/', get_models, name='get_models'),
    path("api/models/list/", list_models, name="api_models_list"),
    path("api/models/delete/<int:pk>/", delete_model, name="delete_model"),
#Panel admin
    path("panel_admin/modelos/", admin_models, name="admin_models"),
    path("panel_admin/add_product/", add_product, name="add_product"),
    path("panel_admin/edit_product/<int:product_id>/", edit_product, name="edit_product"),
    path("panel_admin/products/", product_list, name="product_list"),
    path('get_models/', get_models, name='get_models'),
#editar productos
    path("products/model/<int:model_id>/", products_by_model, name="products_by_model"),
    path("products/<int:product_id>/", product_detail, name="product_detail"),
    path("products/delete/<int:product_id>/", delete_product, name="delete_product"),

  
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

