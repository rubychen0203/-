from app import db
from sqlalchemy import Enum as SQLEnum  # 已匯入的
from sqlalchemy.sql import func
from enum import Enum
from datetime import datetime

# User Roles Enum
class UserRoleEnum(Enum):
    ADMIN = "ADMIN"
    RESTAURANT = "RESTAURANT"
    CUSTOMER = "CUSTOMER"
    DELIVERY_PERSON = "DELIVERY_PERSON"
    
    def __str__(self):
        return self.value  # 返回枚舉的字串值

# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(25), unique=True, nullable=False)
    role = db.Column(db.Enum(UserRoleEnum), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f'User {self.username}'

# Restaurant Model
class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(25), unique=True, nullable=False)
    account_balance = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)

# Menu Model
class Menu(db.Model):
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    item_name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    description = db.Column(db.Text)
    available = db.Column(db.Boolean, nullable=False)
    
    restaurant = db.relationship('Restaurant', backref='menus')

# Customer Model
class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(25), unique=True, nullable=False)    

# DeliveryPerson Model
class DeliveryPerson(db.Model):
    __tablename__ = 'delivery_persons'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(25), unique=True, nullable=False)    
    current_order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True)
    earnings = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    
    current_order = db.relationship('Order', backref='assigned_delivery_person', foreign_keys=[current_order_id])

# Order Model
class PaymentStatusEnum(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    REFUNDED = "REFUNDED"
    FAILED = "FAILED"

    def __str__(self):
        return self.value  # 返回枚舉的字串值

class OrderStatusEnum(Enum):
    PREPARING = "PREPARING"            # 商家正在準備中
    READY_FOR_PICKUP = "READY_FOR_PICKUP"  # 訂單已準備好，可供取餐或配送
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"  # 訂單正在配送中
    DELIVERED = "DELIVERED"            # 訂單已送達
    GET="GET"#確認取餐
    
    def __str__(self):
        return self.value  # 返回枚舉的字串值    
    
class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    delivery_person_id = db.Column(db.Integer, db.ForeignKey('delivery_persons.id'))
    order_details = db.Column(db.Text, nullable=False)
    order_status = db.Column(db.Enum(OrderStatusEnum), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    order_time = db.Column(db.DateTime, default=func.now(), nullable=False)
    delivery_time = db.Column(db.DateTime)
    delivery_address = db.Column(db.Text, nullable=False)
    payment_status = db.Column(db.Enum(PaymentStatusEnum), nullable=False, default=PaymentStatusEnum.PENDING)

    restaurant = db.relationship('Restaurant', backref=db.backref('orders', lazy=True))
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))
    delivery_person = db.relationship('DeliveryPerson', backref=db.backref('orders', lazy=True), foreign_keys=[delivery_person_id])

# Review Model
class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    delivery_person_id = db.Column(db.Integer, db.ForeignKey('delivery_persons.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=0)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    
    restaurant = db.relationship('Restaurant', backref=db.backref('reviews', lazy=True))
    customer = db.relationship('Customer', backref=db.backref('reviews', lazy=True))
    delivery_person = db.relationship('DeliveryPerson', backref=db.backref('reviews', lazy=True))

# Settlement Model
class Settlement(db.Model):
    __tablename__ = 'settlements'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    delivery_person_id = db.Column(db.Integer, db.ForeignKey('delivery_persons.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    transaction_date = db.Column(db.DateTime, default=func.now(), nullable=False)
