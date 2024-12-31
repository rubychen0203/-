from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from app.controllers.cus_db import get_restaurants, get_menus_by_restaurant, get_menu_item, insert_order, get_order_status, update_order_status,get_customer_id_by_user_id

customer_blueprint = Blueprint('customer', __name__, template_folder='../views/customer')

@customer_blueprint.route('/')
def index():
    restaurants = get_restaurants()
    print(restaurants)
    return render_template('customer_dashboard.html', restaurants=restaurants)  

@customer_blueprint.route('/menu/<int:restaurant_id>')
def menu(restaurant_id):
    
    menus = get_menus_by_restaurant(restaurant_id)
    restaurant = next(r for r in get_restaurants() if r['id'] == restaurant_id)
    print(session['user_id'],session['role'])
    if 'cart' not in session:
        session['cart'] = []

    return render_template('menu.html', menus=menus, restaurant=restaurant)

@customer_blueprint.route('/add_to_cart/<int:item_id>')
def add_to_cart(item_id):
    item = get_menu_item(item_id)
    print(session['user_id'],session['role'])
    if item:
        item['price'] = float(item['price'])
        session['cart'].append(item)
        session.modified = True

    return redirect(url_for('customer.menu', restaurant_id=item['restaurant_id']))

@customer_blueprint.route('/cart/<int:restaurant_id>')
def view_cart(restaurant_id):
    print(session['user_id'],session['role'])
    return render_template('cart.html', cart=session['cart'],restaurant_id=restaurant_id)

@customer_blueprint.route('/checkout', methods=['POST'])
def checkout():
    print(session['user_id'],session['role'])
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('main.index'))

    restaurant_id = session['cart'][0]['restaurant_id']
    order_details=str(item['item_name'] for item in session['cart'])
    total_amount = sum(item['price'] for item in session['cart'])
    order_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    delivery_address = request.form['delivery_address']
    print(session['user_id'])
    print(session['role'])
    customer_id=get_customer_id_by_user_id(session['user_id'])
    print(customer_id)
    print(customer_id)
    order_id = insert_order(
        customer_id=customer_id,
        restaurant_id=restaurant_id,
        order_details=order_details,
        total_amount=total_amount,
        order_time=order_time,
        delivery_address=delivery_address,
        delivery_person_id=None
    )
    print(order_id)
    session.pop('cart', None)
    return redirect(url_for('customer.order_waiting', order_id=order_id))

@customer_blueprint.route('/order_waiting/<int:order_id>')
def order_waiting(order_id):
    return render_template('order_waiting.html', order_id=order_id)

@customer_blueprint.route('/check_order_status/<int:order_id>')
def check_order_status(order_id):
    order_status = get_order_status(order_id)
    return {'status': order_status}

@customer_blueprint.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status_route(order_id):
    result = update_order_status(order_id)
    if result['success']:
        print(result)
        return redirect(url_for('customer.order_waiting', order_id=order_id))
    else:
        return {'success': False, 'error': result['error']}, 500

@customer_blueprint.route('/success')
def order_success():
    return render_template('/customer/order_success.html')

# @customer_blueprint.route('/clear_session')
# def clear_session():
#     session.clear()
#     flash("Session has been cleared!", "info")
#     return redirect(url_for('main.index'))
