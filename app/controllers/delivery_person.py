from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import DeliveryPerson, Order, OrderStatusEnum,PaymentStatusEnum,Restaurant
from app import db
from decimal import Decimal

# 定義 Blueprint
delivery_bp = Blueprint('delivery', __name__, url_prefix='/delivery')

def validate_order_status(order, expected_status, delivery_person_id=None):
    """通用訂單狀態校驗函數"""
    if order.order_status != expected_status:
        
        return False, "訂單狀態不符合預期"
    if delivery_person_id and order.delivery_person_id != delivery_person_id:
        return False, "外送員不匹配"
    return True, None

@delivery_bp.route('/dashboard', methods=['GET'])
def delivery_dashboard():
    """外送員儀表板"""
    user_id = session.get('user_id')

    if not user_id:
        flash("請先登入", "warning")
        return redirect(url_for('auth.login'))

    # 確認外送員身份
    delivery_person = DeliveryPerson.query.filter_by(user_id=user_id).first()
    if not delivery_person:
        flash("找不到外送員資訊，請確認您的帳號", "warning")
        return redirect(url_for('auth.login'))

    # 查詢外送員的歷史訂單數據
    completed_orders = Order.query.filter_by(
        delivery_person_id=delivery_person.id,
        order_status=OrderStatusEnum.DELIVERED
    ).all()

    # 計算收入總額
    total_earnings = sum(order.total_amount * 0.5 for order in completed_orders)  # 假設提成為 50%

    return render_template(
        'delivery/delivery_dashboard.html',
        delivery_person=delivery_person,
        completed_orders=completed_orders,
        total_earnings=total_earnings
    )

@delivery_bp.route('/deorders', methods=['GET'])
def deorders():
    """顯示待接單列表"""
    available_orders = Order.query.filter_by(order_status=OrderStatusEnum.READY_FOR_PICKUP).all()
    
    # 為每筆訂單找到對應的餐廳地址
    data = [{
        "id": order.id,
        "restaurant_address": Restaurant.query.get(order.restaurant_id).address,
        "delivery_address": order.delivery_address,
        "total_amount": order.total_amount,
    } for order in available_orders]
    
    return render_template('delivery/deliverylist.html', orders=data)


@delivery_bp.route('/orders/accept/<int:order_id>', methods=['POST'])
def accept_order(order_id):
    """接受訂單"""
    user_id = session.get('user_id')

    # 確認外送員身份
    delivery_person = DeliveryPerson.query.filter_by(user_id=user_id).first()
    if not delivery_person:
        flash("找不到外送員資訊，請先登入", "warning")
        return redirect(url_for('auth.login'))

    # 查詢訂單
    order = Order.query.get_or_404(order_id)
    is_valid, error_message = validate_order_status(order, OrderStatusEnum.READY_FOR_PICKUP)
    if not is_valid:
        flash(error_message, "danger")
        return redirect(url_for('main.dashboard'))
    restaurant = Restaurant.query.get(order.restaurant_id)

    # 確認外送員當前是否有進行中的訂單
    if delivery_person.current_order_id:
        flash("您已有正在配送的訂單，無法接新單", "warning")
        return redirect(url_for('main.dashboard'))

    # 更新訂單狀態
    order.order_status = OrderStatusEnum.OUT_FOR_DELIVERY
    order.delivery_person_id = delivery_person.id
    delivery_person.current_order_id = order.id

    try:
        db.session.commit()
    except Exception as e:
        print(f"[ERROR] 接單失敗: {e}")
        flash("接單過程中發生錯誤，請稍後再試", "danger")
        return redirect(url_for('main.dashboard'))
    data=[{
    "id": order.id,
    "order_status": order.order_status.name,
    "restaurant_name": restaurant.name,
    "payment_status": order.payment_status,
    "total_amount": order.total_amount,
    "delivery_address": order.delivery_address,
    "restaurant_address": restaurant.address,
    "order_details": order.order_details,
   }]
    flash(f"成功接單：訂單 {order.id}", "success")
    return render_template('delivery/start_delivery.html', orders=data)

@delivery_bp.route('/start_delivery', methods=['GET'])
def start_delivery():
    """開始配送"""
    user_id = session.get('user_id')

    # 確認外送員身份
    delivery_person = DeliveryPerson.query.filter_by(user_id=user_id).first()
    if not delivery_person:
        flash("找不到外送員資訊，請先登入", "warning")
        return redirect(url_for('auth.login'))

    # 查詢外送員正在配送的訂單
    orders = Order.query.filter_by(
        delivery_person_id=delivery_person.id,
        order_status=OrderStatusEnum.OUT_FOR_DELIVERY
    ).all()
    restaurant = Restaurant.query.get(orders.restaurant_id)


    if not orders:
        flash("目前沒有正在配送的訂單", "info")
        return redirect(url_for('main.dashboard'))

    # 整理數據
    data = [{
        "id": order.id,
        "order_status": order.order_status.name,
        "restaurant_name": restaurant.restaurant_name,
        "payment_status": order.payment_status,
        "restaurant_name": order.name,
        "total_amount": order.total_amount,
        "delivery_address": order.delivery_address,
        "restaurant_address": restaurant.address,
        "customer_phone": order.customer_phone
    } for order in orders]
    
    return render_template('delivery/start_delivery.html', data=data)

@delivery_bp.route('/orders/complete/<int:order_id>', methods=['POST', 'GET'])
def complete_order(order_id):
    """完成訂單"""
    user_id = session.get('user_id')  # 確保變數名一致
    if not user_id:
        flash("請先登入", "warning")
        return redirect(url_for('auth.login'))

    # 查找外送員
    delivery_person = DeliveryPerson.query.filter_by(user_id=user_id).first()
    if not delivery_person:
        flash("找不到外送員資訊，請確認您的帳號", "warning")
        return redirect(url_for('auth.login'))

    # 查找訂單
    order = Order.query.get_or_404(order_id)
    if order.order_status != OrderStatusEnum.OUT_FOR_DELIVERY:
        flash("訂單無法完成配送，請確認狀態", "warning")
        return redirect(url_for('delivery.view_current_order'))

    # 更新訂單狀態與外送員收益
    try:
        order.payment_status = PaymentStatusEnum.COMPLETED
        order.order_status = OrderStatusEnum.DELIVERED
        delivery_person.earnings += order.total_amount * Decimal('0.05')
        delivery_person.current_order_id = None  # 完成訂單後清除正在配送的訂單
        db.session.commit()
        flash(f"訂單 {order.id} 已完成配送", "success")
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] 完成訂單失敗: {e}")
        flash("完成訂單過程中發生錯誤，請稍後再試", "danger")
        return redirect(url_for('delivery.delivery_dashboard'))

    return redirect(url_for('delivery.delivery_dashboard'))


@delivery_bp.route('/current-order', methods=['GET'])
def view_current_order():
    """查看當前進行中的訂單"""
    user_id = session.get('user_id')

    # 確認外送員身份
    delivery_person = DeliveryPerson.query.filter_by(user_id=user_id).first()
    if not delivery_person:
        flash("找不到外送員資訊，請先登入", "warning")
        return redirect(url_for('auth.login'))

    # 查詢進行中的訂單
    active_order = Order.query.filter_by(
        delivery_person_id=delivery_person.id,
        order_status=OrderStatusEnum.OUT_FOR_DELIVERY
    ).first()

    return render_template(
        'delivery/start_delivery.html',
        active_order=active_order
    )

