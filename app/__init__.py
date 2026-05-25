import os
import logging
from flask import Flask, send_from_directory
import app.config as config_module

def create_app(config_module=config_module):
    """Фабрика приложений для создания инстанса Flask"""
    app = Flask(__name__)
    
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
    
    # Маршрут-фоллбек для tailwind.css при локальном запуске без сборки
    @app.route('/static/css/tailwind.css')
    def serve_tailwind():
        static_css_dir = os.path.join(app.root_path, 'static', 'css')
        tailwind_css_path = os.path.join(static_css_dir, 'tailwind.css')
        if os.path.exists(tailwind_css_path):
            return send_from_directory(static_css_dir, 'tailwind.css')
        else:
            return send_from_directory(static_css_dir, 'tailwind.input.css')
            
    return app
