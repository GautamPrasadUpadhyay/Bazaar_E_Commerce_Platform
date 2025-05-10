document.addEventListener('DOMContentLoaded', function() {
    // Add click event listeners to all "Add to Wishlist" buttons
    const addToWishlistButtons = document.querySelectorAll('.add-to-wishlist-btn');
    
    addToWishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get product details from data attributes
            const productId = this.dataset.productId;
            const productName = this.dataset.productName;
            const productPrice = this.dataset.productPrice;
            const productImage = this.dataset.productImage;
            
            // Add product to wishlist
            addToWishlist(productId, productName, productPrice, productImage);
        });
    });
});

function addToWishlist(productId, productName, productPrice, productImage) {
    // Get CSRF token
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    
    // Send request to add item to wishlist
    fetch('/add_to_wishlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            product_id: productId,
            product_name: productName,
            price: productPrice,
            image: productImage
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update wishlist badge count
            updateWishlistBadge(data.wishlist_count);
            
            // Show success message
            showToast('Product added to wishlist successfully!');
            
            // Change button style to indicate product was added
            const button = document.querySelector(`.add-to-wishlist-btn[data-product-id="${productId}"]`);
            if (button) {
                button.classList.add('added');
                setTimeout(() => {
                    button.classList.remove('added');
                }, 2000);
            }
        } else {
            showToast('Error adding product to wishlist: ' + data.message, true);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', true);
    });
}

function removeFromWishlist(productId) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    
    fetch(`/remove-from-wishlist/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove item from DOM
            const item = document.querySelector(`.wishlist-item[data-product-id="${productId}"]`);
            if (item) {
                item.remove();
            }
            
            // Update wishlist count in navbar
            const wishlistBadge = document.querySelector('.nav-icon .badge');
            if (wishlistBadge) {
                wishlistBadge.textContent = data.wishlist_count;
            }
            
            // Show empty state if no items left
            if (data.wishlist_count === 0) {
                location.reload();
            }
            
            showToast('Item removed from wishlist successfully');
        } else {
            showToast(data.message || 'Error removing item from wishlist', true);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error removing item from wishlist', true);
    });
}

function moveToCart(productId) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    
    fetch(`/move-to-cart/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart and wishlist badges
            updateWishlistBadge(data.wishlist_count);
            updateCartBadge(data.cart_count);
            
            // Remove item from wishlist DOM
            const item = document.querySelector(`.wishlist-item[data-product-id="${productId}"]`);
            if (item) {
                item.remove();
            }
            
            // Show empty state if no items left
            if (data.wishlist_count === 0) {
                location.reload();
            }
            
            showToast('Item moved to cart successfully');
        } else {
            showToast(data.message || 'Error moving item to cart', true);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error moving item to cart', true);
    });
}

function updateWishlistBadge(count) {
    const wishlistBadge = document.querySelector('.nav-icon:nth-child(2) .badge');
    if (wishlistBadge) {
        wishlistBadge.textContent = count;
    }
}

function updateCartBadge(count) {
    const cartBadge = document.querySelector('.nav-icon:first-child .badge');
    if (cartBadge) {
        cartBadge.textContent = count;
    }
}

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

// Add CSS for toast messages
const style = document.createElement('style');
style.textContent = `
.toast {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%) translateY(100px);
    background: #333;
    color: white;
    padding: 12px 24px;
    border-radius: 4px;
    opacity: 0;
    transition: all 0.3s ease;
    z-index: 1000;
}

.toast.show {
    transform: translateX(-50%) translateY(0);
    opacity: 1;
}

.toast.success {
    background: #4CAF50;
}

.toast.error {
    background: #f44336;
}

.wishlist-item {
    display: flex;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #eee;
}

.wishlist-item-image {
    width: 100px;
    height: 100px;
    margin-right: 20px;
}

.wishlist-item-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.wishlist-item-details {
    flex-grow: 1;
}

.wishlist-item-actions {
    display: flex;
    gap: 10px;
}

.add-to-cart-btn {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.add-to-cart-btn:hover {
    background-color: #45a049;
}

.remove-from-wishlist {
    background-color: #f44336;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.remove-from-wishlist:hover {
    background-color: #da190b;
}

.empty-wishlist {
    text-align: center;
    padding: 40px;
}

.empty-wishlist i {
    font-size: 48px;
    color: #ccc;
    margin-bottom: 20px;
}
`;
document.head.appendChild(style); 