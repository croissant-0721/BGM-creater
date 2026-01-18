/**
 * Theme Management for Panqu AI
 * Handles Light/Dark mode toggling and persistence.
 */

const ThemeManager = {
    // Keys
    STORAGE_KEY: 'panqu_theme_preference',
    inputClass: 'theme-toggle-input',

    init() {
        this.applySavedTheme();
        this.bindEvents();
    },

    bindEvents() {
        // Find all theme toggles in DOM (desktop, mobile navs)
        const toggles = document.querySelectorAll(`.${this.inputClass}`);
        toggles.forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                this.setTheme(e.target.checked ? 'dark' : 'light');
            });

            // Sync initial state
            toggle.checked = document.documentElement.getAttribute('data-theme') === 'dark';
        });
    },

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(this.STORAGE_KEY, theme);

        // Sync all toggle inputs if multiple exist on page
        const toggles = document.querySelectorAll(`.${this.inputClass}`);
        toggles.forEach(t => t.checked = theme === 'dark');
    },

    applySavedTheme() {
        const saved = localStorage.getItem(this.STORAGE_KEY);
        if (saved) {
            document.documentElement.setAttribute('data-theme', saved);
        } else {
            // If no saved preference, check if HTML has a default, otherwise 'light'
            const current = document.documentElement.getAttribute('data-theme');
            if (!current) {
                document.documentElement.setAttribute('data-theme', 'light');
            }
        }
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
});
