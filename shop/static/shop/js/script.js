// --- ShortyShop UI helpers + Modelos por marca ---
document.addEventListener("DOMContentLoaded", () => {
  // Navbar scroll efecto
  (function () {
    const navbar = document.querySelector(".navbar");
    if (!navbar) return;
    const onScroll = () => {
      if (window.scrollY > 50) navbar.classList.add("scrolled");
      else navbar.classList.remove("scrolled");
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  })();

  // ---------- Add/Edit Product: dinámico de modelos ----------
  const brandSelect      = document.getElementById("id_marca");
  const modelsContainer  = document.getElementById("models-container");
  const searchInput      = document.getElementById("modelSearch");
  const btnAll           = document.getElementById("btnSelectAll");
  const btnClear         = document.getElementById("btnClearAll");
  const countSelectedEl  = document.getElementById("modelsCount"); // <span> o <strong>
  const countTotalEl     = document.getElementById("modelsTotal"); // opcional
  const newModelInput    = document.getElementById("newModelName");
  const btnAddModel      = document.getElementById("btnAddModel");

  // Vista previa de imagen
  const imageInput       = document.getElementById("image");
  const imagePreviewWrap = document.getElementById("imagePreviewWrap");
  const imagePreview     = document.getElementById("imagePreview");
  if (imageInput && imagePreview && imagePreviewWrap) {
    imageInput.addEventListener("change", (e) => {
      const file = e.target.files?.[0];
      if (!file) {
        imagePreviewWrap.classList.add("d-none");
        imagePreview.src = "";
        return;
      }
      const reader = new FileReader();
      reader.onload = (ev) => {
        imagePreview.src = ev.target.result;
        imagePreviewWrap.classList.remove("d-none");
      };
      reader.readAsDataURL(file);
    });
  }

  if (!brandSelect || !modelsContainer) return;

  // Endpoints (pueden venir por data-* del <body>)
  const MODELS_API    = document.body?.dataset?.modelsApi    || "/get-models/";
  const ADD_MODEL_API = document.body?.dataset?.addModelApi  || "/api/models/add/";

  // ---- CSRF (Django) ----
  function getCookie(name) {
    const m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return m ? decodeURIComponent(m.pop()) : null;
  }
  const getCSRFToken = () => getCookie("csrftoken");

  // ---- Helpers selección/contador/búsqueda ----
  function getSelectedIdsFromDataset() {
    const raw = (modelsContainer.dataset.selected || "").trim();
    if (!raw) return new Set();
    return new Set(
      raw.split(",").map((s) => s.trim()).filter(Boolean)
    );
  }

  function updateCount() {
    const total = modelsContainer.querySelectorAll(
      '.form-check-input[type="checkbox"]'
    ).length;
    const checked = modelsContainer.querySelectorAll(
      '.form-check-input[type="checkbox"]:checked'
    ).length;

    if (countSelectedEl && !countTotalEl) {
      countSelectedEl.textContent = `Sel: ${checked} seleccionados · ${total} totales`;
    }
    if (countSelectedEl && countTotalEl) {
      countSelectedEl.textContent = String(checked);
      countTotalEl.textContent    = String(total);
    }
  }

  function applySearch() {
    if (!searchInput) return;
    const q = searchInput.value.trim().toLowerCase();
    modelsContainer.querySelectorAll(".form-check").forEach((row) => {
      const text = (row.querySelector(".form-check-label")?.textContent || "").toLowerCase();
      row.style.display = q && !text.includes(q) ? "none" : "";
    });
  }

  function preselectFromDataset() {
    const selected = getSelectedIdsFromDataset();
    if (selected.size === 0) return;
    modelsContainer
      .querySelectorAll('.form-check-input[type="checkbox"]')
      .forEach((c) => { if (selected.has(String(c.value))) c.checked = true; });
  }

  function createCheckbox(model) {
    const wrap = document.createElement("div");
    wrap.className = "form-check";
    wrap.innerHTML = `
      <input class="form-check-input" type="checkbox" id="mdl_${model.id}"
             name="compatible_models" value="${model.id}">
      <label class="form-check-label" for="mdl_${model.id}">${model.name}</label>`;
    return wrap;
  }

  function renderModels(list) {
    if (!Array.isArray(list) || list.length === 0) {
      modelsContainer.innerHTML = '<small class="text-muted">No hay modelos para esta marca.</small>';
      updateCount();
      return;
    }
    const frag = document.createDocumentFragment();
    list.forEach((m) => frag.appendChild(createCheckbox(m)));
    modelsContainer.innerHTML = "";
    modelsContainer.appendChild(frag);
    preselectFromDataset();
    applySearch();
    updateCount();
  }

  async function fetchModels(brand) {
    if (!brand) {
      modelsContainer.innerHTML = '<small class="text-muted">Elegí primero la Marca del Auto.</small>';
      updateCount();
      return;
    }
    try {
      const url = `${MODELS_API}?brand=${encodeURIComponent(brand)}`;
      const res = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json(); // [{id, name}, ...]
      renderModels(data);
    } catch (err) {
      console.error("Error trayendo modelos:", err);
      modelsContainer.innerHTML = '<small class="text-danger">No se pudieron cargar los modelos.</small>';
      updateCount();
    }
  }

  // ---- Agregar modelo "al vuelo" ----
  async function addNewModel() {
    const brand = brandSelect.value;
    const name  = (newModelInput?.value || "").trim();
    if (!brand) { alert("Elegí primero una marca."); return; }
    if (!name)  return;

    try {
      const res = await fetch(ADD_MODEL_API, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": getCSRFToken() || ""
        },
        body: JSON.stringify({ name, brand })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const created = await res.json(); // {id, name}
      if (!created || !created.id || !created.name) {
        console.warn("Respuesta inesperada al crear modelo:", created);
        return;
      }
      const node = createCheckbox(created);
      modelsContainer.appendChild(node);
      node.querySelector('input[type="checkbox"]').checked = true;
      newModelInput.value = "";
      applySearch();
      updateCount();
    } catch (err) {
      console.error("Error creando modelo:", err);
      alert("No se pudo crear el modelo. Intentalo de nuevo.");
    }
  }

  // ---- Eventos ----
  brandSelect.addEventListener("change", (e) => fetchModels(e.target.value));

  modelsContainer.addEventListener("change", (e) => {
    if (e.target.matches('.form-check-input[type="checkbox"]')) updateCount();
  });

  if (searchInput) searchInput.addEventListener("input", applySearch);

  if (btnAll) {
    btnAll.addEventListener("click", () => {
      modelsContainer
        .querySelectorAll('.form-check-input[type="checkbox"]:not(:checked)')
        .forEach((c) => (c.checked = true));
      updateCount();
    });
  }

  if (btnClear) {
    btnClear.addEventListener("click", () => {
      modelsContainer
        .querySelectorAll('.form-check-input[type="checkbox"]:checked')
        .forEach((c) => (c.checked = false));
      updateCount();
    });
  }

  if (btnAddModel && newModelInput) {
    btnAddModel.addEventListener("click", addNewModel);
    newModelInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") { e.preventDefault(); addNewModel(); }
    });
  }

  // Estado inicial
  if (brandSelect.value) fetchModels(brandSelect.value);
  else { preselectFromDataset(); updateCount(); }
});
