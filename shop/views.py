from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from .models import Cart, CartItem, Product, ModelCar, BRAND_CHOICES
from .forms import ProductForm


# Página principal
def home(request):
    categories = [
        ("Baterías", "Baterías"),
        ("Filtros de Aceite", "Filtros de Aceite"),
        ("Pastillas de Freno", "Pastillas de Freno"),
        ("Amortiguadores", "Amortiguadores"),
        ("Correas", "Correas"),
        ("Aceites", "Aceites"),
        ("Embragues", "Embragues"),
        ("Luces", "Luces"),
    ]
    
    brands = [
        "Chevrolet", "Ford", "Honda", "Mazda", "Mercedes",
        "Nissan", "Peugeot", "Renault", "Toyota", "Volkswagen"
    ]

    # Simulación de productos más vendidos y populares
    best_sellers = Product.objects.order_by('-stock')[:4]
    popular_products = Product.objects.order_by('-id')[:4]

    return render(request, "shop/home.html", {
        "categories": categories,
        "brands": brands,
        "best_sellers": best_sellers,
    })


# Filtrar productos por modelo de auto
def products_by_model(request, model_id):
    model = get_object_or_404(ModelCar, id=model_id)
    products = Product.objects.filter(compatible_models=model)
    return render(request, "shop/products.html", {"products": products, "model": model})

# Página de detalles de un producto
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

# Página del carrito de compras
@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    vendedores = [
        {"nombre": "Fernando Alvarez", "telefono": "+5491169544042"},
    ]

    return render(request, "shop/cart.html", {"cart": cart, "vendedores": vendedores})

# Agregar un producto al carrito
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')

# Eliminar un producto del carrito
@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect("cart")

# Actualizar cantidad en el carrito
@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == "POST":
        quantity = request.POST.get("quantity")
        cart_item.quantity = int(quantity) if quantity.isdigit() and int(quantity) > 0 else 1
        cart_item.save()

    return redirect("cart")

# Validar si el usuario es administrador
def is_admin(user):
    return user.is_authenticated and user.is_staff

# Agregar producto
@login_required
def add_product(request):
    if not request.user.is_staff:
        return redirect("home")

    categories = Product.CATEGORY_CHOICES
    brands = BRAND_CHOICES             # 👈 usa la constante global
    models = ModelCar.objects.all()

    if request.method == "POST":
        form = ProductForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            product.compatible_models.set(request.POST.getlist("compatible_models"))
            messages.success(request, "Producto agregado correctamente.")
            return redirect("product_list")
        else:
            messages.error(request, "Error al agregar el producto. Verifica los campos.")
    else:
        form = ProductForm()

    return render(request, "shop/add_product.html", {
        "form": form,
        "categories": categories,
        "brands": brands,
        "models": models
    })


#editar producto
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    CATEGORY_CHOICES = [("Accesorios", "Accesorios"), ("Repuestos", "Repuestos")]
    models = ModelCar.objects.all()
    brands = BRAND_CHOICES  # <-- AQUI

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            p = form.save(commit=False)
            p.category = request.POST.get("category")
            p.marca = request.POST.get("marca")  # <-- guardar marca
            p.save()
            selected_models = request.POST.getlist("compatible_models")
            p.compatible_models.set(selected_models or [])
            messages.success(request, "Producto actualizado correctamente")
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)

    return render(request, "shop/edit_product.html", {
        "form": form,
        "product": product,
        "models": models,
        "categories": CATEGORY_CHOICES,
        "brands": brands,  # <-- AQUI
    })

# Eliminar producto
@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete()
        return redirect("product_list")
    return render(request, "shop/delete_product.html", {"product": product})

# Lista de productos filtrados por modelo
def product_list(request, category_label=None):
    """Listado con filtros. Si category_label está presente, filtra por esa categoría."""
    model_id = request.GET.get('model')
    brand = request.GET.get('brand')
    sort = request.GET.get('sort')

    products = Product.objects.all()

    # Filtrar por categoría si viene seteada (pestañas)
    if category_label:
        products = products.filter(category__iexact=category_label)

    # Filtros de la barra lateral
    if brand:
        products = products.filter(marca=brand)
    elif model_id:
        products = products.filter(compatible_models__id=model_id)

    # Orden
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    # Modelos y marcas disponibles (acotadas por la categoría si corresponde)
    models = ModelCar.objects.filter(product__in=products).distinct()
    brands = (products.values_list('marca', flat=True).distinct().order_by('marca'))

    # Etiqueta de título para el template
    section = category_label or "Todos los Productos"

    return render(request, 'shop/product_list.html', {
        'products': products,
        'models': models,
        'brands': [(b, b) for b in brands],  # si tu template espera (key,label)
        'selected_model': model_id,
        'selected_brand': brand,
        'selected_sort': sort,
        'section': section,
    })

# Wrappers para las pestañas
def product_list_repuestos(request):
    return product_list(request, category_label='Repuestos')

def product_list_accesorios(request):
    return product_list(request, category_label='Accesorios')

#Lista de compras
@login_required
def mis_compras(request):
    # lógica para traer las compras reales del usuario
    return render(request, 'shop/mis_compras.html')

# Página "Acerca de"
def about(request):
    return render(request, "shop/about.html")

# Página en construcción
def en_construccion(request):
    return render(request, 'shop/en_construccion.html')

# Vista 403
def error_403(request, exception):
    return render(request, "shop/403.html", status=403)

def products_by_brand(request, marca):
    selected_model_id = (request.GET.get('model') or '').strip()

    base_qs = Product.objects.filter(marca=marca, stock__gt=0)
    products = base_qs
    if selected_model_id:
        products = products.filter(compatible_models__id=selected_model_id).distinct()

    # Modelos compatibles con esa marca (en base al catálogo con stock)
    modelos_con_stock = ModelCar.objects.filter(product__in=base_qs).distinct().order_by('name')

    return render(request, "shop/category.html", {
        "products": products,
        "brand": marca,
        "models": modelos_con_stock,
        "selected_model_id": selected_model_id,
    })


def products_by_category(request, category):
    selected_model_id = (request.GET.get('model') or '').strip()

    base_qs = Product.objects.filter(category=category, stock__gt=0)
    products = base_qs
    if selected_model_id:
        products = products.filter(compatible_models__id=selected_model_id).distinct()

    modelos_con_stock = ModelCar.objects.filter(product__in=base_qs).distinct().order_by('name')

    return render(request, "shop/category.html", {
        "products": products,
        "category": category,
        "models": modelos_con_stock,
        "selected_model_id": selected_model_id,
    })


def get_models(request):
    brand = (request.GET.get('brand') or '').strip()
    if not brand:
        return JsonResponse([], safe=False)
    qs = ModelCar.objects.filter(marca__iexact=brand).order_by('name').values('id', 'name')
    return JsonResponse(list(qs), safe=False)

#vista de accesorios
def accessories(request):
    brand = request.GET.get('brand')
    model_id = request.GET.get('model')
    sort = request.GET.get('sort')

    products = Product.objects.filter(category__iexact='Accesorios', stock__gt=0)
    if brand:
        products = products.filter(marca=brand)
    if model_id:
        products = products.filter(compatible_models__id=model_id)
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    models = (ModelCar.objects
              .filter(product__category__iexact='Accesorios')
              .distinct())
    if brand:
        models = models.filter(product__marca=brand).distinct()

    brands = (Product.objects
              .filter(category__iexact='Accesorios')
              .values_list('marca', flat=True)
              .distinct().order_by('marca'))

    return render(request, 'shop/product_list.html', {
        'products': products,
        'models': models,
        'brands': brands,
        'selected_model': model_id,
        'selected_brand': brand,
        'selected_sort': sort,
        'section': 'Accesorios', 
    })