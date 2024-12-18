from flask import Blueprint, request, jsonify
from app.models import Restaurant, db

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route('/', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([{'id': r.id, 'name': r.name} for r in restaurants])

@restaurant_bp.route('/create', methods=['POST'])
def create_restaurant():
    data = request.json
    new_restaurant = Restaurant(
        user_id=data['user_id'],
        name=data['name'],
        address=data['address'],
        phone=data['phone']
    )
    db.session.add(new_restaurant)
    db.session.commit()
    return jsonify({'message': 'Restaurant created successfully'}), 201
