import requests
import re
from datetime import datetime, timedelta

# Кэш для таблицы обновлений
UPDATE_TABLE_CACHE = None
UPDATE_TABLE_CACHE_TIME = None
CACHE_DURATION = timedelta(hours=1)

# Маппинг источников для каждого конфига
SOURCES_MAP = {
    1: "https://github.com/sakha1370/OpenRay",
    2: "https://github.com/sevcator/5ubscrpt10n",
    3: "https://github.com/yitong2333/proxy-minging",
    4: "https://github.com/acymz/AutoVPN",
    5: "https://github.com/miladtahanian/V2RayCFGDumper",
    6: "https://github.com/roosterkid/openproxylist",
    7: "https://github.com/Epodonios/v2ray-configs",
    8: "https://github.com/CidVpn/cid-vpn-config/",
    9: "https://github.com/mohamadfg-dev/telegram-v2ray-configs-collector",
    10: "https://github.com/mheidari98/.proxy",
    11: "https://github.com/youfoundamin/V2rayCollector",
    12: "https://github.com/mheidari98/.proxy",
    13: "https://github.com/MahsaNetConfigTopic/config",
    14: "https://github.com/LalatinaHub/Mineral",
    15: "https://github.com/miladtahanian/Config-Collector",
    16: "https://github.com/Pawdroid/Free-servers",
    17: "https://github.com/MhdiTaheri/V2rayCollector_Py",
    18: "https://github.com/Epodonios/v2ray-configs",
    19: "https://github.com/MhdiTaheri/V2rayCollector",
    20: "https://github.com/Argh94/Proxy-List",
    21: "https://github.com/shabane/kamaji",
    22: "https://github.com/wuqb2i4f/xray-config-toolkit",
    23: "https://github.com/Delta-Kronecker/Xray/",
    24: "https://github.com/STR97/STRUGOV",
    25: "https://github.com/V2RayRoot/V2RayConfig",
    26: [
        "https://github.com/EtoNeYaProject/etoneyaproject.github.io",
        "https://storage.yandexcloud.net/cid-vpn/whitelist.txt",
        "https://github.com/igareck/vpn-configs-for-russia",
        "https://bp.wl.free.nf/confs/wl.txt",
        "https://github.com/gbwltg/gbwl",
        "https://github.com/zieng2/wl"
    ]
}

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
        
        # Добавляем источники если есть
        if i in SOURCES_MAP:
            config['sources'] = SOURCES_MAP[i]
        
        # Добавляем информацию об обновлении если есть
        if i in update_info:
            config['last_update'] = update_info[i]
        
        configs.append(config)

    return configs
