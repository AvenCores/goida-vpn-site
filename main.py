from flask import Flask, render_template, send_from_directory, jsonify, request, Response
from services import get_vpn_configs
import requests
import json
from datetime import datetime, timedelta
from urllib.parse import urljoin
import os

app = Flask(__name__)

# SEO defaults (can be overridden via env in production)
DEFAULT_META_TITLE = "Goida VPN Configs - Автоматические VPN-конфиги"
DEFAULT_META_DESCRIPTION = (
    "Автоматические VPN-конфиги для V2Ray, VLESS, Hysteria, Trojan, VMess, Reality и Shadowsocks. "
    "Обновление каждые 9 минут, удобные ссылки и QR-коды."
)
DEFAULT_META_KEYWORDS = "vpn, vless, v2ray, shadowsocks, hysteria, trojan, vmess, reality, vpn configs, free vpn, goida vpn, обход блокировок"

def normalize_site_url(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    if not value.endswith('/'):
        value += '/'
    return value

def get_site_url() -> str | None:
    site_url = normalize_site_url(os.environ.get('SITE_URL'))
    if site_url:
        return site_url
    try:
        return normalize_site_url(request.url_root)
    except RuntimeError:
        return None

def generate_robots_txt(site_url: str | None) -> str:
    lines = [
        "User-agent: *",
        "Allow: /",
    ]
    if site_url:
        lines.append(f"Sitemap: {urljoin(site_url, 'sitemap.xml')}")
    return "\n".join(lines) + "\n"

def generate_sitemap_xml(site_url: str | None, lastmod: str | None = None) -> str:
    if not lastmod:
        lastmod = datetime.utcnow().date().isoformat()
    loc = urljoin(site_url or "/", "")
    if not loc.endswith('/'):
        loc += '/'
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        "    <changefreq>hourly</changefreq>\n"
        "    <priority>1.0</priority>\n"
        "  </url>\n"
        "</urlset>\n"
    )

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
    analytics_ids = {
        'ga_id': os.environ.get('GA_ID'),
        'ym_id': os.environ.get('YM_ID')
    }
    site_url = get_site_url()
    meta_title = os.environ.get('META_TITLE', DEFAULT_META_TITLE)
    meta_description = os.environ.get('META_DESCRIPTION', DEFAULT_META_DESCRIPTION)
    meta_keywords = os.environ.get('META_KEYWORDS', DEFAULT_META_KEYWORDS)
    og_image = os.environ.get('OG_IMAGE_URL')
    return render_template(
        'index.html',
        configs=configs,
        analytics_ids=analytics_ids,
        site_url=site_url,
        canonical_url=site_url,
        meta_title=meta_title,
        meta_description=meta_description,
        meta_keywords=meta_keywords,
        og_image=og_image
    )

@app.route('/robots.txt')
def robots_txt():
    site_url = get_site_url()
    content = generate_robots_txt(site_url)
    return Response(content, mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap_xml():
    site_url = get_site_url()
    content = generate_sitemap_xml(site_url)
    return Response(content, mimetype='application/xml')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'favicon.png', mimetype='image/png')

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

# Кэш для статистики GitHub
STATS_CACHE_FILE = 'github_stats_cache.json'
STATS_CACHE_DURATION = timedelta(hours=1)

BADGES = {
    'python.svg': 'https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54',
    'license.svg': 'https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge',
    'stars.svg': 'https://img.shields.io/github/stars/AvenCores/goida-vpn-configs?style=for-the-badge',
    'forks.svg': 'https://img.shields.io/github/forks/AvenCores/goida-vpn-configs?style=for-the-badge',
    'prs.svg': 'https://img.shields.io/github/issues-pr/AvenCores/goida-vpn-configs?style=for-the-badge',
    'issues.svg': 'https://img.shields.io/github/issues/AvenCores/goida-vpn-configs?style=for-the-badge'
}

def download_badges():
    """Скачивает бэджи локально для кэширования"""
    badges_dir = os.path.join('static', 'images', 'badges')
    if not os.path.exists(badges_dir):
        os.makedirs(badges_dir)
    
    print("Загрузка бэджей...")
    for filename, url in BADGES.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(os.path.join(badges_dir, filename), 'wb') as f:
                    f.write(response.content)
                print(f"✅ Бэдж {filename} обновлен")
            else:
                print(f"⚠️ Не удалось загрузить бэдж {filename}: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка при загрузке бэджа {filename}: {e}")

def get_cached_stats():
    """Получить кэшированную статистику, если она актуальна"""
    if os.path.exists(STATS_CACHE_FILE):
        try:
            with open(STATS_CACHE_FILE, 'r') as f:
                cache = json.load(f)
                cache_time = datetime.fromisoformat(cache.get('timestamp', ''))
                if datetime.now() - cache_time < STATS_CACHE_DURATION:
                    return cache.get('data')
        except Exception as e:
            print(f"Ошибка при чтении кэша статистики: {e}")
    return None

def save_stats_cache(data):
    """Сохранить статистику в кэш"""
    cache = {
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    try:
        with open(STATS_CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Ошибка при сохранении кэша статистики: {e}")

@app.route('/api/github-stats')
def get_github_stats():
    """API endpoint для получения статистики репозитория с кэшированием"""
    # Сначала проверяем кэш
    cached_stats = get_cached_stats()
    if cached_stats:
        print("Возвращаем кэшированную статистику GitHub")
        return jsonify(cached_stats)

    # Если кэша нет, делаем запрос
    print("Получаем новую статистику с GitHub")
    repo = 'AvenCores/goida-vpn-configs'
    try:
        response = requests.get(f'https://api.github.com/repos/{repo}', timeout=10)
        response.raise_for_status()
        data = response.json()
        save_stats_cache(data) # Сохраняем в кэш
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении статистики с GitHub: {e}")
        return jsonify(error=str(e)), getattr(e.response, 'status_code', 500)

@app.route('/LICENSE')
def serve_license():
    return send_from_directory('static', 'LICENSE')

if __name__ == '__main__':
    # Импортируем промышленный сервер
    from waitress import serve
    
    # Скачиваем бэджи при запуске
    download_badges()
    
    print("Запуск локального сайта на http://127.0.0.1:5000")
    # Запускаем приложение через waitress
    serve(app, host='127.0.0.1', port=5000)
