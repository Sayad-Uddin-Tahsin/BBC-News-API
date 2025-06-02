// index.js - Header fade-in animation
window.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        const header = document.getElementById('header-content');
        if (header) {
            header.style.opacity = 1;
            header.style.transform = 'translateY(0)';
        }
    }, 200);
});
