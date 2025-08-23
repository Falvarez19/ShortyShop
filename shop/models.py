from django.conf import settings
from django.db import models

# --- Usar las mismas marcas en todo el proyecto ---
BRAND_CHOICES = [
    ("Chevrolet", "Chevrolet"),
    ("Ford", "Ford"),
    ("Volkswagen", "Volkswagen"),
    ("Toyota", "Toyota"),
    ("Renault", "Renault"),
    ("Peugeot", "Peugeot"),
    ("Nissan", "Nissan"),
    ("Mazda", "Mazda"),
    ("Mercedes", "Mercedes"),
    ("Honda", "Honda"),
]

# Modelo de autos (cada modelo pertenece a una marca)
class ModelCar(models.Model):
    name = models.CharField(max_length=50, verbose_name="Modelo")
    # Nuevo: para poder filtrar/crear por marca
    marca = models.CharField(max_length=50, choices=BRAND_CHOICES, verbose_name="Marca", null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["marca", "name"], name="uniq_model_per_brand")
        ]

    def __str__(self):
        return f"{self.name} ({self.marca})" if self.marca else self.name


# Modelo de productos
class Product(models.Model):
    CATEGORY_CHOICES = [
        ("Accesorios", "Accesorios"),
        ("Repuestos", "Repuestos"),
    ]

    name = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Categoría")
    marca = models.CharField(max_length=50, choices=BRAND_CHOICES, verbose_name="Marca")
    compatible_models = models.ManyToManyField(ModelCar, verbose_name="Modelos compatibles")
    description = models.TextField(verbose_name="Descripción", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock = models.PositiveIntegerField(verbose_name="Stock Disponible", default=0)
    image = models.ImageField(upload_to="products/", verbose_name="Imagen del Producto", blank=True, null=True)

    def __str__(self):
        modelos = ", ".join([model.name for model in self.compatible_models.all()])
        return f"{self.name} - {self.category} ({self.marca}) [{modelos}]"


# Modelo del carrito de compras
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Carrito de {self.user}" if self.user else "Carrito Anónimo"


# Modelo de ítems dentro del carrito
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Carrito {self.cart.user})"
