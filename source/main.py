import os
import argparse
import logging
from waitress import serve

from app import create_app
from app.config import set_debug_mode
from app.services.github import download_badges

if __name__ == '__main__':
    # Настройка логгера
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='Goida VPN Site')
    parser.add_argument('--debug', action='store_true', help='Режим отладки с автоперезагрузкой')
    parser.add_argument('--host', default='127.0.0.1', help='Хост для прослушивания')
    parser.add_argument('--port', type=int, default=5000, help='Порт для прослушивания')
    args = parser.parse_args()

    # Синхронизируем режим отладки в модуле конфигурации
    set_debug_mode(args.debug)

    # Создаем Flask приложение через фабрику
    app = create_app()
    app.config['DEBUG'] = args.debug

    # Проверка: выполняется ли код в дочернем процессе релоадера Flask
    is_reloader_child = os.environ.get('WERKZEUG_RUN_MAIN') in ('true', '1')

    # Инициализация (загрузка бейджей) только в родительском процессе
    if not is_reloader_child:
        download_badges()
        if args.debug:
            log.info("[DEBUG] Запуск в режиме ОТЛАДКИ (auto-reload & debugger включены)")
            log.info(f"[URL] Сайт доступен на http://{args.host}:{args.port}")

    host = args.host
    port = args.port

    if args.debug:
        app.run(host=host, port=port, debug=True, use_reloader=True)
    else:
        if not is_reloader_child:
            log.info(f"[START] Запуск в ПРОДАКШЕН режиме (Waitress)")
            log.info(f"[URL] Сайт доступен на http://{host}:{port}")
        serve(app, host=host, port=port)
