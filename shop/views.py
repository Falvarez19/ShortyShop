from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Cart, CartItem, Product, ModelCar, BRAND_CHOICES
from .forms import ProductForm
from django.views.decorators.http import require_POST
from django.db.models import F
from django.utils.http import url_has_allowed_host_and_scheme
import json
from django.urls import reverse


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
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Acepta "quantity" o "qty" (por compatibilidad)
    try:
        qty = int(request.POST.get("quantity") or request.POST.get("qty") or 1)
    except ValueError:
        qty = 1
    qty = max(qty, 1)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": 0})
    item.quantity = (item.quantity or 0) + qty
    item.save()

    messages.success(request, f"“{product.name}” agregado al carrito.")

    # Volver a donde estábamos
    next_url = (
        request.POST.get("next")
        or request.META.get("HTTP_REFERER")
        or reverse("product_detail", args=[product_id])
    )
    return redirect(next_url)

# Eliminar un producto del carrito
@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect("cart")

# Actualizar cantidad en el carrito
@login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    # Sanitizar cantidad
    try:
        qty = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        qty = 1
    qty = max(1, qty)

    item.quantity = qty
    item.save()

    cart = item.cart
    cart_total = sum(ci.product.price * ci.quantity for ci in cart.items.all())
    cart_count = sum(ci.quantity for ci in cart.items.all())

    # Si viene de fetch() (X-Requested-With), respondemos JSON y no recargamos
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "item_id": item.id,
            "item_total": float(item.product.price * item.quantity),
            "cart_total": float(cart_total),
            "cart_count": cart_count,
        })

    # Fallback para submits normales
    return redirect("cart")

def cart_counter(request):
    count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Usa el related_name que tengas; si no definiste, es cartitem_set
        qs = getattr(cart, "items", getattr(cart, "cartitem_set"))
        count = qs.aggregate(total=Sum("quantity"))["total"] or 0
    return {"cart_count": count}

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
from django.shortcuts import render
from .models import Product, ModelCar

def product_list(request, category_label=None):
    brand    = request.GET.get('brand', '') or ''
    model_id = request.GET.get('model', '') or ''
    sort     = request.GET.get('sort', 'price_asc') or 'price_asc'

    # 1) Base: sólo categoría (para pestañas)
    base_qs = Product.objects.all()
    if category_label:
        base_qs = base_qs.filter(category__iexact=category_label)

    # 2) Facetas (NO usar el queryset ya filtrado por marca/modelo)
    #    Marcas presentes en la categoría (si hay)
    brands_in_db = base_qs.values_list('marca', flat=True).distinct()
    brands = [(b, b) for b in brands_in_db]

    #    Modelos: si hay marca elegida, modelos de esa marca en la categoría;
    #    si no, todos los modelos de la categoría.
    if brand:
        models = (ModelCar.objects
                  .filter(marca=brand, product__in=base_qs)
                  .distinct().order_by('name'))
    else:
        models = (ModelCar.objects
                  .filter(product__in=base_qs)
                  .distinct().order_by('name'))

    # 3) Ahora sí, aplicar filtros activos sobre una copia del base_qs
    products = base_qs
    if brand:
        products = products.filter(marca=brand)
    if model_id:
        products = products.filter(compatible_models__id=model_id)

    # 4) Orden
    if sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'price_asc':
        products = products.order_by('price')
    else:
        # por si agregás más criterios
        products = products.order_by('name')

    section = category_label or "Todos los Productos"

    return render(request, 'shop/product_list.html', {
        'products': products,
        'models': models,                # <- el template ya usa 'models'
        'brands': brands,                # [(value, label)]
        'selected_model': model_id,
        'selected_brand': brand,
        'selected_sort': sort,
        'section': section,
    })

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


# --- Panel Admin de Modelos ---
@staff_member_required
def admin_models(request):
    if request.method == "POST":
        brand = request.POST.get("brand")
        name  = (request.POST.get("name") or "").strip()
        if brand and name:
            ModelCar.objects.get_or_create(marca=brand, name=name)
        return redirect(f"{reverse('admin_models')}?brand={brand or ''}")

    filter_brand = request.GET.get("brand", "")
    qs = ModelCar.objects.all().order_by("marca", "name")
    if filter_brand:
        qs = qs.filter(marca=filter_brand)

    return render(request, "shop/admin_models.html", {
        "brands": BRAND_CHOICES,
        "selected_brand": filter_brand,
        "models": qs,
    })

# --- API: listar (opcional si lo usas vía fetch) ---
@staff_member_required
def list_models(request):
    brand = (request.GET.get("brand") or "").strip()
    q = (request.GET.get("q") or "").strip()

    qs = ModelCar.objects.all()
    if brand:
        qs = qs.filter(marca__iexact=brand)
    if q:
        qs = qs.filter(name__icontains=q)

    data = [{"id": m.id, "name": m.name, "brand": m.marca} for m in qs.order_by("name")[:500]]
    return JsonResponse({"ok": True, "results": data})

# --- API: alta de modelo (deja **sólo esta**; elimina cualquier duplicada) ---

@require_POST
@staff_member_required
def add_model(request):
    # JSON (AJAX)
    if request.content_type and "application/json" in request.content_type.lower():
        try:
            data = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"ok": False, "error": "JSON inválido."}, status=400)
        brand = (data.get("brand") or "").strip()
        name  = (data.get("name") or "").strip()
        if not brand or not name:
            return JsonResponse({"ok": False, "error": "Faltan datos."}, status=400)
        obj, created = ModelCar.objects.get_or_create(
            marca__iexact=brand, name__iexact=name,
            defaults={"marca": brand, "name": name}
        )
        return JsonResponse({"ok": True, "id": obj.id, "name": obj.name, "created": created})

    # Form POST normal
    brand = (request.POST.get("brand") or "").strip()
    name  = (request.POST.get("name") or "").strip()
    if not brand or not name:
        messages.error(request, "Completá marca y nombre.")
        return redirect(f"{reverse('admin_models')}?brand={brand}")

    obj, created = ModelCar.objects.get_or_create(
        marca__iexact=brand, name__iexact=name,
        defaults={"marca": brand, "name": name}
    )
    if created:
        messages.success(request, f"Modelo “{obj.name}” creado.")
    else:
        messages.info(request, f"El modelo “{obj.name}” ya existía.")

    return redirect(f"{reverse('admin_models')}?brand={brand}")
# --- API: borrar modelo ---
@staff_member_required
@require_POST
def delete_model(request, pk):
    """Borra un modelo desde el panel y vuelve con mensajes (sin JSON)."""
    # preservar el filtro actual de marca si lo hubiera
    brand_filter = request.GET.get("brand", "")

    try:
        m = ModelCar.objects.get(pk=pk)
    except ModelCar.DoesNotExist:
        messages.error(request, "El modelo ya no existe.")
    else:
        in_use = Product.objects.filter(compatible_models=m).count()
        if in_use:
            messages.error(
                request,
                f"No se puede eliminar: está en uso por {in_use} producto(s)."
            )
        else:
            m.delete()
            messages.success(request, "Modelo eliminado correctamente.")

    url = reverse("admin_models")
    if brand_filter:
        url += f"?brand={brand_filter}"
    return redirect(admin_models)