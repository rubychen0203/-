from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Product, db

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/')
def home():
    return render_template('home.html')

@main_blueprint.route('/products')
def products():
    products = Product.get_all()
    return render_template('products.html', products=products)

@main_blueprint.route('/add_product', methods=['POST'])
def add_product():
    name = request.form.get('name')
    price = float(request.form.get('price'))
    description = request.form.get('description')
    Product.add_product(name, price, description)
    return redirect(url_for('main.products'))
