/**
 * Boba Video Clone - Main JavaScript
 * Handles interactive elements and animations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;

        // Add/remove scrolled class
        if (currentScroll > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
    });

    // Smooth scroll for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            // Only intercept if it's a section link
            if (href !== '#' && href.startsWith('#')) {
                e.preventDefault();
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);

                if (targetElement) {
                    const navbarHeight = navbar.offsetHeight;
                    const targetPosition = targetElement.offsetTop - navbarHeight;

                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Intersection Observer for scroll animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all cards and sections
    const animatedElements = document.querySelectorAll(
        '.showcase-card, .style-card, .feature-card, .pricing-card, .section-title, .section-subtitle'
    );

    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Video play button interactions
    const playButtons = document.querySelectorAll('.btn-play');
    playButtons.forEach(button => {
        button.addEventListener('click', function() {
            const card = this.closest('.showcase-card');
            // You can add video playback functionality here
            console.log('Play video for:', card.querySelector('.showcase-title').textContent);
        });
    });

    // Add hover effect to pricing cards
    const pricingCards = document.querySelectorAll('.pricing-card');
    pricingCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            if (!this.classList.contains('featured')) {
                pricingCards.forEach(c => c.classList.remove('featured'));
                this.classList.add('featured');
            }
        });
    });

    // Mobile menu close on link click
    const navbarCollapse = document.querySelector('.navbar-collapse');
    const navLinksMobile = document.querySelectorAll('.nav-link');
    navLinksMobile.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 992) {
                const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                bsCollapse.hide();
            }
        });
    });

    // Ensure hero background video plays correctly
    const heroVideo = document.querySelector('.hero-bg-video');
    if (heroVideo) {
        // Ensure video plays in all browsers
        heroVideo.play().catch(function(error) {
            console.log('Video autoplay failed:', error);
            // Add a play button overlay if autoplay fails
            const playButton = document.createElement('button');
            playButton.className = 'btn-video-play';
            playButton.innerHTML = '<i class="bi bi-play-fill"></i>';
            playButton.style.cssText = 'position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:80px;height:80px;border-radius:50%;background:rgba(255,255,255,0.2);border:none;color:white;font-size:2rem;cursor:pointer;z-index:2;';
            playButton.addEventListener('click', function() {
                heroVideo.play();
                this.remove();
            });
            document.querySelector('.hero-video-background').appendChild(playButton);
        });
    }

    // Counter animation for pricing stats
    function animateCounter(element, target, duration = 2000) {
        let start = 0;
        const increment = target / (duration / 16);

        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(start);
            }
        }, 16);
    }

    // Add active state to nav links based on scroll position
    const sections = document.querySelectorAll('section[id]');

    window.addEventListener('scroll', function() {
        const scrollY = window.pageYOffset;

        sections.forEach(section => {
            const sectionHeight = section.offsetHeight;
            const sectionTop = section.offsetTop - navbar.offsetHeight - 100;
            const sectionId = section.getAttribute('id');
            const correspondingLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);

            if (correspondingLink) {
                if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                    correspondingLink.classList.add('active');
                } else {
                    correspondingLink.classList.remove('active');
                }
            }
        });
    });

    // Add loading animation for images
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('load', function() {
            this.style.opacity = '1';
        });

        // If image is already loaded
        if (img.complete) {
            img.style.opacity = '1';
        } else {
            img.style.opacity = '0';
            img.style.transition = 'opacity 0.3s ease';
        }
    });

    // Easter egg - Konami code
    const konamiCode = [
        'ArrowUp', 'ArrowUp',
        'ArrowDown', 'ArrowDown',
        'ArrowLeft', 'ArrowRight',
        'ArrowLeft', 'ArrowRight',
        'b', 'a'
    ];
    let konamiIndex = 0;

    document.addEventListener('keydown', function(e) {
        if (e.key === konamiCode[konamiIndex]) {
            konamiIndex++;
            if (konamiIndex === konamiCode.length) {
                activateEasterEgg();
                konamiIndex = 0;
            }
        } else {
            konamiIndex = 0;
        }
    });

    function activateEasterEgg() {
        // Fun animation or effect
        document.body.style.animation = 'rainbow 2s ease';
        setTimeout(() => {
            document.body.style.animation = '';
        }, 2000);
    }

    // Console message
    console.log('%c🎬 Boba Video Clone', 'font-size: 24px; font-weight: bold; color: #667eea;');
    console.log('%cBuilt with Bootstrap 5', 'font-size: 14px; color: #4ecdc4;');
    console.log('%cExplore, experiment, and create freely!', 'font-size: 12px; color: #b0b0b0;');
});

// Add rainbow animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes rainbow {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }
`;
document.head.appendChild(style);