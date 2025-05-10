document.addEventListener('DOMContentLoaded', function() {
    // Add click event listeners to all "Add to Cart" buttons
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get product details from data attributes
            const productId = this.dataset.productId;
            const productName = this.dataset.productName;
            const productPrice = this.dataset.productPrice;
            const productImage = this.dataset.productImage;
            
            // Add product to cart
            addProductToCart(productId, productName, productPrice, productImage);
        });
    });
    
    // Add event listeners for quantity buttons in cart
    const quantityButtons = document.querySelectorAll('.qty-btn');
    if (quantityButtons) {
        quantityButtons.forEach(button => {
            button.addEventListener('click', function() {
                const productId = this.closest('.cart-item').dataset.productId;
                const isIncrease = this.classList.contains('plus');
                updateQuantity(productId, isIncrease ? 1 : -1);
            });
        });
    }
    
    // Add event listeners for remove buttons in cart
    const removeButtons = document.querySelectorAll('.cart-item-remove button');
    if (removeButtons) {
        removeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const productId = this.closest('.cart-item').dataset.productId;
                removeFromCart(productId);
            });
        });
    }
});

function addProductToCart(productId, productName, productPrice, productImage) {
    // Get CSRF token
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Send request to add item to cart
    fetch('/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            product_id: productId,
            product_name: productName,
            price: productPrice,
            image: productImage,
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart badge count
            updateCartBadge(data.cart_count);
            
            // Show success message
            showToast('Product added to cart successfully!');
            
            // Change button style to indicate product was added
            const button = document.querySelector(`.add-to-cart-btn[data-product-id="${productId}"]`);
            if (button) {
                button.classList.add('added');
                setTimeout(() => {
                    button.classList.remove('added');
                }, 2000);
            }
        } else {
            showToast('Error adding product to cart: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.');
    });
}

// Get CSRF token from meta tag
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Function to update cart item quantity
async function updateQuantity(productId, change) {
    try {
        const response = await fetch('/update-cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                product_id: productId,
                change: change
            })
        });

        if (response.ok) {
            const data = await response.json();
            updateCartUI(data);
        } else {
            throw new Error('Failed to update quantity');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to update quantity. Please try again.');
    }
}

// Function to remove item from cart
async function removeFromCart(productId) {
    if (!confirm('Are you sure you want to remove this item from your cart?')) {
        return;
    }

    try {
        const response = await fetch('/remove-from-cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                product_id: productId
            })
        });

        if (response.ok) {
            const data = await response.json();
            updateCartUI(data);
        } else {
            throw new Error('Failed to remove item');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to remove item. Please try again.');
    }
}

// Function to move item to wishlist
async function moveToWishlist(productId) {
    try {
        const response = await fetch('/move-to-wishlist', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                product_id: productId
            })
        });

        if (response.ok) {
            const data = await response.json();
            updateCartUI(data);
            alert('Item moved to wishlist successfully!');
        } else {
            throw new Error('Failed to move item to wishlist');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to move item to wishlist. Please try again.');
    }
}

// Function to proceed to checkout
function proceedToCheckout() {
    if (!document.querySelector('.cart-item')) {
        alert('Your cart is empty!');
        return;
    }
    window.location.href = '/checkout';
}

// Function to update cart UI
function updateCartUI(data) {
    // Update cart items
    const cartContainer = document.querySelector('.cart-items');
    if (data.cart_items && data.cart_items.length > 0) {
        cartContainer.innerHTML = data.cart_items.map(item => `
            <div class="cart-item" data-product-id="${item.product_id}">
                <div class="cart-item-image">
                    <img src="/static/${item.image}" alt="${item.product_name}">
                </div>
                <div class="cart-item-details">
                    <h3>${item.product_name}</h3>
                    <p class="cart-item-price">₹${item.price}</p>
                </div>
                <div class="cart-item-quantity">
                    <button class="qty-btn minus" onclick="updateQuantity('${item.product_id}', -1)">-</button>
                    <input type="number" class="qty-input" value="${item.quantity}" min="1" max="10" readonly>
                    <button class="qty-btn plus" onclick="updateQuantity('${item.product_id}', 1)">+</button>
                </div>
                <div class="cart-item-subtotal">
                    ₹${item.price * item.quantity}
                </div>
                <div class="cart-item-actions">
                    <button class="move-to-wishlist-btn" onclick="moveToWishlist('${item.product_id}')">
                        <i class="fas fa-heart"></i> Move to Wishlist
                    </button>
                    <button class="remove-from-cart" onclick="removeFromCart('${item.product_id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    } else {
        cartContainer.innerHTML = `
            <div class="empty-cart">
                <i class="fas fa-shopping-cart"></i>
                <h3>Your cart is empty</h3>
                <p>Looks like you haven't added anything to your cart yet.</p>
                <a href="/" class="continue-shopping-btn">
                    Continue Shopping
                </a>
            </div>
        `;
    }

    // Update cart summary
    if (data.summary) {
        document.querySelector('.summary-item:nth-child(1) span:last-child').textContent = `₹${data.summary.subtotal}`;
        document.querySelector('.summary-item:nth-child(2) span:last-child').textContent = `₹${data.summary.shipping}`;
        document.querySelector('.summary-item.total span:last-child').textContent = `₹${data.summary.total}`;
    }

    // Update cart badge
    const cartBadge = document.querySelector('.nav-icon .badge');
    if (cartBadge) {
        cartBadge.textContent = data.cart_count || '0';
    }
}

function updateCartBadge(count) {
    const cartBadge = document.querySelector('.nav-icon .badge');
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
`;
document.head.appendChild(style);