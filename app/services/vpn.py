import requests
import re
import threading
from datetime import datetime
from app.config import SOURCES_MAP, VPN_CACHE_DURATION
import app.config as config_module

# Кэш для таблицы обновлений
UPDATE_TABLE_CACHE = None
UPDATE_TABLE_CACHE_TIME = None

# Блокировка и флаг для неблокирующего фонового обновления
UPDATE_LOCK = threading.Lock()
IS_UPDATING = False

def _fetch_and_parse_update_table():
    global UPDATE_TABLE_CACHE, UPDATE_TABLE_CACHE_TIME, IS_UPDATING
    try:
        response = requests.get(
            'https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/refs/heads/main/README.md',
            timeout=10
        )
        if response.status_code == 200:
            readme_content = response.text
            
            # Парсим таблицу
            table_pattern = r'\|\s*(\d+)\s*\|[^|]*\|[^|]*\|\s*(\d{2}:\d{2})\s*\|\s*(\d{2}\.\d{2}\.\d{4})\s*\|'
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
            
            UPDATE_TABLE_CACHE = update_info
            UPDATE_TABLE_CACHE_TIME = datetime.now()
    except Exception as e:
        print(f"Ошибка при фоновом парсинге таблицы обновлений: {e}")
    finally:
        with UPDATE_LOCK:
            IS_UPDATING = False

def parse_update_table():
    """Парсит таблицу обновлений из README.md репозитория"""
    global UPDATE_TABLE_CACHE, UPDATE_TABLE_CACHE_TIME, IS_UPDATING

    # В режиме отладки используем заглушку
    if config_module.DEBUG_MODE:
        print("[DEBUG] DEBUG MODE: Используем заглушку для таблицы обновлений")
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
        
        # Если кэш устарел, но фоновое обновление уже запущено
        with UPDATE_LOCK:
            if IS_UPDATING:
                return UPDATE_TABLE_CACHE
            
            # Запускаем фоновое обновление и сразу отдаем старый кэш
            IS_UPDATING = True
            threading.Thread(target=_fetch_and_parse_update_table, daemon=True).start()
            return UPDATE_TABLE_CACHE
            
    # Если кэша нет вообще (первый запуск), делаем запрос синхронно, чтобы страница не была пустой
    with UPDATE_LOCK:
        IS_UPDATING = True
    _fetch_and_parse_update_table()
    return UPDATE_TABLE_CACHE or {}

def get_vpn_configs():
    base_url = "https://github.com/AvenCores/goida-vpn-configs/raw/refs/heads/main/githubmirror/"
    
    # Получаем информацию об обновлениях
    update_info = parse_update_table()
    
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
