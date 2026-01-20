import requests
import re
from datetime import datetime, timedelta

# Кэш для таблицы обновлений
UPDATE_TABLE_CACHE = None
UPDATE_TABLE_CACHE_TIME = None
CACHE_DURATION = timedelta(hours=1)

def parse_update_table():
    """Парсит таблицу обновлений из README.md репозитория"""
    global UPDATE_TABLE_CACHE, UPDATE_TABLE_CACHE_TIME
    
    # Проверяем кэш
    if UPDATE_TABLE_CACHE and UPDATE_TABLE_CACHE_TIME:
        if datetime.now() - UPDATE_TABLE_CACHE_TIME < CACHE_DURATION:
            return UPDATE_TABLE_CACHE
    
    try:
        # Получаем README
        response = requests.get(
            'https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/refs/heads/main/README.md',
            timeout=10
        )
        if response.status_code != 200:
            return {}
        
        readme_content = response.text
        
        # Парсим таблицу
        # Ищем строки таблицы вида: | число | [...] | HH:MM | DD.MM.YYYY |
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
        
        # Кэшируем результат
        UPDATE_TABLE_CACHE = update_info
        UPDATE_TABLE_CACHE_TIME = datetime.now()
        
        return update_info
    except Exception as e:
        print(f"Ошибка при парсинге таблицы обновлений: {e}")
        return {}

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
        
        # Добавляем информацию об обновлении если есть
        if i in update_info:
            config['last_update'] = update_info[i]
        
        configs.append(config)

    return configs