from flask import Blueprint, render_template, request, redirect, url_for, flash,session
from app.models import Menu, Review, Restaurant,User,Order
from app import db
from sqlalchemy import func

# 定義 Blueprint
restaurant_bp = Blueprint('restaurant', __name__, url_prefix='/restaurant')

@restaurant_bp.route('/dashboard', methods=['GET'])
def restaurant_dashboard():
    user_id = session.get('user_id')

    # 查詢餐廳資訊
    restaurant = Restaurant.query.filter_by(user_id=user_id).first()
    menu_items = Menu.query.filter_by(restaurant_id=restaurant.id).all()

    # 計算每個餐廳的平均評分
    restaurant_avg_ratings = {}
    avg_rating = db.session.query(func.avg(Review.rating)) \
        .filter(Review.restaurant_id == restaurant.id).scalar()
    restaurant_avg_ratings[restaurant.id] = avg_rating if avg_rating is not None else 0  # 預設為 0

    return render_template(
        'restaurant/menu.html',
        menu_items=menu_items,
        restaurant_avg_ratings=restaurant_avg_ratings,
        restaurant=restaurant  # 確保 restaurant 也被傳遞
    )

def update_info(self, name=None, address=None, phone=None):
    if name:
        self.name = name
    if address:
        self.address = address
    if phone:
        self.phone = phone
    
    try:
        db.session.add(self)  # 確保這個物件被加入到 session 進行更新
    except Exception as e:
        print(f"Error updating info: {e}")

    
@restaurant_bp.route('/restaurant/edit', methods=['GET', 'POST'])
def edit_restaurant():
    user_id = session.get('user_id')
    restaurant = Restaurant.query.filter_by(user_id=user_id).first()

    if not restaurant:
        flash("找不到您的餐廳", "warning")
        return redirect(url_for('restaurant.restaurant_dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']  # 保持為字串類型，不要轉換為 float
        address = request.form['address']

        restaurant.name = name
        restaurant.phone = phone
        restaurant.address = address

        db.session.commit()
        flash('菜品已成功更新', 'success')

    return render_template('restaurant/edit_restaurant.html', restaurant=restaurant)


# 新增菜單
def add_menu(item_name, price, description, available, restaurant_id):
    new_item = Menu(
        restaurant_id=restaurant_id,
        item_name=item_name,
        price=price,
        description=description,
        available=available
    )
    db.session.add(new_item)
    db.session.commit()

# 編輯菜單
@restaurant_bp.route('/menu/edit', methods=['GET', 'POST'])
@restaurant_bp.route('/menu/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_menu(item_id=None):
    # 取得當前用戶的 user_id
    user_id = session.get('user_id')

    # 查詢菜品
    menu_item = Menu.query.get(item_id) if item_id else None

    # 如果是編輯模式，檢查用戶是否是該餐廳的擁有者
    if menu_item and menu_item.restaurant.user_id != user_id:
        flash("您無權編輯此菜品", "danger")
        return redirect(url_for('restaurant.restaurant_dashboard'))  # 若不是擁有者，重定向至餐廳儀表板

    # 查找當前用戶擁有的餐廳
    restaurant = Restaurant.query.filter_by(user_id=user_id).first()
    if not restaurant:
        flash("您沒有餐廳，無法新增菜品", "warning")
        return redirect(url_for('restaurant.restaurant_dashboard'))

    if request.method == 'POST':
        # 更新或新增菜單
        item_name = request.form['item_name']
        price = float(request.form['price'])
        description = request.form['description']
        available = request.form['available'] == 'yes'

        if menu_item:  # 編輯模式
            menu_item.item_name = item_name
            menu_item.price = price
            menu_item.description = description
            menu_item.available = available
            db.session.commit()
            flash('菜品已成功更新', 'success')
        else:  # 新增模式
            add_menu(item_name, price, description, available, restaurant.id)
            flash('菜品已成功新增', 'success')

        return redirect(url_for('restaurant.restaurant_dashboard'))

    return render_template('restaurant/menu_edit.html', menu_item=menu_item)

# 刪除菜單
@restaurant_bp.route('/menu/delete/<int:item_id>', methods=['POST'])
def delete_menu_item(item_id):
    item = Menu.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('菜品已成功刪除', 'success')
    return redirect(url_for('restaurant.restaurant_dashboard'))

@restaurant_bp.route('/orders/update/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.order_status = 'READY_FOR_PICKUP'  # 設定為備餐完畢
    db.session.commit()
    flash(f'訂單 {order.id} 狀態已更新為 READY_FOR_PICKUP', 'success')
    return redirect(url_for('restaurant.view_orders'))

# 查看訂單
@restaurant_bp.route('/orders', methods=['GET'])
def view_orders():
    user_id = session.get('user_id')

    if not user_id:
        flash("您需要登入才能查看訂單", "warning")
        return redirect(url_for('auth.login'))  # 如果沒有登入，重定向到登入頁面

    # 查詢當前用戶所擁有的餐廳
    restaurant = Restaurant.query.filter_by(user_id=user_id).first()

    if not restaurant:
        flash("找不到您的餐廳", "warning")
        return redirect(url_for('restaurant.restaurant_dashboard'))  # 如果找不到餐廳，重定向到餐廳儀表板

    # 根據餐廳的 ID 查詢訂單
    orders = Order.query.filter_by(restaurant_id=restaurant.id).all()

    # 計算訂單的總金額
    total_amount = sum(order.total_amount for order in orders)

    account_balance = restaurant.account_balance if restaurant else 0

    return render_template(
        'restaurant/order_status.html',
        orders=orders,
        total_amount=total_amount,
        account_balance=account_balance
    )


# 登入頁面
@restaurant_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')
