import os
import logging
from flask import Flask
import app.config as config_module

def create_app(config_module=config_module):
    """Фабрика приложений для создания инстанса Flask"""
    # templates и static находятся в корне проекта, поэтому переопределяем пути относительно папки app/
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), '..', 'static')
    )
    
    # Загружаем настройки из модуля config
    app.config.from_object(config_module)
    
    # Настройка логирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    
    # Импортируем и регистрируем синие страницы (Blueprints)
    from app.routes.views import views_bp
    from app.routes.api import api_bp
    from app.routes.seo import seo_bp
    
    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp) # префикс /api уже настроен внутри Blueprint
    app.register_blueprint(seo_bp)
    
    return app
