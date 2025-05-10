// Get CSRF token from meta tag
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Current step in the order process
let currentStep = 1;
let selectedPaymentMethod = null;
let orderData = {
    product_id: null,
    product_price: null,
    total_amount: null
};

// Function to update step indicators
function updateSteps() {
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        if (index + 1 < currentStep) {
            step.classList.remove('active');
            step.classList.add('completed');
        } else if (index + 1 === currentStep) {
            step.classList.add('active');
            step.classList.remove('completed');
        } else {
            step.classList.remove('active', 'completed');
        }
    });
}

// Function to show loading overlay
function showLoading() {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = '<div class="loading-spinner"></div>';
    document.body.appendChild(overlay);
}

// Function to hide loading overlay
function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Function to show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
}

// Function to show success message
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    document.body.appendChild(successDiv);
    setTimeout(() => successDiv.remove(), 3000);
}

// Function to validate phone number
function validatePhoneNumber(phone) {
    const phoneRegex = /^[0-9]{10}$/;
    return phoneRegex.test(phone);
}

// Function to validate pincode
function validatePincode(pincode) {
    const pincodeRegex = /^[0-9]{6}$/;
    return pincodeRegex.test(pincode);
}

// Function to proceed to address section
function proceedToAddress() {
    // Store product data
    const productElement = document.querySelector('.order-summary-item');
    orderData.product_id = productElement.dataset.productId;
    orderData.product_price = parseFloat(document.querySelector('.order-summary-item-price').textContent.replace('₹', ''));
    orderData.total_amount = parseFloat(document.querySelector('.order-total-item.total span:last-child').textContent.replace('₹', ''));

    currentStep = 2;
    updateSteps();
    document.getElementById('orderSummarySection').style.display = 'none';
    document.getElementById('deliveryAddressSection').style.display = 'block';
}

// Function to go back to order summary
function backToSummary() {
    currentStep = 1;
    updateSteps();
    document.getElementById('deliveryAddressSection').style.display = 'none';
    document.getElementById('orderSummarySection').style.display = 'block';
}

// Function to validate address form
function validateAddressForm() {
    const form = document.getElementById('addressForm');
    const phone = form.phone.value;
    const pincode = form.pincode.value;

    if (!form.checkValidity()) {
        form.reportValidity();
        return false;
    }

    if (!validatePhoneNumber(phone)) {
        showError('Please enter a valid 10-digit phone number');
        return false;
    }

    if (!validatePincode(pincode)) {
        showError('Please enter a valid 6-digit pincode');
        return false;
    }

    return true;
}

// Function to proceed to payment section
function proceedToPayment() {
    if (!validateAddressForm()) {
        return;
    }

    currentStep = 3;
    updateSteps();
    document.getElementById('deliveryAddressSection').style.display = 'none';
    document.getElementById('paymentSection').style.display = 'block';
}

// Function to go back to address section
function backToAddress() {
    currentStep = 2;
    updateSteps();
    document.getElementById('paymentSection').style.display = 'none';
    document.getElementById('deliveryAddressSection').style.display = 'block';
}

// Function to select payment method
function selectPaymentMethod(method) {
    selectedPaymentMethod = method;
    const paymentMethods = document.querySelectorAll('.payment-method');
    paymentMethods.forEach(pm => {
        if (pm.getAttribute('onclick').includes(method)) {
            pm.classList.add('selected');
        } else {
            pm.classList.remove('selected');
        }
    });
}

// Function to place order
async function placeOrder() {
    if (!selectedPaymentMethod) {
        showError('Please select a payment method');
        return;
    }

    showLoading();

    try {
        const formData = new FormData(document.getElementById('addressForm'));
        const addressData = Object.fromEntries(formData.entries());

        const orderPayload = {
            ...orderData,
            ...addressData,
            payment_method: selectedPaymentMethod
        };

        const response = await fetch('/place_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(orderPayload)
        });

        const data = await response.json();

        if (response.ok && data.success) {
            currentStep = 4;
            updateSteps();
            document.getElementById('paymentSection').style.display = 'none';
            document.getElementById('successSection').style.display = 'block';
            document.getElementById('orderId').textContent = data.order_id;
            document.getElementById('deliveryDate').textContent = data.estimated_delivery;
            showSuccess('Order placed successfully!');
        } else {
            throw new Error(data.message || 'Failed to place order');
        }
    } catch (error) {
        showError(error.message || 'An error occurred while placing your order. Please try again.');
    } finally {
        hideLoading();
    }
}

// Function to edit order
function editOrder() {
    window.location.href = document.referrer;
}

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    updateSteps();
    
    // Add input validation listeners
    const phoneInput = document.getElementById('phone');
    const pincodeInput = document.getElementById('pincode');

    phoneInput.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10);
    });

    pincodeInput.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '').slice(0, 6);
    });
}); 