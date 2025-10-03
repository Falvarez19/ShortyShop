# ShortyShop — Documentación Técnica

Este documento complementa el README con detalles de **arquitectura**, **frontend**, **APIs** y un **guion** para el video de demo.

---

## 1) Modelos y vistas

### Modelos principales
- **Product**: nombre, marca (`choices`), precio, stock, imagen, descripción, relaciones M2M con `ModelCar` (compatibilidades).
- **ModelCar**: `brand` (choice) + `name` (texto).

### Vistas relevantes
- **Listado** (`product_list`) con filtros por `brand` y `model`, y orden por precio.
- **Detalle** (`product_detail`) muestra precio con miles, stock y modelos compatibles.
- **Carrito** (`cart_view`): renderiza items; **`update_cart`** actualiza cantidad (devuelve JSON si `XMLHttpRequest`).
- **Admin modelos** (`admin_models`): listar, filtrar, agregar y eliminar modelos.

---

## 2) Rutas / URLs

```python
from django.urls import path
from shop import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:id>/', views.edit_product, name='edit_product'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('panel_admin/modelos/', views.admin_models, name='admin_models'),
    path('panel_admin/modelos/delete/<int:pk>/', views.delete_model, name='delete_model'),

    path('get-models/', views.get_models, name='get_models'),
    path('api/models/add/', views.add_model, name='add_model'),
]
```

---

## 3) Frontend

### 3.1 CSS (`static/shop/css/style.css`)
- **Tokens**: `--brand-primary`, `--brand-neutral-*`, radios, sombras, etc.
- **Componentes**: navbar, cards, brand slider, sidebar filtros, product rows, botones.
- **Modo oscuro**: todo bajo `:root[data-theme="dark"] { ... }` (navbar, cards, tablas, inputs, dropdowns, footer, etc.).
- **Accesibilidad**: contrastes en badges y estados hover/focus.

> Si algo se ve “muy oscuro” en light o viceversa, asegurate de no tener utilitarios Bootstrap que fuercen colores (p.ej. `.text-dark`) sin sus equivalentes para dark. El CSS ya hace overrides comunes.

### 3.2 JS (`static/shop/js/script.js`)
- **Helper CSRF** global (`getCSRFToken`).
- Efectos de navbar y overlay en menú móvil.
- **Previsualización** de imagen en alta/edición.
- **Modelos dinámicos**: al cambiar `marca`, llama a `/get-models/` y rellena un grid de checkboxes.
- **Alta rápida** de modelo (`/api/models/add/`) con `fetch` + `X-CSRFToken`.
- Contadores de seleccionados/total + **búsqueda local** por texto y **select all/clear**.
- **Carrito AJAX**: oculta botón *Actualizar* y hace `POST` al cambiar cantidad; espera JSON:
  ```json
  {"item_total": 12345.0, "cart_total": 45678.0, "cart_count": 3}
  ```
  Aplica formateo `Intl.NumberFormat('es-AR', { style:'currency', currency:'ARS' })` en los totales.
- **Theme toggle**: coloca `data-theme="dark"`/`"light"` en `<html>` y guarda elección en `localStorage`.

> (Opcional) Si usás botón “Enviar a WhatsApp” en carrito, añadí un handler a `.send-whatsapp` que arme el mensaje con items y `window.open(https://wa.me/...)` (el snippet original sirve tal cual).

### 3.3 Templates (notas)
- En templates con dinero: `{% load l10n humanize %}` y usar `{{ value|floatformat:2|localize }}`.
- Para dark mode asegurate que `<html data-theme="{{ theme|default:'light' }}">` o que el JS establezca el atributo al cargar.

---

## 4) Carrito — contrato de API (AJAX)

- **Request**: `POST /cart/update/<item_id>/` con `quantity` (form-urlencoded).  
  Headers: `X-Requested-With: XMLHttpRequest`, `X-CSRFToken: <token>`

- **Response (JSON)**:
  ```json
  {
    "item_total": 19999.0,
    "cart_total": 49999.0,
    "cart_count": 3
  }
  ```

- **Comportamiento UI**:
  - Actualiza el total de la fila (`.product-total`) y el **gran total** (`#cart-total`).
  - Si existe `#cartBadge`, actualiza el contador del ícono de carrito.

---

## 5) Base de datos y settings

- **SQLite (dev)**: sin `DATABASE_URL`, la app usa `db.sqlite3`. Ojo permisos/ruta.
- **PostgreSQL (local/prod)**: define `DATABASE_URL`. Recomendado usar `dj-database-url` para parseo:
  ```python
  import dj_database_url, os
  DATABASES = {
      "default": dj_database_url.config(default=f"sqlite:///{BASE_DIR/'db.sqlite3'}")
  }
  ```
- **Localización**:
  ```python
  LANGUAGE_CODE = "es-ar"
  USE_I18N = True
  TIME_ZONE = "America/Argentina/Buenos_Aires"
  MIDDLEWARE += ["django.middleware.locale.LocaleMiddleware"]
  ```

---

## 6) Despliegue en Fly.io

1. `fly launch` (app nueva)
2. `fly postgres create` (DB starter) y `fly postgres attach -a shortyshop <db>`
3. `fly secrets set SECRET_KEY=... ALLOWED_HOSTS=shortyshop.fly.dev DEBUG=0`
4. En `fly.toml`:
   ```toml
   [deploy]
   release_command = "python manage.py migrate --noinput"
   ```
5. `fly deploy`

**Tips**:
- Añadí `python manage.py collectstatic` al build/release si usás `STATICFILES_STORAGE` externo.
- Si falla el attach, seteá `DATABASE_URL` manualmente en secrets.

---

## 7) Guion para el video (2–3 min)

1. **Intro (5s)**: Logo + “ShortyShop: repuestos y accesorios”.  
2. **Catálogo (30s)**: Filtros por marca/modelo, orden por precio.
3. **Detalle (25s)**: Precio, stock, compatibilidades (chips), dark mode.
4. **Carrito (25s)**: Cambiar cantidades → actualización en vivo y totales con formato **es-AR**.
5. **Panel Modelos (25s)**: Buscar, agregar (AJAX), eliminar con confirmación.
6. **Dark Mode (10s)**: Toggle y contraste legible.
7. **Cierre (5s)**: Opcional: botón enviar por WhatsApp.

---

## 8) Outline de diapositivas

1. **Título** — Qué es ShortyShop.
2. **Arquitectura** — Django + Bootstrap + (Postgres/SQLite).
3. **Features** — Catálogo, filtros, carrito AJAX, dark mode, panel modelos.
4. **UX/UI** — Tokens de diseño + componentes + accesibilidad.
5. **Live demo** — Screens & flujo.
6. **Deploy** — Fly.io + migraciones automáticas.
7. **Próximos pasos** — Auth clientes, checkout, imágenes múltiples.

---

## 9) Troubleshooting ampliado

- **SQLite “unable to open database file”**: ruta inexistente o sin permisos; en Windows, cierre de procesos que bloquean el archivo.
- **Cifras sin puntos**: asegurá `|localize` y `LANGUAGE_CODE="es-ar"`; en JS, `Intl.NumberFormat('es-AR', {currency:'ARS', style:'currency'})`.
- **Dark mode ilegible**: verifica que no haya utilitarios `text-dark/bg-white` sin override; usa las clases definidas en `style.css`.
- **CSRF en fetch**: `X-CSRFToken` desde cookie `csrftoken` (helper en `script.js`).

---

¡Listo! Con esto tenés el material para el video y para el repo.
