from flask import Flask, render_template, send_from_directory, jsonify
from services import get_vpn_configs
import requests
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Кэш для ссылок на скачивание
CACHE_FILE = 'download_links_cache.json'
CACHE_DURATION = timedelta(hours=24)

# Fallback ссылки на случай, если GitHub API недоступен
FALLBACK_LINKS = {
    'v2rayng-apk': 'https://github.com/2dust/v2rayNG/releases/download/1.10.32/v2rayNG_1.10.32_universal.apk',
    'throne-win10': 'https://github.com/throneproj/Throne/releases/download/1.0.13/Throne-1.0.13-windows64.zip',
    'throne-win7': 'https://github.com/throneproj/Throne/releases/download/1.0.13/Throne-1.0.13-windowslegacy64.zip',
    'throne-linux': 'https://github.com/throneproj/Throne/releases/download/1.0.13/Throne-1.0.13-linux-amd64.zip',
}

def get_cached_links():
    """Получить кэшированные ссылки если они актуальны"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
                cache_time = datetime.fromisoformat(cache.get('timestamp', ''))
                if datetime.now() - cache_time < CACHE_DURATION:
                    return cache.get('links')
        except Exception as e:
            print(f"Ошибка при чтении кэша: {e}")
    return None

def save_links_cache(links):
    """Сохранить ссылки в кэш"""
    cache = {
        'timestamp': datetime.now().isoformat(),
        'links': links
    }
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Ошибка при сохранении кэша: {e}")

def fetch_download_links():
    """Получить актуальные ссылки с GitHub API"""
    links = {}
    
    try:
        # v2rayNG
        print("Получение v2rayNG...")
        response = requests.get('https://api.github.com/repos/2dust/v2rayNG/releases/latest', timeout=10)
        print(f"v2rayNG ответ: {response.status_code}")
        if response.status_code == 200:
            releases = response.json()
            apk = next((a for a in releases.get('assets', []) if 'universal.apk' in a['name']), None)
            if apk:
                links['v2rayng-apk'] = apk['browser_download_url']
                print(f"v2rayNG ссылка: {links['v2rayng-apk']}")
        else:
            print(f"Ошибка GitHub API для v2rayNG: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при получении v2rayNG: {e}")
    
    try:
        # Throne
        print("Получение Throne...")
        response = requests.get('https://api.github.com/repos/throneproj/Throne/releases/latest', timeout=10)
        print(f"Throne ответ: {response.status_code}")
        if response.status_code == 200:
            releases = response.json()
            throne_win10 = next((a for a in releases.get('assets', []) if 'windows64' in a['name'] and 'legacy' not in a['name']), None)
            throne_win7 = next((a for a in releases.get('assets', []) if 'windowslegacy64' in a['name']), None)
            throne_linux = next((a for a in releases.get('assets', []) if 'linux-amd64' in a['name']), None)
            
            if throne_win10:
                links['throne-win10'] = throne_win10['browser_download_url']
                print(f"Throne Win10 ссылка: {links['throne-win10']}")
            if throne_win7:
                links['throne-win7'] = throne_win7['browser_download_url']
                print(f"Throne Win7 ссылка: {links['throne-win7']}")
            if throne_linux:
                links['throne-linux'] = throne_linux['browser_download_url']
                print(f"Throne Linux ссылка: {links['throne-linux']}")
        else:
            print(f"Ошибка GitHub API для Throne: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при получении Throne: {e}")
    
    return links if links else None

@app.route('/')
def home():
    configs = get_vpn_configs()
    return render_template('index.html', configs=configs)

@app.route('/api/download-links')
def get_download_links():
    """API endpoint для получения ссылок на скачивание"""
    # Сначала проверяем кэш
    cached = get_cached_links()
    if cached:
        print("Возвращаем кэшированные ссылки")
        return jsonify(cached)
    
    # Если кэша нет или он устарел, получаем новые ссылки
    print("Получаем новые ссылки с GitHub")
    links = fetch_download_links()
    
    if links:
        save_links_cache(links)
        print(f"Возвращаем новые ссылки: {links}")
        return jsonify(links)
    
    # Fallback - возвращаем ссылки по умолчанию
    print("Возвращаем fallback ссылки")
    save_links_cache(FALLBACK_LINKS)
    return jsonify(FALLBACK_LINKS)

@app.route('/LICENSE')
def serve_license():
    return send_from_directory('static', 'LICENSE')

if __name__ == '__main__':
    app.run(debug=True, port=5000)