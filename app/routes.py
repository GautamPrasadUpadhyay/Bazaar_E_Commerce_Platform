from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import Product, Order, OrderItem
from app.extensions import db

@bp.route('/ordernow/<int:product_id>', methods=['GET'])
@login_required
def ordernow(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('ordernow.html', product=product)

@bp.route('/place_order', methods=['POST'])
@login_required
def place_order():
    try:
        data = request.get_json()
        
        # Create new order
        order = Order(
            user_id=current_user.id,
            status='pending',
            total_amount=float(data.get('total_amount', 0)),
            shipping_address=data.get('address', ''),
            payment_method=data.get('payment_method', ''),
            phone_number=data.get('phone', ''),
            city=data.get('city', ''),
            state=data.get('state', ''),
            pincode=data.get('pincode', '')
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=data.get('product_id'),
            quantity=1,
            price=float(data.get('product_price', 0))
        )
        
        db.session.add(order_item)
        db.session.commit()
        
        # Calculate estimated delivery date (3-5 business days)
        from datetime import datetime, timedelta
        delivery_date = datetime.now() + timedelta(days=4)
        
        return jsonify({
            'success': True,
            'order_id': order.id,
            'estimated_delivery': delivery_date.strftime('%B %d, %Y')
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
