from django.contrib import admin
from .models import ModelCar, Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "marca", "get_models", "price", "stock")
    list_filter = ("category", "marca")
    search_fields = ("name",)

    def get_models(self, obj):
        return ", ".join([m.name for m in obj.compatible_models.all()])
    get_models.short_description = "Modelos Compatibles"

admin.site.register(ModelCar)
