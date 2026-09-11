import logging
import requests
import re
import threading
from datetime import datetime
from app.config import SOURCES_MAP, VPN_CACHE_DURATION
import app.config as config_module

log = logging.getLogger(__name__)

# Кэш для таблицы обновлений
UPDATE_TABLE_CACHE = None
UPDATE_TABLE_CACHE_TIME = None

# Блокировка и флаг для неблокирующего фонового обновления
UPDATE_LOCK = threading.Lock()
IS_UPDATING = False

UPDATE_TABLE_URL = 'https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/refs/heads/main/README.md'

def _parse_readme_table(readme_content):
    """Парсит таблицу обновлений из текста README.md репозитория"""
    table_pattern = r'\|\s*(\d+)\s*\|[^|]*\|[^|]*\|\s*(\d{2}:\d{2})(?:\s*\([^)]*\))?\s*\|\s*(\d{2}\.\d{2}\.\d{4})\s*\|'
    matches = re.findall(table_pattern, readme_content)

    update_info = {}
    for match in matches:
        config_id = int(match[0])
        time_str = match[1]  # HH:MM
        date_str = match[2]  # DD.MM.YYYY

        update_info[config_id] = {
            'time': time_str,
            'date': date_str,
            'datetime_str': f"{date_str} {time_str}"
        }
    return update_info


def fetch_update_table_sync(timeout=15):
    """Синхронно скачивает и парсит таблицу обновлений.

    Используется при статическом билде (build.py), где нельзя полагаться
    на фоновый поток: рендер идёт сразу и иначе даты не попадут в HTML.
    При успехе обновляет общий кэш. Возвращает dict (может быть пустым).
    """
    global UPDATE_TABLE_CACHE, UPDATE_TABLE_CACHE_TIME
    last_error = None
    for attempt in range(2):
        try:
            response = requests.get(UPDATE_TABLE_URL, timeout=timeout)
            if response.status_code == 200:
                update_info = _parse_readme_table(response.text)
                if update_info:
                    with UPDATE_LOCK:
                        UPDATE_TABLE_CACHE = update_info
                        UPDATE_TABLE_CACHE_TIME = datetime.now()
                    return update_info
                log.warning("Таблица обновлений пуста после парсинга README.md")
                break
            last_error = f"README.md вернул статус {response.status_code}"
        except Exception as e:
            last_error = e
    log.warning(f"Ошибка при синхронной загрузке таблицы обновлений: {last_error}")
    return UPDATE_TABLE_CACHE or {}

def _fetch_and_parse_update_table():
    global UPDATE_TABLE_CACHE, UPDATE_TABLE_CACHE_TIME, IS_UPDATING
    try:
        response = requests.get(
            UPDATE_TABLE_URL,
            timeout=10
        )
        if response.status_code == 200:
            update_info = _parse_readme_table(response.text)

            UPDATE_TABLE_CACHE = update_info
            UPDATE_TABLE_CACHE_TIME = datetime.now()
    except Exception as e:
        log.warning(f"Ошибка при фоновом парсинге таблицы обновлений: {e}")
    finally:
        with UPDATE_LOCK:
            IS_UPDATING = False

def parse_update_table(force_sync=False):
    """Парсит таблицу обновлений из README.md репозитория"""
    global UPDATE_TABLE_CACHE, UPDATE_TABLE_CACHE_TIME, IS_UPDATING

    # В режиме отладки используем заглушку
    if config_module.DEBUG_MODE:
        log.debug("[DEBUG] DEBUG MODE: Используем заглушку для таблицы обновлений")
        fallback_update_info = {}
        now = datetime.now()
        for i in range(1, 27):
            fallback_update_info[i] = {
                'time': now.strftime('%H:%M'),
                'date': now.strftime('%d.%m.%Y'),
                'datetime_str': now.strftime('%d.%m.%Y %H:%M')
            }
        return fallback_update_info

    # Проверяем кэш
    if UPDATE_TABLE_CACHE and UPDATE_TABLE_CACHE_TIME:
        # Если кэш ещё свежий, отдаем сразу
        if datetime.now() - UPDATE_TABLE_CACHE_TIME < VPN_CACHE_DURATION:
            return UPDATE_TABLE_CACHE

        # Синхронный режим (статический билд): не отдаём протухший кэш,
        # а ждём свежие данные — иначе даты не попадут в собранный HTML.
        if force_sync:
            return fetch_update_table_sync()

        # Если кэш устарел, но фоновое обновление уже запущено
        with UPDATE_LOCK:
            if IS_UPDATING:
                return UPDATE_TABLE_CACHE
            
            # Запускаем фоновое обновление и сразу отдаем старый кэш
            IS_UPDATING = True
            threading.Thread(target=_fetch_and_parse_update_table, daemon=True).start()
            return UPDATE_TABLE_CACHE
            
    # Если кэша нет вообще (первый запуск), запускаем фоновое обновление асинхронно,
    # чтобы не блокировать запуск сервера или первый HTTP-запрос.
    # В синхронном режиме (статический билд) ждём данные сразу.
    if force_sync:
        return fetch_update_table_sync()

    with UPDATE_LOCK:
        if not IS_UPDATING:
            IS_UPDATING = True
            threading.Thread(target=_fetch_and_parse_update_table, daemon=True).start()
    return UPDATE_TABLE_CACHE or {}

def get_vpn_configs(wait_for_updates=False):
    base_url = "https://github.com/AvenCores/goida-vpn-configs/raw/refs/heads/main/githubmirror/"

    # Получаем информацию об обновлениях
    update_info = parse_update_table(force_sync=wait_for_updates)
    
    configs = []
    # Рекомендованные согласно README: 1, 6, 22, 23, 24, 25
    recommended_ids = [1, 6, 22, 23, 24, 25]
    
    for i in range(1, 27):
        config = {
            "id": i,
            "name": f"Config {i}.txt",
            "url": f"{base_url}{i}.txt",
            "is_recommended": i in recommended_ids,
            "is_sni": i == 26, # Обход SNI/CIDR
            "qr_link": f"https://github.com/AvenCores/goida-vpn-configs/blob/main/qr-codes/{i}.png"
        }
        
        # Добавляем источники если есть
        if i in SOURCES_MAP:
            config['sources'] = SOURCES_MAP[i]
        
        # Добавляем информацию об обновлении если есть
        if i in update_info:
            config['last_update'] = update_info[i]
        
        configs.append(config)

    return configs
