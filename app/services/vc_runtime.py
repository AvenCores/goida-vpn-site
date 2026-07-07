import os
import re
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from app.config import VC_RUNTIME_CACHE_FILE, VC_RUNTIME_CACHE_DURATION, VC_RUNTIME_FALLBACK
import app.config as config_module

def get_cached_vc_runtime_link():
    """Получить кэшированную ссылку на Visual C++ Runtimes если она актуальна"""
    if config_module.DEBUG_MODE:
        return None
    
    if os.path.exists(VC_RUNTIME_CACHE_FILE):
        try:
            with open(VC_RUNTIME_CACHE_FILE, 'r') as f:
                cache = json.load(f)
                cache_time = datetime.fromisoformat(cache.get('timestamp', ''))
                if datetime.now() - cache_time < VC_RUNTIME_CACHE_DURATION:
                    return cache.get('link')
        except Exception as e:
            print(f"Ошибка при чтении кэша VC Runtime: {e}")
    return None

def save_vc_runtime_link_cache(link):
    """Сохранить ссылку на Visual C++ Runtimes в кэш"""
    if config_module.DEBUG_MODE:
        return
    
    cache = {
        'timestamp': datetime.now().isoformat(),
        'link': link
    }
    try:
        with open(VC_RUNTIME_CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Ошибка при сохранении кэша VC Runtime: {e}")

def fetch_vc_runtime_link():
    """Получить актуальную ссылку на Visual C++ Runtimes с comss.ru"""
    if config_module.DEBUG_MODE:
        print("[DEBUG] DEBUG MODE: Используем заглушку для VC Runtime ссылки")
        return VC_RUNTIME_FALLBACK
    
    url = 'https://www.comss.ru/download/page.php?id=6271'
    
    try:
        print(f"Получение ссылки на Visual C++ Runtimes с {url}...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем кнопку "скачать как" и связанные элементы
        download_link = None
        
        # Ищем все ссылки, содержащие dl.comss.org
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'dl.comss.org' in href and 'Visual-C-Runtimes' in href:
                download_link = href
                break
        
        # Если не нашли, ищем в data-атрибутах кнопок
        if not download_link:
            for btn in soup.find_all('button', {'data-toggle': 'dropdown'}):
                if 'скачать как' in btn.get_text().lower():
                    parent = btn.find_parent()
                    if parent:
                        dropdown_menu = parent.find('div', class_='dropdown-menu') or parent.find('ul', class_='dropdown-menu')
                        if dropdown_menu:
                            for link in dropdown_menu.find_all('a', href=True):
                                href = link.get('href', '')
                                if 'dl.comss.org' in href and 'Visual-C-Runtimes' in href:
                                    download_link = href
                                    break
                                data_url = link.get('data-url') or link.get('data-href')
                                if data_url and 'dl.comss.org' in data_url and 'Visual-C-Runtimes' in data_url:
                                    download_link = data_url
                                    break
                        if download_link:
                            break
        
        # Если всё ещё не нашли, пробуем найти в JavaScript коде страницы
        if not download_link:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    matches = re.findall(r'https://dl\.comss\.org/download/Visual-C-Runtimes[^\s\'"]+', script.string)
                    if matches:
                        download_link = matches[0]
                        break
        
        if download_link:
            print(f"Найдена ссылка на Visual C++ Runtimes: {download_link}")
            return download_link
        else:
            print("Не удалось найти ссылку на Visual C++ Runtimes, используем fallback")
            return VC_RUNTIME_FALLBACK
            
    except Exception as e:
        print(f"Ошибка при получении Visual C++ Runtimes: {e}")
        return VC_RUNTIME_FALLBACK
