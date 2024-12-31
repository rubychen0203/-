from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# 初始化 SQLAlchemy 和 Migrate 實例
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    # 創建 Flask 應用
    app = Flask(__name__, template_folder='views')
    app.config.from_object(Config)  # 從 config.py 載入配置

    # 初始化 db 和 migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # 延遲匯入以避免循環匯入問題
    with app.app_context():
        from app.controllers.routes import main_blueprint
        from app.controllers.auth_controller import auth_blueprint
        from app.controllers.cus_controller import customer_blueprint
        # 註冊 Blueprints
        app.register_blueprint(main_blueprint)
        app.register_blueprint(auth_blueprint, url_prefix='/auth')
        app.register_blueprint(customer_blueprint, url_prefix='/customer')

    return app

    return app
