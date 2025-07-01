// static/js/limits.js
document.addEventListener('DOMContentLoaded', function() {
    const valorInput = document.getElementById('valor');
    const valorSlider = document.getElementById('valor-slider');

    // Sync slider with input
    valorInput.addEventListener('input', function() {
        valorSlider.value = this.value;
    });

    // Sync input with slider
    valorSlider.addEventListener('input', function() {
        valorInput.value = this.value;
    });

    // Format currency
    valorInput.addEventListener('blur', function() {
        const value = parseFloat(this.value);
        if (!isNaN(value)) {
            this.value = value.toFixed(2);
        }
    });

    // Set today's date
    const today = new Date();
    const options = { weekday: 'long', day: 'numeric' };
    const formattedDate = today.toLocaleDateString('pt-BR', options);
    document.querySelector('label[for="today"]').textContent = formattedDate;
});