from django.contrib import admin
from .models import Product, CartItem
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'gender', 'price', 'stock', 'created_at')
    search_fields = ('name', 'category', 'gender')
    list_filter = ('category', 'gender')

admin.site.register(CartItem)