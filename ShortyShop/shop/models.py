from django.db import models
from django.conf import settings

class Product(models.Model):
    CATEGORY_CHOICES = [
        ("Zapatillas", "Zapatillas"),
        ("Ropa", "Ropa"),
        ("Accesorios", "Accesorios"),
    ]
    
    GENDER_CHOICES = [
        ("Hombre", "Hombre"),
        ("Mujer", "Mujer"),
        ("Niños", "Niños"),
        ("Unisex", "Unisex"),
    ]

    name = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    description = models.TextField(verbose_name="Descripción", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock = models.PositiveIntegerField(verbose_name="Stock Disponible", default=0)
    image = models.ImageField(upload_to="products/", verbose_name="Imagen del Producto", blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Categoría", default="Zapatillas")
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES, verbose_name="Género", default="Unisex")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.name} - {self.category} ({self.gender})"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("product_detail", kwargs={"pk": self.pk})


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Carrito de {self.user}" if self.user else "Carrito Anónimo"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Carrito {self.cart.user})"