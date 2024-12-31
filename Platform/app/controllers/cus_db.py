from app.models import db,User, Restaurant, Menu, Order, Customer, DeliveryPerson
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects import mysql
# 獲取所有餐廳
def get_restaurants():
    try:
        restaurants = Restaurant.query.all()
        print(db.engine.url)
        return [{'id': r.id, 'name': r.name, 'address': r.address} for r in restaurants]
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return []

# 獲取特定菜單項目
def get_menu_item(item_id):
    try:
        item = Menu.query.get(item_id)
        if item:
            return {
                'id': item.id,
                'restaurant_id': item.restaurant_id,
                'item_name': item.item_name,
                'price': float(item.price),
                'description': item.description,
                'available': item.available
            }
        return None
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return None

# 獲取指定餐廳的所有菜單
def get_menus_by_restaurant(restaurant_id):
    try:
        # 創建查詢對象
        query = Menu.query.filter(Menu.restaurant_id == restaurant_id, Menu.available > 0)

        # 打印生成的 SQL（包含參數值）
        compiled_query = query.statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True})
        print(f"Compiled SQL: {compiled_query}")

        # 執行查詢
        menus = query.all()
        print(db.engine.url)
        print(f"Fetched menus: {menus}")

        return [{'id': m.id, 'item_name': m.item_name, 'price': float(m.price), 'description': m.description} for m in menus]
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return []


# 獲取訂單狀態
def get_order_status(order_id):
    try:
        order = Order.query.get(order_id)
        if order:
            return {'order_status': str(order.order_status), 'payment_status': str(order.payment_status)}
        return {'order_status': 'Unknown', 'payment_status': 'Unknown'}
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return {'order_status': 'Unknown', 'payment_status': 'Unknown'}
    
def get_customer_id_by_user_id(user_id):
    customer = Customer.query.filter_by(user_id=user_id).first()
    print(db.engine.url)
    if customer:
        return customer.id
    else:
        return None

# 插入訂單
def insert_order(customer_id, restaurant_id, order_details, total_amount,order_time, delivery_address, delivery_person_id=None):
    try:
        order = Order(
            customer_id=customer_id,
            restaurant_id=restaurant_id,
            order_details=order_details,
            total_amount=total_amount,
            order_time=order_time,
            delivery_address=delivery_address,
            order_status='PREPARING',
            payment_status='PENDING',
            delivery_person_id=delivery_person_id
        )
        db.session.add(order)
        db.session.commit()
        print("INSERT")
        return order.id
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return None

# 獲取所有菜單項目
def get_menus():
    try:
        menus = Menu.query.filter_by(available=True).all()
        return [{'id': m.id, 'item_name': m.item_name, 'price': float(m.price), 'description': m.description} for m in menus]
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return []

# 更新訂單狀態
def update_order_status(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return {'success': False, 'error': 'Order not found'}
        order.order_status = 'DELIVERED'
        db.session.commit()
        return {'success': True, 'order_id': order_id}
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return {'success': False, 'error': str(e)}
