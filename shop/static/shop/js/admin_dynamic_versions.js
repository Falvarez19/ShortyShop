document.addEventListener("DOMContentLoaded", function () {
    const modelField = document.querySelector("#id_model");
    let versionField = document.querySelector("#id_version");

    if (!modelField || !versionField) {
        console.error("No se encontraron los campos de modelo y versión.");
        return;
    }

    // Función para actualizar las versiones cuando se selecciona un modelo
    function actualizarVersiones() {
        const modelId = modelField.value;
        if (!modelId) return;

        // Limpiar el campo de versiones antes de cargar nuevas opciones
        versionField.innerHTML = "";
        let defaultOption = new Option("Seleccione una versión", "");
        versionField.appendChild(defaultOption);

        // Realizar la petición a la API para obtener las versiones del modelo seleccionado
        fetch(`/api/get_versions/?model_id=${modelId}`)
            .then(response => response.json())
            .then(data => {
                data.versions.forEach(version => {
                    let option = new Option(version.name, version.id);
                    versionField.appendChild(option);
                });
            })
            .catch(error => console.error("Error cargando versiones:", error));
    }

    // Detectar cambio en el modelo y actualizar versiones
    modelField.addEventListener("change", actualizarVersiones);

    // Ejecutar la función al cargar la página si hay un modelo seleccionado
    if (modelField.value) {
        actualizarVersiones();
    }
});
