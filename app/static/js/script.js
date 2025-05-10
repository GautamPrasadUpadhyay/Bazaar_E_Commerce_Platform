document.addEventListener("DOMContentLoaded", function () {
    const testimonials = document.querySelectorAll(".testimonial");
    const prevButton = document.querySelector(".prev-testimony");
    const nextButton = document.querySelector(".next-testimony");
    let currentIndex = 0;

    function updateTestimonials() {
        testimonials.forEach((testimonial, index) => {
            testimonial.classList.remove("active");
            testimonial.style.display = "none";
        });

        testimonials[currentIndex].classList.add("active");
        testimonials[currentIndex].style.display = "block";
    }

    prevButton.addEventListener("click", function () {
        currentIndex = (currentIndex === 0) ? testimonials.length - 1 : currentIndex - 1;
        updateTestimonials();
    });

    nextButton.addEventListener("click", function () {
        currentIndex = (currentIndex === testimonials.length - 1) ? 0 : currentIndex + 1;
        updateTestimonials();
    });

    updateTestimonials(); // Initialize display
});

function showToast(message, isSuccess = true) {
    const toast = document.getElementById('successToast');
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    toast.classList.add('show');
    
    if (!isSuccess) {
        toast.classList.add('error');
    }
    
    setTimeout(() => {
        toast.classList.remove('show', 'error');
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to all "Add to Cart" buttons
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get product details from data attributes
            const productId = this.getAttribute('data-product-id');
            const productName = this.getAttribute('data-product-name');
            const productPrice = this.getAttribute('data-product-price');
            const productImage = this.getAttribute('data-product-image');
            
            // Send product data to server
            addToCart(productId, productName, productPrice, productImage);
        });
    });
});

function addToCart(productId, productName, productPrice, productImage) {
    // Get CSRF token from meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    
    // Create fetch request to add item to cart
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
            // Update cart icon badge count
            const cartBadge = document.querySelector('.nav-icon .badge');
            if (cartBadge) {
                cartBadge.textContent = data.cart_count;
            }
            
            // Show success message
            showToast('Product added to cart successfully!');
            
            // Update button state
            const button = document.querySelector(`.add-to-cart-btn[data-product-id="${productId}"]`);
            if (button) {
                button.classList.add('in-cart');
                button.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    button.innerHTML = '<i class="fas fa-shopping-cart"></i>';
                    button.classList.remove('in-cart');
                }, 2000);
            }
        } else {
            showToast('Error adding product to cart: ' + data.message, false);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred while adding the product to cart.', false);
    });
}

// Wishlist

function addToWishlist(productId, productName, productPrice, productImage) {
    // Get CSRF token from meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    
    // Create fetch request to add item to cart
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
            image: productImage,
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart icon badge count
            const wishlistBadge = document.querySelector('.nav-icon .badge');
            if (wishlistBadge) {
                wishlistBadge.textContent = data.wishlist_count;
            }
            
            // Show success message
            showToast('Product added to wishlist successfully!');
            
            // Update button state
            const button = document.querySelector(`.add-to-wishlist-btn[data-product-id="${productId}"]`);
            if (button) {
                button.classList.add('in-wishlist');
                button.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    button.innerHTML = '<i class="fas fa-heart"></i>';
                    button.classList.remove('in-wishlist');
                }, 2000);
            }
        } else {
            showToast('Error adding product to wishlist: ' + data.message, false);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred while adding the product to wishlist.', false);
    });
}