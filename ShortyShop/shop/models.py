from django.db import models
from django.conf import settings

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    description = models.TextField(verbose_name="Descripción", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock = models.PositiveIntegerField(verbose_name="Stock Disponible", default=0)
    image = models.ImageField(upload_to="products/", verbose_name="Imagen del Producto", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Ahora Product ya está definido antes
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
