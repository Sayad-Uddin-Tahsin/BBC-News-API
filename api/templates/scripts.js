// index.js - Header fade-in and menu handling
window.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        const header = document.getElementById('header-content');
        if (header) {
            header.style.opacity = 1;
            header.style.transform = 'translateY(0)';
        }
    }, 200);
});

// Handle hamburger menu
const hamburger = document.getElementById('hamburger');
const navbarLinks = document.getElementById('navbar-links');

// Function to toggle menu
function toggleMenu() {
    navbarLinks.classList.toggle('active');
    hamburger.classList.toggle('active');
}

// Add click event listener
hamburger.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    toggleMenu();
});

// Close menu when clicking outside
document.addEventListener('click', (e) => {
    if (navbarLinks.classList.contains('active') && 
        !hamburger.contains(e.target) && 
        !navbarLinks.contains(e.target)) {
        toggleMenu();
    }
});

// Prevent clicks inside menu from closing it
navbarLinks.addEventListener('click', (e) => {
    e.stopPropagation();
});

// Handle header content fade-in
const headerContent = document.getElementById('header-content');
window.addEventListener('load', () => {
    headerContent.style.opacity = '1';
    headerContent.style.transform = 'translateY(0)';
});
