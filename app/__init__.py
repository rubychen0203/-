
from flask import Flask,render_template,request,redirect,url_for

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


# 初始化 SQLAlchemy 和 Migrate 實例

db = SQLAlchemy()
migrate = Migrate()

def create_app():

    app = Flask(__name__, template_folder='views')
    app.config.from_object(Config)  # 載入配置

    # 初始化資料庫和遷移工具，並將 SQLAlchemy 綁定到 Flask 應用
    db.init_app(app)
    migrate.init_app(app, db)

    # 註冊 Blueprints
    from app.controllers.routes import main_blueprint
    from app.controllers.user import user_bp
    from app.controllers.restaurant import restaurant_bp
    from app.controllers.order import order_bp
    from app.controllers.auth_controller import auth_blueprint
    from app.controllers.delivery_person import delivery_bp
    from app.controllers.cus_controller import customer_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(restaurant_bp, url_prefix='/restaurant')
    app.register_blueprint(order_bp, url_prefix='/orders')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(delivery_bp, url_prefix='/delivery')
    app.register_blueprint(customer_blueprint, url_prefix='/customer')

    return app
