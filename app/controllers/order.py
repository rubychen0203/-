from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Order, PaymentStatusEnum
from flask_login import login_required, current_user

order_bp = Blueprint('order', __name__)

# 創建訂單
@order_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_order():
    if request.method == 'POST':
        restaurant_id = request.form['restaurant_id']
        delivery_person_id = request.form['delivery_person_id']
        total_amount = request.form['total_amount']
        delivery_address = request.form['delivery_address']

        new_order = Order(
            customer_id=current_user.id,
            restaurant_id=restaurant_id,
            delivery_person_id=delivery_person_id,
            total_amount=total_amount,
            delivery_address=delivery_address,
            order_status='Pending',
            payment_status=PaymentStatusEnum.PENDING
        )
        
        db.session.add(new_order)
        db.session.commit()

        flash('Your order has been created!', 'success')
        return redirect(url_for('order.view_orders'))
    
    return render_template('orders/create_order.html')

# 查看所有訂單
@order_bp.route('/')
@login_required
def view_orders():
    # 這裡假設只顯示目前用戶的訂單
    orders = Order.query.filter_by(customer_id=current_user.id).all()
    return render_template('orders/view_orders.html', orders=orders)

# 更新訂單狀態
@order_bp.route('/update/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'POST':
        order.order_status = request.form['order_status']
        order.payment_status = request.form['payment_status']
        db.session.commit()

        flash('Order status has been updated!', 'success')
        return redirect(url_for('order.view_orders'))
    
    return render_template('orders/update_order.html', order=order)
