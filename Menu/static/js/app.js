function cargarContenido(url) {
    $("#contenido").load(url, function(response, status, xhr) {
        if (status == "success") {
            console.log("Contenido cargado correctamente:", url);
            $(".content").addClass("center-content");

            // Si hay scripts en el HTML cargado, hay que volver a ejecutarlos
            ejecutarScriptsDinamicos("#contenido");
        } else {
            console.error("Error al cargar contenido:", xhr.status, xhr.statusText);
        }
    });
}

function ejecutarScriptsDinamicos(selector) {
    $(selector).find("script").each(function() {
        var scriptText = $(this).text();
        var scriptTag = document.createElement("script");
        scriptTag.textContent = scriptText;
        document.body.appendChild(scriptTag);
    });
}

// Función para actualizar datos sin recargar la página
function actualizarDatos() {
    fetch("/monitoreo/actualizar_datos")
        .then(response => response.json())
        .then(data => {
            console.log("Datos actualizados:", data);
            actualizarTabla(data);
        })
        .catch(error => console.error("Error al actualizar datos:", error));
}

// Función para actualizar la tabla con los nuevos datos
function actualizarTabla(data) {
    let tabla = document.getElementById("tabla-reportes");
    if (!tabla) {
        console.error("No se encontró la tabla con id 'tabla-reportes'");
        return;
    }
    
    let tbody = tabla.querySelector("tbody");
    tbody.innerHTML = ""; // Limpiar contenido actual

    ["reportes_trimestrales", "reportes_mensuales", "reportes_semestrales", "reportes_anuales"].forEach(categoria => {
        if (data[categoria]) {
            data[categoria].forEach(reporte => {
                let row = `<tr>
                    <td>${reporte.nombre}</td>
                    <td style="background-color: ${reporte.indicador};">${reporte.indicador}</td>
                    <td>${reporte.nombre_original}</td>
                </tr>`;
                tbody.innerHTML += row;
            });
        }
    });
}
