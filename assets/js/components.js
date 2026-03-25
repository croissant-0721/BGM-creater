/**
 * Component Loader for Boba Video Clone
 * Dynamically loads header and footer from the includes directory
 */

document.addEventListener('DOMContentLoaded', function() {
    loadComponent('header-placeholder', 'includes/header.html', () => {
        // Callback after header is loaded
        highlightActiveLink();
        initMobileMenu();
        // Re-initialize navbar scroll effect if main.js hasn't done it yet
        // note: main.js expects .navbar to exist on DOMContentLoaded
    });

    loadComponent('footer-placeholder', 'includes/footer.html');
});

/**
 * Loads an HTML component into a placeholder element
 * @param {string} placeholderId - The ID of the placeholder element
 * @param {string} url - The URL of the HTML snippet to load
 * @param {function} callback - Optional callback after loading
 */
function loadComponent(placeholderId, url, callback) {
    const placeholder = document.getElementById(placeholderId);
    if (!placeholder) return;

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`Failed to load ${url}`);
            return response.text();
        })
        .then(data => {
            placeholder.innerHTML = data;
            if (callback) callback();
        })
        .catch(error => {
            console.error('Error loading component:', error);
        });
}

/**
 * Highlights the active link based on the current page
 */
function highlightActiveLink() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage || (currentPage === 'index.html' && href.startsWith('#'))) {
            // Specific logic for landing page anchors
            if (currentPage === 'index.html' && href.startsWith('#')) {
                // Let the scroll observer handle this
            } else {
                link.classList.add('active');
            }
        }
    });
}

/**
 * Re-initializes mobile menu toggle functionality for dynamically loaded nav
 */
function initMobileMenu() {
    const navbarCollapse = document.querySelector('.navbar-collapse');
    const navLinksMobile = document.querySelectorAll('.nav-link');
    
    if (navbarCollapse && navLinksMobile.length > 0) {
        navLinksMobile.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse) || new bootstrap.Collapse(navbarCollapse);
                    bsCollapse.hide();
                }
            });
        });
    }
}
