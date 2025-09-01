// Main Store JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Quantity input validation
    const quantityInputs = document.querySelectorAll('input[type="number"][name="quantity"]');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const value = parseInt(this.value);
            const min = parseInt(this.min);
            const max = parseInt(this.max);
            
            if (value < min) {
                this.value = min;
            } else if (value > max) {
                this.value = max;
            }
        });
    });
    
    // Add to cart form validation
    const addToCartForms = document.querySelectorAll('form[action*="add-to-cart"]');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const quantityInput = this.querySelector('input[name="quantity"]');
            if (quantityInput) {
                const quantity = parseInt(quantityInput.value);
                if (quantity <= 0) {
                    e.preventDefault();
                    alert('Quantity must be greater than 0.');
                    return false;
                }
            }
        });
    });
    
    // Cart quantity update with AJAX (optional enhancement)
    const cartQuantityInputs = document.querySelectorAll('.cart-quantity-input');
    cartQuantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                // Add loading state
                this.classList.add('loading');
                
                // Submit form
                form.submit();
            }
        });
    });
    
    // Search form enhancement
    const searchForm = document.querySelector('form[action*=""]');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="q"]');
        if (searchInput) {
            // Add search suggestions (placeholder for future enhancement)
            searchInput.addEventListener('input', function() {
                const query = this.value.trim();
                if (query.length >= 2) {
                    // Could implement AJAX search suggestions here
                }
            });
        }
    }
    
    // Product image lazy loading
    const productImages = document.querySelectorAll('.product-image');
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                }
            });
        });
        
        productImages.forEach(img => {
            if (img.dataset.src) {
                imageObserver.observe(img);
            }
        });
    }
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Form enhancement - auto-save draft (optional)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const formData = new FormData(form);
        const formKey = form.action || form.id || 'form';
        
        // Load saved draft on page load
        const savedData = localStorage.getItem(`draft_${formKey}`);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(key => {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input && input.type !== 'file') {
                        input.value = data[key];
                    }
                });
            } catch (e) {
                console.error('Error loading form draft:', e);
            }
        }
        
        // Save draft on input change
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                const currentData = {};
                inputs.forEach(inp => {
                    if (inp.name && inp.type !== 'file') {
                        currentData[inp.name] = inp.value;
                    }
                });
                localStorage.setItem(`draft_${formKey}`, JSON.stringify(currentData));
            });
        });
        
        // Clear draft on successful submit
        form.addEventListener('submit', function() {
            localStorage.removeItem(`draft_${formKey}`);
        });
    });
    
    // Mobile menu enhancement
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close mobile menu when clicking on a link
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    navbarCollapse.classList.remove('show');
                }
            });
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navbarCollapse.contains(e.target) && !navbarToggler.contains(e.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
    
    // Product card hover effects
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Alert auto-dismiss
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (alert.classList.contains('alert-dismissible')) {
            setTimeout(() => {
                const closeButton = alert.querySelector('.btn-close');
                if (closeButton) {
                    closeButton.click();
                }
            }, 5000); // Auto-dismiss after 5 seconds
        }
    });
    
    // Category filter enhancement
    const categoryLinks = document.querySelectorAll('.category-filter a');
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Remove active class from all links
            categoryLinks.forEach(l => l.classList.remove('active'));
            // Add active class to clicked link
            this.classList.add('active');
        });
    });
    
    // Price formatting
    const priceElements = document.querySelectorAll('.price');
    priceElements.forEach(element => {
        const price = parseFloat(element.textContent.replace(/[^0-9.-]+/g, ''));
        if (!isNaN(price)) {
            element.textContent = `$${price.toFixed(2)}`;
        }
    });
    
    // Stock status indicator
    const stockElements = document.querySelectorAll('.stock-status');
    stockElements.forEach(element => {
        const stock = parseInt(element.textContent);
        if (stock > 0) {
            element.classList.add('text-success');
            element.textContent = `In Stock (${stock})`;
        } else {
            element.classList.add('text-danger');
            element.textContent = 'Out of Stock';
        }
    });
    
    // Initialize any additional components
    initializeComponents();
});

// Initialize additional components
function initializeComponents() {
    // Add any additional component initialization here
    
    // Example: Initialize a shopping cart counter
    updateCartCounter();
    
    // Example: Initialize wishlist functionality
    initializeWishlist();
}

// Update cart counter
function updateCartCounter() {
    // This could be enhanced with AJAX to get real-time cart count
    const cartLinks = document.querySelectorAll('a[href*="cart"]');
    cartLinks.forEach(link => {
        // Add cart counter if needed
    });
}

// Initialize wishlist functionality
function initializeWishlist() {
    // This could be implemented for future enhancement
    const wishlistButtons = document.querySelectorAll('.wishlist-btn');
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            // Add wishlist functionality here
            console.log('Wishlist functionality not yet implemented');
        });
    });
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Utility function to debounce function calls
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

// Export functions for use in other scripts
window.StoreUtils = {
    formatCurrency,
    debounce
};
