// Get CSRF token from meta tag
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Function to track order
async function trackOrder(orderId) {
    try {
        const response = await fetch(`/track-order/${orderId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        if (response.ok) {
            const data = await response.json();
            showTrackingInfo(data);
        } else {
            throw new Error('Failed to get tracking information');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to get tracking information. Please try again.');
    }
}

// Function to buy item again
async function buyAgain(productId) {
    try {
        const response = await fetch('/buy-again', {
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
            if (data.success) {
                window.location.href = '/cart';
            } else {
                throw new Error(data.message || 'Failed to add item to cart');
            }
        } else {
            throw new Error('Failed to add item to cart');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to add item to cart. Please try again.');
    }
}

// Function to show tracking information
function showTrackingInfo(data) {
    const modal = document.createElement('div');
    modal.className = 'tracking-modal';
    modal.innerHTML = `
        <div class="tracking-modal-content">
            <span class="close-modal">&times;</span>
            <h3>Order Tracking</h3>
            <div class="tracking-timeline">
                ${data.timeline.map(step => `
                    <div class="tracking-step ${step.completed ? 'completed' : ''}">
                        <div class="step-icon">
                            <i class="fas ${getStepIcon(step.status)}"></i>
                        </div>
                        <div class="step-details">
                            <h4>${step.status}</h4>
                            <p>${step.date}</p>
                            <p>${step.location || ''}</p>
                        </div>
                    </div>
                `).join('')}
            </div>
            <div class="tracking-summary">
                <p><strong>Estimated Delivery:</strong> ${data.estimated_delivery}</p>
                <p><strong>Tracking Number:</strong> ${data.tracking_number}</p>
                <p><strong>Carrier:</strong> ${data.carrier}</p>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Add event listener for closing modal
    modal.querySelector('.close-modal').addEventListener('click', () => {
        modal.remove();
    });

    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Helper function to get appropriate icon for tracking step
function getStepIcon(status) {
    const icons = {
        'Order Placed': 'fa-shopping-cart',
        'Processing': 'fa-cog',
        'Shipped': 'fa-truck',
        'Out for Delivery': 'fa-truck-loading',
        'Delivered': 'fa-check-circle'
    };
    return icons[status] || 'fa-circle';
}

// Function to update order status
async function updateOrderStatus(orderId, status) {
    try {
        const response = await fetch('/update-order-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                order_id: orderId,
                status: status
            })
        });

        if (response.ok) {
            const data = await response.json();
            updateOrderUI(data);
        } else {
            throw new Error('Failed to update order status');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to update order status. Please try again.');
    }
}

// Function to update order UI
function updateOrderUI(data) {
    const orderCard = document.querySelector(`.order-card[data-order-id="${data.order_id}"]`);
    if (orderCard) {
        const statusBadge = orderCard.querySelector('.status-badge');
        if (statusBadge) {
            statusBadge.className = `status-badge ${data.status.toLowerCase()}`;
            statusBadge.textContent = data.status;
        }
    }
}

// Initialize orders page
document.addEventListener('DOMContentLoaded', () => {
    // Add event listeners for tracking buttons
    document.querySelectorAll('.track-order-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
        });
    });

    // Add event listeners for buy again buttons
    document.querySelectorAll('.buy-again-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
        });
    });
}); 