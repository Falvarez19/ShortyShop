# ===============================
# ============ IMPORTS ==========
# ===============================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum  # usado en cart_counter
# from django.db.models import F   # si lo necesitás, descomentá

from .models import Cart, CartItem, Product, ModelCar, BRAND_CHOICES
from .forms import ProductForm
import json


# ==========================================================
# =====================   #CART  ===========================
# ==========================================================

# Página del carrito (muestra items, totales y botones de acción)
@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    vendedores = [{"nombre": "Fernando Alvarez", "telefono": "+5491169544042"}]
    return render(request, "shop/cart.html", {"cart": cart, "vendedores": vendedores})


# Agrega un producto al carrito (acepta quantity/qty) y vuelve a la página previa
@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    try:
        qty = int(request.POST.get("quantity") or request.POST.get("qty") or 1)
    except ValueError:
        qty = 1
    qty = max(qty, 1)

    item, _ = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": 0})
    item.quantity = (item.quantity or 0) + qty
    item.save()

    messages.success(request, f"“{product.name}” agregado al carrito.")

    next_url = (
        request.POST.get("next")
        or request.META.get("HTTP_REFERER")
        or reverse("product_detail", args=[product_id])
    )
    return redirect(next_url)


# Elimina un ítem del carrito por ID
@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect("cart")


# Actualiza la cantidad de un ítem; si es AJAX devuelve JSON con totales
@login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

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

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "item_id": item.id,
            "item_total": float(item.product.price * item.quantity),
            "cart_total": float(cart_total),
            "cart_count": cart_count,
        })

    return redirect("cart")


# Context processor para el badge del carrito (total de unidades)
def cart_counter(request):
    count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        qs = getattr(cart, "items", getattr(cart, "cartitem_set"))
        count = qs.aggregate(total=Sum("quantity"))["total"] or 0
    return {"cart_count": count}


# ==========================================================
# ==============   #PÁGINAS PRINCIPALES  ===================
# =================== (Catálogo / UI) ======================
# ==========================================================

# Página de inicio (categorías, marcas, destacados)
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
    brands = ["Chevrolet", "Ford", "Honda", "Mazda", "Mercedes",
              "Nissan", "Peugeot", "Renault", "Toyota", "Volkswagen"]

    best_sellers = Product.objects.order_by("-stock")[:4]
    return render(request, "shop/home.html", {
        "categories": categories,
        "brands": brands,
        "best_sellers": best_sellers,
    })


# Detalle de un producto
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "shop/product_detail.html", {"product": product})


# Lista productos compatibles con un modelo (por ID)
def products_by_model(request, model_id):
    model = get_object_or_404(ModelCar, id=model_id)
    products = Product.objects.filter(compatible_models=model)
    return render(request, "shop/products.html", {"products": products, "model": model})


# Listado general con filtros de marca/modelo y orden (opcional por categoría)
def product_list(request, category_label=None):
    brand    = request.GET.get('brand', '') or ''
    model_id = request.GET.get('model', '') or ''
    sort     = request.GET.get('sort', 'price_asc') or 'price_asc'

    base_qs = Product.objects.all()
    if category_label:
        base_qs = base_qs.filter(category__iexact=category_label)

    # Facetas (no usar el queryset ya filtrado)
    brands_in_db = base_qs.values_list('marca', flat=True).distinct()
    brands = [(b, b) for b in brands_in_db]

    if brand:
        models = (ModelCar.objects
                  .filter(marca=brand, product__in=base_qs)
                  .distinct().order_by('name'))
    else:
        models = (ModelCar.objects
                  .filter(product__in=base_qs)
                  .distinct().order_by('name'))

    # Aplicar filtros activos
    products = base_qs
    if brand:
        products = products.filter(marca=brand)
    if model_id:
        products = products.filter(compatible_models__id=model_id)

    # Orden
    if sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'price_asc':
        products = products.order_by('price')
    else:
        products = products.order_by('name')

    section = category_label or "Todos los Productos"

    return render(request, 'shop/product_list.html', {
        'products': products,
        'models': models,
        'brands': brands,
        'selected_model': model_id,
        'selected_brand': brand,
        'selected_sort': sort,
        'section': section,
    })


# Atajo de pestaña: repuestos (reusa product_list)
def product_list_repuestos(request):
    return product_list(request, category_label='Repuestos')


# Atajo de pestaña: accesorios (reusa product_list)
def product_list_accesorios(request):
    return product_list(request, category_label='Accesorios')


# Listado por marca con filtro opcional de modelo (solo con stock)
def products_by_brand(request, marca):
    selected_model_id = (request.GET.get('model') or '').strip()

    base_qs = Product.objects.filter(marca=marca, stock__gt=0)
    products = base_qs
    if selected_model_id:
        products = products.filter(compatible_models__id=selected_model_id).distinct()

    modelos_con_stock = ModelCar.objects.filter(product__in=base_qs).distinct().order_by('name')
    return render(request, "shop/category.html", {
        "products": products,
        "brand": marca,
        "models": modelos_con_stock,
        "selected_model_id": selected_model_id,
    })


# Listado por categoría con filtro opcional de modelo (solo con stock)
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


# API simple: devuelve modelos por marca (para selects dinámicos)
def get_models(request):
    brand = (request.GET.get('brand') or '').strip()
    if not brand:
        return JsonResponse([], safe=False)
    qs = ModelCar.objects.filter(marca__iexact=brand).order_by('name').values('id', 'name')
    return JsonResponse(list(qs), safe=False)


# Sección “Accesorios” usando product_list.html con filtros
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


# Mis compras (placeholder para historial real)
@login_required
def mis_compras(request):
    return render(request, 'shop/mis_compras.html')


# Página “Sobre nosotros”
def about(request):
    return render(request, "shop/about.html")


# Página genérica “en construcción”
def en_construccion(request):
    return render(request, 'shop/en_construccion.html')


# Handler de error 403 (permite template custom)
def error_403(request, exception):
    return render(request, "shop/403.html", status=403)


# ==========================================================
# ===============   #ADMIN PRODUCTOS  ======================
# ==========================================================

# Helper: determina si el usuario es admin/staff
def is_admin(user):
    return user.is_authenticated and user.is_staff


# Alta de producto (solo staff) con selección de modelos compatibles
@login_required
def add_product(request):
    if not request.user.is_staff:
        return redirect("home")

    categories = Product.CATEGORY_CHOICES
    brands = BRAND_CHOICES
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


# Edición de producto (categoría, marca, modelos compatibles)
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    CATEGORY_CHOICES = [("Accesorios", "Accesorios"), ("Repuestos", "Repuestos")]
    models = ModelCar.objects.all()
    brands = BRAND_CHOICES

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            p = form.save(commit=False)
            p.category = request.POST.get("category")
            p.marca = request.POST.get("marca")
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
        "brands": brands,
    })


# Elimina un producto (solo admin) con confirmación por POST
@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete()
        return redirect("product_list")
    return render(request, "shop/delete_product.html", {"product": product})


# ==========================================================
# ===============   #ADMIN MODELOS  ========================
# ==========================================================

# Panel de modelos (listar/filtrar por marca y alta simple por POST)
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


# API: lista modelos (filtros por marca y búsqueda por nombre)
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


# API: alta de modelo (acepta JSON para AJAX y form normal)
@require_POST
@staff_member_required
def add_model(request):
    # AJAX JSON
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

    # Form normal
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


# Elimina un modelo (si no está en uso) y vuelve filtrando por la marca actual
@staff_member_required
@require_POST
def delete_model(request, pk):
    brand_filter = request.GET.get("brand", "")

    try:
        m = ModelCar.objects.get(pk=pk)
    except ModelCar.DoesNotExist:
        messages.error(request, "El modelo ya no existe.")
    else:
        in_use = Product.objects.filter(compatible_models=m).count()
        if in_use:
            messages.error(request, f"No se puede eliminar: está en uso por {in_use} producto(s).")
        else:
            m.delete()
            messages.success(request, "Modelo eliminado correctamente.")

    url = reverse("admin_models")
    if brand_filter:
        url += f"?brand={brand_filter}"
    return redirect(url)
