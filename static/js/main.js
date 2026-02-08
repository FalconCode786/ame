/**
 * Al Muslim Engineers - Solar Solutions
 * Main JavaScript File
 * Author: AI Developer
 * Version: 1.0
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modules
    initThemeToggle();
    initNavigation();
    initFlashMessages();
    initSmoothScroll();
    initParallaxEffects();
    initAnimations();
    initFormValidation();
    initQuantityControls();
});

/**
 * Theme Toggle - Dark/Light Mode
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }
}

function updateThemeIcon(theme) {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (theme === 'dark') {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
        }
    }
}

/**
 * Mobile Navigation
 */
function initNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('open');
            
            // Update icon
            const icon = navToggle.querySelector('i');
            if (navMenu.classList.contains('open')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
        
        // Close menu when clicking on a link
        const navLinks = navMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('open');
                const icon = navToggle.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            });
        });
    }
    
    // Navbar scroll effect
    const navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
}

/**
 * Flash Messages Auto-dismiss
 */
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateX(100%)';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
}

/**
 * Smooth Scroll for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Parallax Effects
 */
function initParallaxEffects() {
    const parallaxElements = document.querySelectorAll('.hero-bg img, .cta-bg img');
    
    if (parallaxElements.length > 0 && !window.matchMedia('(pointer: coarse)').matches) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const speed = 0.5;
                element.style.transform = `translateY(${scrolled * speed}px)`;
            });
        });
    }
}

/**
 * Scroll Animations
 */
function initAnimations() {
    const animatedElements = document.querySelectorAll('.service-card, .step-card, .product-card, .gallery-card, .testimonial-card');
    
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(element);
    });
    
    // Add CSS for animated elements
    const style = document.createElement('style');
    style.textContent = `
        .animate-in {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    `;
    document.head.appendChild(style);
}

/**
 * Form Validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    
                    // Add error message if not exists
                    let errorMsg = field.parentElement.querySelector('.error-message');
                    if (!errorMsg) {
                        errorMsg = document.createElement('span');
                        errorMsg.className = 'error-message';
                        errorMsg.style.color = 'var(--danger-color)';
                        errorMsg.style.fontSize = '0.85rem';
                        errorMsg.style.marginTop = '4px';
                        errorMsg.style.display = 'block';
                        field.parentElement.appendChild(errorMsg);
                    }
                    errorMsg.textContent = 'This field is required';
                } else {
                    field.classList.remove('error');
                    const errorMsg = field.parentElement.querySelector('.error-message');
                    if (errorMsg) {
                        errorMsg.remove();
                    }
                }
            });
            
            // Password confirmation validation
            const password = form.querySelector('#password');
            const confirmPassword = form.querySelector('#confirm_password');
            
            if (password && confirmPassword) {
                if (password.value !== confirmPassword.value) {
                    isValid = false;
                    alert('Passwords do not match!');
                }
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Quantity Controls for Cart
 */
function initQuantityControls() {
    // This is handled inline in the HTML for cart items
    // Additional functionality can be added here
}

/**
 * Solar Calculator - Real-time calculations
 */
function calculateSolarSavings() {
    const monthlyBill = parseFloat(document.getElementById('monthly_bill')?.value) || 0;
    const roofArea = parseFloat(document.getElementById('roof_area')?.value) || 0;
    
    if (monthlyBill > 0 && roofArea > 0) {
        // Electricity rate in Pakistan (approximate)
        const electricityRate = 25; // PKR per unit
        
        // Calculate monthly consumption
        const monthlyUnits = monthlyBill / electricityRate;
        
        // Solar parameters for Rawalpindi
        const peakSunHours = 5.5;
        const systemLossFactor = 0.8;
        
        // Calculate required capacity
        const dailyUnits = monthlyUnits / 30;
        const requiredCapacity = dailyUnits / (peakSunHours * systemLossFactor);
        
        // Round to standard capacity
        const standardCapacities = [1, 2, 3, 5, 7, 10, 15, 20, 25, 30, 40, 50];
        let recommendedCapacity = standardCapacities.find(c => c >= requiredCapacity) || 50;
        
        // Check roof constraint
        const requiredArea = recommendedCapacity * 100;
        if (requiredArea > roofArea) {
            recommendedCapacity = Math.floor(roofArea / 100);
            recommendedCapacity = Math.max(1, recommendedCapacity);
        }
        
        // Cost estimation
        const costPerKw = 80000;
        const totalCost = recommendedCapacity * costPerKw;
        
        // Savings calculation
        const monthlyGeneration = recommendedCapacity * peakSunHours * 30 * systemLossFactor;
        const monthlySavings = monthlyGeneration * electricityRate;
        const annualSavings = monthlySavings * 12;
        const paybackYears = totalCost / annualSavings;
        
        return {
            capacity: recommendedCapacity,
            cost: totalCost,
            monthlySavings: monthlySavings,
            annualSavings: annualSavings,
            payback: paybackYears.toFixed(1),
            netMeteringEligible: recommendedCapacity >= 5
        };
    }
    
    return null;
}

/**
 * Application Status Checker
 */
function checkApplicationStatus(referenceNumber) {
    fetch(`/api/application-status/${referenceNumber}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showNotification('Application not found', 'error');
            } else {
                displayApplicationStatus(data);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Failed to fetch application status', 'error');
        });
}

/**
 * Show Notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 16px 24px;
        background: var(--bg-primary);
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

/**
 * Lazy Loading Images
 */
function initLazyLoading() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
}

/**
 * Counter Animation
 */
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    function updateCounter() {
        start += increment;
        if (start < target) {
            element.textContent = Math.floor(start);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    }
    
    updateCounter();
}

/**
 * Tab Navigation for Dashboard
 */
function initTabNavigation() {
    const tabLinks = document.querySelectorAll('[data-tab]');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetTab = this.getAttribute('data-tab');
            
            // Update active states
            tabLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === targetTab) {
                    content.classList.add('active');
                }
            });
            
            // Update URL hash
            window.history.pushState(null, null, `#${targetTab}`);
        });
    });
    
    // Handle initial hash
    const initialHash = window.location.hash.slice(1);
    if (initialHash) {
        const targetLink = document.querySelector(`[data-tab="${initialHash}"]`);
        if (targetLink) {
            targetLink.click();
        }
    }
}

/**
 * Print functionality
 */
function printOrder(orderId) {
    window.print();
}

/**
 * Copy to Clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

/**
 * Confirm Delete
 */
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

/**
 * Format Currency
 */
function formatCurrency(amount, currency = 'PKR') {
    return new Intl.NumberFormat('en-PK', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

/**
 * Format Date
 */
function formatDate(dateString, format = 'long') {
    const date = new Date(dateString);
    const options = format === 'long' 
        ? { year: 'numeric', month: 'long', day: 'numeric' }
        : { year: 'numeric', month: 'short', day: 'numeric' };
    
    return date.toLocaleDateString('en-PK', options);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Add CSS animations
const animationStyles = document.createElement('style');
animationStyles.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .error {
        border-color: var(--danger-color) !important;
    }
    
    .navbar.scrolled {
        box-shadow: var(--shadow-md);
    }
`;
document.head.appendChild(animationStyles);

// Export functions for global access
window.AlMuslimEngineers = {
    calculateSolarSavings,
    checkApplicationStatus,
    showNotification,
    copyToClipboard,
    formatCurrency,
    formatDate,
    debounce,
    throttle,
    confirmDelete,
    printOrder
};
