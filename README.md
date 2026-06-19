 # ShortyShop

Tienda web de **repuestos** y **accesorios** para autos construida con **Django**.
Incluye catálogo con filtros por **marca** y **modelo**, carrito con actualización
AJAX, modo **oscuro/claro**, y panel liviano para **gestionar modelos** de auto.
Opcional: envío del pedido por **WhatsApp** a un vendedor.

---

## 🚀 Stack
- Python 3.11+ / 3.12
- Django 5.x
- Pillow (imágenes)
- Bootstrap 5 + Bootstrap Icons
- SQLite (dev) / PostgreSQL (prod, Fly.io)
- (Opcional) `python-dotenv` para variables de entorno en `.env`

---

## 🧰 Instalación rápida (desarrollo)

```bash
git clone https://github.com/Falvarez19/ShortyShop.git shortyshop
cd shortyshop

# 1) Crear y activar venv
python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

# 2) Dependencias
pip install -U pip
# Si tenés requirements.txt:
# pip install -r requirements.txt
# Si no, base mínima:
pip install django pillow python-dotenv

# 3) Migraciones + superusuario
python manage.py migrate
python manage.py createsuperuser

# 4) Levantar servidor
python manage.py runserver
```

### `.env` recomendado (dev)
```
DEBUG=1 
SECRET_KEY=dev-please-change-me
ALLOWED_HOSTS=127.0.0.1,localhost
# DATABASE_URL opcional: si no está, se usa SQLite en db.sqlite3
# DATABASE_URL=postgres://USER:PASS@HOST:5432/DBNAME
```
> En **dev**, si no definís `DATABASE_URL`, Django usará **SQLite** por defecto (archivo `db.sqlite3`).

---

## 🗂️ Estructura de proyecto (simplificada)

```
ShortyShop/
├─ shop/
│  ├─ models.py         # Product, ModelCar (+ BRAND_CHOICES)
│  ├─ views.py          # Vistas + APIs (get_models, add_model, delete_model, carrito)
│  ├─ urls.py           # Rutas de la app
│  ├─ templates/shop/
│  │  ├─ base.html
│  │  ├─ product_list.html
│  │  ├─ product_detail.html
│  │  ├─ cart.html
│  │  ├─ add_product.html / edit_product.html
│  │  └─ admin_models.html
│  ├─ static/shop/
│  │  ├─ css/style.css  # tokens, componentes, dark mode
│  │  └─ js/script.js   # UI + carga dinámica + carrito AJAX + theme toggle
│  └─ forms.py
└─ manage.py
```

---

## 🗺️ Rutas principales

- `/` — Home
- `/products/` — Listado general con filtros (marca, modelo, orden precio)
- `/products/<int:product_id>/` — **Detalle** de producto (precio con miles, stock, compatibilidades)
- `/repuestos/` — Listado por categoría *Repuestos*
- `/accesorios/` — Listado por categoría *Accesorios*
- `/add-product/` — Alta de producto (staff)
- `/edit-product/<int:id>/` — Edición de producto (staff)
- `/cart/` — Carrito
- `/panel_admin/modelos/` — **Panel de Modelos** (listar/filtrar/agregar/eliminar) *(staff)*

Asegurate de tener en `urls.py` algo como:
```python
from django.urls import path
from shop import views

urlpatterns = [
    path('panel_admin/modelos/', views.admin_models, name='admin_models'),
    path('panel_admin/modelos/delete/<int:pk>/', views.delete_model, name='delete_model'),
    path('get-models/', views.get_models, name='get_models'),
    path('api/models/add/', views.add_model, name='add_model'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]
```

---

## 🔗 API (marcas/modelos)

### 1) Obtener modelos por marca
`GET /get-models/?brand=<Marca>` → `[{ "id": 1, "name": "Onix" }, ...]`

### 2) Crear modelo (AJAX/Fetch o form)
`POST /api/models/add/`  
Body JSON: `{"brand":"Ford","name":"Fiesta 1.6 2015"}`  
Headers: `X-CSRFToken: <token>`

Respuesta:
```json
{"ok": true, "id": 7, "name": "Fiesta 1.6 2015"}
```

### 3) Eliminar modelo
`POST /panel_admin/modelos/delete/<pk>/` — redirige al panel con el mismo filtro (si había).

---

## 💡 Frontend

- **`static/shop/css/style.css`**: design tokens, componentes (cards, badges, sidebar filtros), navbar, carrusel, **dark mode** mediante `:root[data-theme="dark"] { ... }`.
- **`static/shop/js/script.js`**: 
  - Previsualización de imagen al subir foto.
  - Carga **dinámica** de modelos según la **marca** (`/get-models/`).
  - **Alta rápida** de modelo (`POST /api/models/add/`) con CSRF.
  - Búsqueda/filtros de modelos compatibles + *select all / clear*.
  - **Carrito AJAX**: actualizar cantidades sin recargar y **formateo** local de precios (es-AR) con `Intl.NumberFormat`.
  - **Theme toggle** (dark/light) con persistencia en `localStorage`.

> Para precios en templates se usa `{% load l10n humanize %}` y filtros `floatformat:2|localize`.
> En JS —fallback— se aplica `Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' })`.

---

## 🗃️ Base de datos (dev y prod)

### Opción A — SQLite (dev por defecto)
No definas `DATABASE_URL`. Django creará/abrirá `db.sqlite3` en la raíz del proyecto.
Si aparece `sqlite3.OperationalError: unable to open database file`:
- Verificá permisos de escritura en la carpeta.
- Asegurate que la ruta del archivo existe (no montes rutas inexistentes).
- Cerrá procesos que tengan bloqueado el archivo (en Windows puede pasar).

### Opción B — PostgreSQL local
Definí `DATABASE_URL` en `.env`:
```
DATABASE_URL=postgres://USER:PASS@localhost:5432/shortyshop
```
En `settings.py`, parsealo (por ej. con `dj-database-url`) o usa tu propia lógica.
Si `DATABASE_URL` está presente, se usará esa conexión en lugar de SQLite.

---

## ☁️ Despliegue en Fly.io (resumen)

1. **Instalar** `flyctl` y loguearte: `fly auth login`
2. Crear app: `fly launch` (elige región, no crees DB aún si no querés)
3. Crear Postgres: `fly postgres create` (elige plan starter)
4. **Attach**: `fly postgres attach --app shortyshop <nombre-db>` → define `DATABASE_URL`
5. Secrets:
   ```bash
   fly secrets set SECRET_KEY="tu-clave-segura" ALLOWED_HOSTS="shortyshop.fly.dev" DEBUG=0
   ```
6. En `fly.toml`, agrega un `release_command` para migraciones:
   ```toml
   [deploy]
   release_command = "python manage.py migrate --noinput"
   ```
7. Deploy: `fly deploy`

> Si ves errores de red tipo “connection was forcibly closed by the remote host”, reintentá `fly deploy` o revisá conectividad/timeout.

---

## 🧪 Pruebas rápidas

1. Crear producto desde `/add-product/` y asociar modelos (carga dinámica al elegir marca).
2. Panel `/panel_admin/modelos/`: agregar un modelo y eliminar otro.
3. Ver un producto `/products/<id>/` y comprobar:
   - Precio con separador de miles (`|localize`)
   - Badge de stock e input cantidad con `max=stock`
   - Lista de modelos compatibles
4. Listado `/products/`: filtrar por marca/modelo y ordenar por precio.
5. Carrito `/cart/`: cambiar cantidades y ver actualización AJAX + formateo pesos.

---

## 🛠️ Troubleshooting

- **CSRF 403 en AJAX**: enviá `X-CSRFToken` (ya implementado en `script.js`).
- **No se cargan modelos**: confirmá `data-models-api` o la URL `get_models` en `urls.py`.
- **Oscuro ilegible**: revisá que el `data-theme="dark"` esté en `<html>` y tengas la última `style.css`.
- **SQLite lock** (Windows): cerrá apps que usen el archivo y reintenta.

---


Hecho con ❤️ — ShortyShop
