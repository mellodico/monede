// perfil_menu.js
document.addEventListener('DOMContentLoaded', function() {
    const perfilButton = document.getElementById('perfilButton');
    const perfilMenu = document.getElementById('perfilMenu');
    
    if (!perfilButton || !perfilMenu) {
        console.error('Menu elements not found');
        return;
    }

    // Toggle menu on button click
    perfilButton.addEventListener('click', function(e) {
        e.stopPropagation();
        perfilMenu.classList.toggle('active');
        
        // Update aria-expanded state
        const isExpanded = perfilMenu.classList.contains('active');
        perfilButton.setAttribute('aria-expanded', isExpanded);
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!perfilMenu.contains(e.target) && !perfilButton.contains(e.target)) {
            perfilMenu.classList.remove('active');
            perfilButton.setAttribute('aria-expanded', 'false');
        }
    });

    // Prevent menu from closing when clicking inside
    perfilMenu.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    // Close menu on ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && perfilMenu.classList.contains('active')) {
            perfilMenu.classList.remove('active');
            perfilButton.setAttribute('aria-expanded', 'false');
        }
    });
});

// Optional: Add this to your Django template to ensure the script is loaded
if (typeof window.initializeProfileMenu === 'undefined') {
    window.initializeProfileMenu = true;
    // The code above will run only once
}