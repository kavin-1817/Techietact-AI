// Theme Toggle System
(function() {
    'use strict';
    
    const html = document.documentElement;
    
    // Get theme from localStorage or default to 'dark'
    function getSavedTheme() {
        return localStorage.getItem('theme') || 'dark';
    }
    
    // Apply theme to document
    function applyTheme(theme) {
        if (theme === 'light') {
            html.setAttribute('data-theme', 'light');
        } else {
            html.removeAttribute('data-theme');
        }
        // Force reflow to ensure styles are applied
        void html.offsetHeight;
    }
    
    // Get current theme from DOM
    function getCurrentTheme() {
        const theme = html.getAttribute('data-theme');
        return theme === 'light' ? 'light' : 'dark';
    }
    
    // Update toggle icon
    function updateIcon(theme) {
        const themeIcon = document.getElementById('themeIcon');
        const themeToggle = document.getElementById('themeToggle');
        
        if (!themeIcon || !themeToggle) return;
        
        if (theme === 'dark') {
            themeIcon.className = 'bi bi-moon-fill';
            themeToggle.setAttribute('title', 'Switch to light mode');
        } else {
            themeIcon.className = 'bi bi-sun-fill';
            themeToggle.setAttribute('title', 'Switch to dark mode');
        }
    }
    
    // Toggle theme
    function toggleTheme() {
        const currentTheme = getCurrentTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        console.log('Current theme:', currentTheme);
        console.log('Switching to:', newTheme);
        
        applyTheme(newTheme);
        localStorage.setItem('theme', newTheme);
        updateIcon(newTheme);
        
        // Verify the change
        setTimeout(function() {
            const appliedTheme = html.getAttribute('data-theme') || 'dark';
            console.log('Theme applied:', appliedTheme);
            console.log('Background color:', window.getComputedStyle(document.body).backgroundColor);
        }, 100);
    }
    
    // Initialize when DOM is ready
    function initTheme() {
        const savedTheme = getSavedTheme();
        applyTheme(savedTheme);
        
        // Update icon
        setTimeout(function() {
            updateIcon(savedTheme);
        }, 100);
        
        // Set up toggle button
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            // Remove any existing listeners by cloning
            const newToggle = themeToggle.cloneNode(true);
            themeToggle.parentNode.replaceChild(newToggle, themeToggle);
            
            newToggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                toggleTheme();
            });
        }
    }
    
    // Run initialization
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }
})();

