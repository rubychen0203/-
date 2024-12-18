from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# 初始化 SQLAlchemy 和 Migrate
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化資料庫
    db.init_app(app)
    migrate.init_app(app, db)

    # 註冊 Blueprints
    from app.controllers.user import user_bp
    from app.controllers.restaurant import restaurant_bp
    from app.controllers.order import order_bp

    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(restaurant_bp, url_prefix='/restaurants')
    app.register_blueprint(order_bp, url_prefix='/orders')

    return app
