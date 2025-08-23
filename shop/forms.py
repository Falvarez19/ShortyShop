from django import forms
from .models import Product, ModelCar


class ProductForm(forms.ModelForm):
    compatible_models = forms.ModelMultipleChoiceField(
        queryset=ModelCar.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Product
        fields = ["name", "category", "marca", "description", "price", "stock", "image", "compatible_models"]

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"