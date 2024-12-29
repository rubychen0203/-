from flask import Blueprint, redirect, url_for, render_template, session, flash

# 建立 Blueprint
main_blueprint = Blueprint('main', __name__)

# 根路徑跳轉至 login 或 home
@main_blueprint.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.home'))  # 如果已登入，跳轉到 home 頁面
    return redirect(url_for('auth.login'))  # 否則跳轉到登入頁

# 登入頁面
@main_blueprint.route('/login')
def login():
    return render_template('login.html')

# 註冊頁面
@main_blueprint.route('/register')
def register():
    return render_template('register.html')

# 根據用戶角色導向不同的主頁
@main_blueprint.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_role = session.get('role')  # 從 session 獲取用戶角色
        if user_role == 'ADMIN':
            return redirect(url_for('main.platform_dashboard'))  # 管理員主頁
        elif user_role == 'RESTAURANT':
            return redirect(url_for('restaurant.restaurant_dashboard'))  # 商家主頁
        elif user_role == 'CUSTOMER':
            return redirect(url_for('main.customer_dashboard'))  # 客戶主頁
        elif user_role == 'DELIVERY_PERSON':
            return redirect(url_for('main.delivery_dashboard'))  # 外送員主頁
        else:
            flash("Invalid role.", "warning")
            return redirect(url_for('auth.login'))  # 若角色無效，跳轉到登入頁面
    else:
        flash("You need to log in first.", "warning")
        return redirect(url_for('auth.login'))  # 若未登入，跳轉到登入頁面

# 管理員頁面
@main_blueprint.route('/platform_dashboard')
def admin_dashboard():
    if 'user_id' in session and session.get('role') == 'ADMIN':
        return render_template('platform/platform_dashboard.html')  # 顯示管理員主頁
    else:
        flash("You need to log in as an admin.", "warning")
        return redirect(url_for('auth.login'))  # 若未登入，跳轉到登入頁面

# 商家主頁
@main_blueprint.route('/restaurant_dashboard')
def restaurant_dashboard():
    if 'user_id' in session and session.get('role') == 'RESTAURANT':
        return render_template('restaurant/restaurant_dashboard.html')  # 顯示餐廳主頁
    else:
        flash("You need to log in as a restaurant.", "warning")
        return redirect(url_for('auth.login'))  # 若未登入，跳轉到登入頁面

# 客戶主頁
@main_blueprint.route('/customer_dashboard')
def customer_dashboard():
    if 'user_id' in session and session.get('role') == 'CUSTOMER':
        return render_template('customer/customer_dashboard.html')  # 顯示客戶主頁
    else:
        flash("You need to log in as a customer.", "warning")
        return redirect(url_for('auth.login'))  # 若未登入，跳轉到登入頁面

# 外送員主頁
@main_blueprint.route('/delivery_dashboard')
def delivery_dashboard():
    if 'user_id' in session and session.get('role') == 'DELIVERY_PERSON':
        return render_template('delivery/delivery_dashboard.html')  # 顯示外送員主頁
    else:
        flash("You need to log in as a delivery person.", "warning")
        return redirect(url_for('auth.login'))  # 若未登入，跳轉到登入頁