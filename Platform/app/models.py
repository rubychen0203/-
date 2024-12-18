from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy import Enum
from flask_migrate import Migrate
from decimal import Decimal
from datetime import datetime
import os

app = Flask(__name__)

# 資料庫配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define User Model
class UserRoleEnum(Enum):
    ADMIN = "Admin"
    RESTAURANT = "Restaurant"
    CUSTOMER = "Customer"
    DELIVERY_PERSON = "Delivery_Person"
    
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
    
# Define Restaurant Model
class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(25), unique=True, nullable=False)
    account_balance = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    
# Define Menu Model
class Menu(db.Model):
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    item_name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    description = db.Column(db.Text)
    available = db.Column(db.Boolean, nullable=False)
    
    restaurant = db.relationship('Restaurant', backref='menus')
    
# Define Customers Model
class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(25), unique=True, nullable=False)    
    address = db.Column(db.Text, nullable=False)
    
# Define Delivery Persons Model
class DeliveryPerson(db.Model):
    __tablename__ = 'delivery_persons'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(25), unique=True, nullable=False)    
    current_order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True)
    earnings = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    
# Define Order Model
class PaymentStatusEnum(Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    REFUNDED = "Refunded"
    FAILED = "Failed"
    
class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    delivery_person_id = db.Column(db.Integer, db.ForeignKey('delivery_persons.id'), nullable=False)
    order_status = db.Column(db.String(10), nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    order_time = db.Column(db.DateTime, default=func.now(), nullable=False)
    delivery_time = db.Column(db.DateTime, default=func.now())
    delivery_address = db.Column(db.Text, nullable=False)
    payment_status = db.Column(db.Enum(PaymentStatusEnum), nullable=False, default=PaymentStatusEnum.PENDING)
    
    restaurant = db.relationship('Restaurant', backref='orders')
    
# Define Review Model
class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    delivery_person_id = db.Column(db.Integer, db.ForeignKey('delivery_persons.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=0)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)

# Define Settlement Model
class Settlement(db.Model):
    __tablename__ = 'settlements'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, unique=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False, unique=True)
    delivery_person_id = db.Column(db.Integer, db.ForeignKey('delivery_persons.id'), nullable=False, unique=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    transaction_date = db.Column(db.DateTime, default=func.now(), nullable=False)