function decreaseQuantity(id) {
    const quantityElement = document.getElementById(`quantity-${id}`);
    let quantity = parseInt(quantityElement.innerText);
    if (quantity > 1) {
        quantityElement.innerText = quantity - 1;
        updateTotal();
    } else {
        removeItem(id);
    }
}

function increaseQuantity(id) {
    const quantityElement = document.getElementById(`quantity-${id}`);
    let quantity = parseInt(quantityElement.innerText);
    quantityElement.innerText = quantity + 1;
    updateTotal();
}

function removeItem(id) {
    // In a real implementation, you would remove the item from the cart
    // For this demo, we'll just alert
    alert(`Item ${id} removed from cart`);
}

function updateTotal() {
    // In a real implementation, you would recalculate the total
    // This is just a placeholder
}

// Function to show empty cart (for demonstration)
function showEmptyCart() {
    document.getElementById('cart-with-items').style.display = 'none';
    document.getElementById('empty-cart').style.display = 'block';
}