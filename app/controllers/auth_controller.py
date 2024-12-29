from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, Customer, Restaurant, DeliveryPerson

# 建立 Blueprint
auth_blueprint = Blueprint('auth', __name__, template_folder='../views/auth')

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 獲取表單資料
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')

        # 資料驗證
        if not username or len(username) < 3 or len(username) > 80:
            flash("Username must be between 3 and 80 characters.", "error")
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash("Email already exists. Please choose a different one.", "error")
            return redirect(url_for('auth.register'))

        if User.query.filter_by(phone=phone).first():
            flash("Phone number already exists. Please choose a different one.", "error")
            return redirect(url_for('auth.register'))

        # 儲存新使用者
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, email=email, phone=phone, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        # 根據角色儲存到對應的資料表
        if role == 'CUSTOMER':
            new_customer = Customer(user_id=new_user.id, name=username, email=email, phone=phone)
            db.session.add(new_customer)
        elif role == 'RESTAURANT':
            new_restaurant = Restaurant(user_id=new_user.id, name=username, phone=phone)
            db.session.add(new_restaurant)
        elif role == 'DELIVERY_PERSON':
            new_delivery_person = DeliveryPerson(user_id=new_user.id, name=username, phone=phone)
            db.session.add(new_delivery_person)

        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 獲取表單資料
        username = request.form.get('username')
        password = request.form.get('password')

        # 查詢使用者
        user = User.query.filter_by(username=username).first()

        # 檢查密碼
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = str(user.role) # 儲存使用者角色
            flash("Login successful!", "success")
            
            # 根據使用者角色重定向到不同頁面
            if user.role.value == 'ADMIN':
                return redirect(url_for('main.admin_dashboard'))
            elif user.role.value == 'RESTAURANT':
                return redirect(url_for('main.restaurant_dashboard'))
            elif user.role.value == 'CUSTOMER':
                return redirect(url_for('main.customer_dashboard'))
            elif user.role.value == 'DELIVERY_PERSON':
                return redirect(url_for('main.delivery_dashboard'))
            else:
                flash("Unknown role", "error")
                return redirect(url_for('auth.login'))  # 如果角色不匹配，返回登入頁

        else:
            flash("Login failed. Check your username and password.", "error")
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_blueprint.route('/logout')
def logout():
    session.pop('user_id', None)  # 清除 session 中的 user_id
    session.pop('role', None)  # 清除 session 中的 role
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))  # 登出後重定向到登入頁面
