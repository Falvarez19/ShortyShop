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
  const brandSelect = document.getElementById("id_marca");
  const modelsContainer = document.getElementById("models-container");
  const searchInput = document.getElementById("modelSearch");
  const btnAll = document.getElementById("btnSelectAll");
  const btnClear = document.getElementById("btnClearAll");
  const countEl = document.getElementById("modelsCount");

  // Vista previa de imagen (opcional)
  const imageInput = document.getElementById("image");
  const imagePreviewWrap = document.getElementById("imagePreviewWrap");
  const imagePreview = document.getElementById("imagePreview");
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

  const MODELS_API =
    document.body?.dataset?.modelsApi || "/get-models/";

  function getSelectedIdsFromDataset() {
    const raw = (modelsContainer.dataset.selected || "").trim();
    if (!raw) return new Set();
    return new Set(
      raw
        .split(",")
        .map((s) => s.trim())
        .filter((s) => s.length)
    );
  }

  function updateCount() {
    if (!countEl) return;
    const total = modelsContainer.querySelectorAll(
      '.form-check-input[type="checkbox"]'
    ).length;
    const checked = modelsContainer.querySelectorAll(
      '.form-check-input[type="checkbox"]:checked'
    ).length;
    countEl.textContent = `Sel: ${checked} seleccionados · ${total} totales`;
  }

  function applySearch() {
    if (!searchInput) return;
    const q = searchInput.value.trim().toLowerCase();
    const items = modelsContainer.querySelectorAll(".form-check");
    items.forEach((row) => {
      const label = row.querySelector(".form-check-label");
      const text = (label?.textContent || "").toLowerCase();
      row.style.display = q && !text.includes(q) ? "none" : "";
    });
  }

  function preselectFromDataset() {
    const selected = getSelectedIdsFromDataset();
    if (selected.size === 0) return;
    modelsContainer
      .querySelectorAll('.form-check-input[type="checkbox"]')
      .forEach((c) => {
        if (selected.has(String(c.value))) c.checked = true;
      });
  }

  function renderModels(list) {
    if (!Array.isArray(list) || list.length === 0) {
      modelsContainer.innerHTML =
        '<small class="text-muted">No hay modelos para esta marca.</small>';
      updateCount();
      return;
    }
    const html = list
      .map(
        (m) => `
      <div class="form-check">
        <input class="form-check-input" type="checkbox" id="mdl_${m.id}" name="compatible_models" value="${m.id}">
        <label class="form-check-label" for="mdl_${m.id}">${m.name}</label>
      </div>`
      )
      .join("");
    modelsContainer.innerHTML = html;
    preselectFromDataset(); // marcar los ya asociados
    applySearch();
    updateCount();
  }

  async function fetchModels(brand) {
    if (!brand) {
      modelsContainer.innerHTML =
        '<small class="text-muted">Elegí primero la Marca del Auto.</small>';
      updateCount();
      return;
    }
    try {
      const url = `${MODELS_API}?brand=${encodeURIComponent(brand)}`;
      const res = await fetch(url, { headers: { "X-Requested-With": "fetch" } });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json(); // [{id, name}, ...]
      renderModels(data);
    } catch (err) {
      console.error("Error trayendo modelos:", err);
      modelsContainer.innerHTML =
        '<small class="text-danger">No se pudieron cargar los modelos.</small>';
      updateCount();
    }
  }

  // Eventos
  brandSelect.addEventListener("change", (e) => {
    fetchModels(e.target.value);
  });

  modelsContainer.addEventListener("change", (e) => {
    if (e.target.matches('.form-check-input[type="checkbox"]')) updateCount();
  });

  if (searchInput) {
    searchInput.addEventListener("input", applySearch);
  }

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

  // Estado inicial (si ya había marca/checkboxes renderizados del servidor)
  if (brandSelect.value) fetchModels(brandSelect.value);
  else {
    preselectFromDataset();
    updateCount();
  }
});
