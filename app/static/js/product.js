// Get CSRF token from meta tag
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').content;
}

// Show toast notification
function showToast(message, isError = false) {
    const toast = document.createElement('div');
    toast.className = `toast ${isError ? 'error' : 'success'}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Update badge count in navbar
function updateBadgeCount(selector, count) {
    const badge = document.querySelector(selector);
    if (badge) {
        badge.textContent = count;
    }
}

// Toggle wishlist status
function toggleWishlist(productId) {
    const card = document.querySelector(`.product-card[data-product-id="${productId}"]`);
    const wishlistBtn = card.querySelector('.wishlist-btn');
    
    // Get product details
    const productData = {
        product_id: productId,
        product_name: card.querySelector('.product-title').textContent,
        price: parseFloat(card.querySelector('.current-price').textContent.replace('₹', '')),
        image: card.querySelector('.product-image img').getAttribute('src').split('/').pop()
    };
    
    fetch('/add-to-wishlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(productData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Toggle button state
            wishlistBtn.classList.toggle('active', data.is_added);
            
            // Update wishlist count
            updateBadgeCount('.nav-icon:nth-child(2) .badge', data.wishlist_count);
            
            // Show success message
            showToast(data.message);
        } else {
            showToast(data.message || 'Failed to update wishlist', true);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error updating wishlist', true);
    });
}

// Check item status on page load
function checkItemStatus() {
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        const productId = card.dataset.productId;
        
        fetch('/check-item-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                product_id: productId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update wishlist button state
                const wishlistBtn = card.querySelector('.wishlist-btn');
                if (wishlistBtn && data.in_wishlist) {
                    wishlistBtn.classList.add('active');
                }
                
                // Update cart button state
                const cartBtn = card.querySelector('.cart-btn');
                if (cartBtn && data.in_cart) {
                    cartBtn.classList.add('active');
                }
            }
        })
        .catch(error => {
            console.error('Error checking item status:', error);
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check item status for all products
    if (document.querySelector('.product-card')) {
        checkItemStatus();
    }
}); 