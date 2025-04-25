function formatDoc(command, value = null) {
    document.execCommand(command, false, value);
    document.getElementById('editor').focus();
}

function publicarContenido() {
    var contenidoHTML = document.getElementById('editor').innerHTML;
    // Aquí puedes enviar 'contenidoHTML' a tu servidor para publicarlo.
    console.log(contenidoHTML); // Para depuración, muestra el HTML en la consola.
    // ... (Código para enviar 'contenidoHTML' al servidor) ...
}

// Ejemplo de cómo adjuntar el evento a un botón de "Publicar"
document.getElementById('publicarBtn').addEventListener('click', publicarContenido);