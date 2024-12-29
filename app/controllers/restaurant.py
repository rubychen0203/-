from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Menu, Order,Restaurant,Review
from sqlalchemy import func

restaurant_bp = Blueprint('restaurant', __name__, url_prefix='/restaurant')


@restaurant_bp.route('/dashboard', methods=['GET'])
def restaurant_dashboard():
    # 在這裡你可以進行任何其他邏輯，例如顯示餐廳的基本資料
    return render_template('restaurant/dashboard.html')  # 顯示餐廳主頁

@restaurant_bp.route('/menu', methods=['GET'])
def view_menu():
    menu_items = Menu.query.all()  # 查詢所有菜品
    restaurant_avg_ratings = {}

    # 計算每個餐廳的平均評分
    for item in menu_items:
        restaurant_id = item.restaurant_id
        # 計算餐廳的平均評分
        avg_rating = db.session.query(func.avg(Review.rating)).filter(Review.restaurant_id == restaurant_id).scalar()

        # 若無評分則設置為 None
        restaurant_avg_ratings[restaurant_id] = avg_rating if avg_rating is not None else None

    return render_template('restaurant/menu.html', menu_items=menu_items, restaurant_avg_ratings=restaurant_avg_ratings)

def add_menu(item_name, price, description, available):
    restaurant_id = 1  # 預設餐廳 ID 為 1

    new_item = Menu(
        restaurant_id=restaurant_id,
        item_name=item_name,
        price=price,
        description=description,
        available=available
    )
    db.session.add(new_item)
    db.session.commit()

@restaurant_bp.route('/menu/edit', methods=['GET', 'POST']) 
@restaurant_bp.route('/menu/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_menu(item_id=None):
    if item_id:  # 編輯模式
        menu_item = Menu.query.get_or_404(item_id)
    else:  # 新增模式
        menu_item = None

    if request.method == 'POST':
        item_name = request.form['item_name']
        price = float(request.form['price'])
        description = request.form['description']
        available = True if request.form['available'] == 'yes' else False
        
        if menu_item:  # 如果有菜品項目，進行編輯
            menu_item.item_name = item_name
            menu_item.price = price
            menu_item.description = description
            menu_item.available = available
            db.session.commit()  # 提交修改
            flash('菜品已成功更新', 'success')
        else:  # 新增模式
            add_menu(item_name, price, description, available)
            flash('菜品已成功新增', 'success')

        return redirect(url_for('restaurant.view_menu'))

    return render_template('restaurant/menu_edit.html', menu_item=menu_item)

@restaurant_bp.route('/menu/delete/<int:item_id>', methods=['POST'])
def delete_menu_item(item_id):
    item = Menu.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('菜品已成功刪除', 'success')
    return redirect(url_for('restaurant.view_menu'))


@restaurant_bp.route('/orders/update/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    # 查詢訂單
    order = Order.query.get(order_id)  # 查詢訂單
    if order:
        order.order_status = 'READY_FOR_PICKUP'  # 設定為備餐完畢
        db.session.commit()  # 提交到資料庫
        flash(f'訂單 {order.id} 狀態已更新為 READY_FOR_PICKUP', 'success')
    else:
        flash(f'訂單 {order_id} 未找到', 'danger')

    # 重定向回訂單頁面
    return redirect(url_for('restaurant.view_orders'))  # 使用正確的路由名稱


@restaurant_bp.route('/orders', methods=['GET'])
def view_orders():
    # 查詢所有訂單
    orders = Order.query.all()
    
    # 計算所有訂單的總金額並累加到餐廳的帳戶餘額
    total_amount = sum(order.total_amount for order in orders)
    
    # 查詢餐廳帳戶餘額並更新
    restaurant = Restaurant.query.get(1)  # 假設只有一個餐廳，ID 為 1
    if restaurant:
        # 更新餐廳帳戶餘額
        restaurant.account_balance += total_amount
        db.session.commit()  # 提交更新到資料庫
    
    # 查詢更新後的帳戶餘額
    account_balance = restaurant.account_balance if restaurant else 0

    return render_template('restaurant/order_status.html', orders=orders, total_amount=total_amount, account_balance=account_balance)



@restaurant_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

